#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eclaircit et assainit les photos du site.

    python3 outils/retouche.py              # essai dans images/retouchees/
    python3 outils/retouche.py --appliquer   # remplace les originaux

Les photos sortaient de l'appareil avec le defaut classique des prises de
vue d'interieur : une dominante jaune-orange due aux lampes (jusqu'a +24 %
de rouge contre -23 % de bleu dans le sejour), des noirs ecrases et une
exposition un peu basse. A l'ecran, cela donne des pieces ternes et datees,
alors qu'elles sont claires en vrai.

Quatre corrections, dans cet ordre :

  1. Balance des blancs, estimee sur les zones claires de l'image (murs et
     plafonds blancs) croisee avec la moyenne generale. La correction est
     volontairement partielle : neutraliser completement rendrait le bois
     gris et tuerait la chaleur de la piece, qui est un argument de vente.
  2. Points noir et blanc, sans jamais ecreter plus que l'original — les
     baies vitrees sont deja a la limite sur plusieurs photos.
  3. Exposition par gamma, pour amener la luminance moyenne a la cible,
     plafonnee pour ne pas delaver.
  4. Microcontraste et saturation, legers, pour reveiller l'ensemble.

Une photo deja traitee est notee dans images/retouche.json et ne l'est pas
deux fois : repasser la correction en boucle finirait par tout delaver.
Les originaux restent de toute facon dans l'historique git.

Prerequis :  pip3 install pillow
"""

import json
import os
import shutil
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageStat

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(RACINE, "images")
ESSAI = os.path.join(IMAGES, "retouchees")
JOURNAL = os.path.join(IMAGES, "retouche.json")

# Fabriquees par un script, deja a leur point : rien a corriger.
IGNOREES = ("carte-accueil", "plaque-porte", "teaser-affiche", "visite-affiche")

CIBLE_LUMINANCE = 141.0   # moyenne visee, sur 255
GAMMA_MAX = 1.30          # au-dela, l'image se delave
BLANCS_MAX = 0.52         # part de la correction de teinte appliquee
GAIN_MINI, GAIN_MAXI = 0.93, 1.07

# Une photo de plein air se traite autrement : le ciel y est bleu pour de
# bonnes raisons, et le « corriger » vers le neutre delave la montagne au
# lieu de l'eclaircir. On y touche a peine a la teinte, on pousse moins
# l'exposition, et on rend le punch par la saturation.
CIEL_PART = 0.18          # part de ciel qui fait basculer en « plein air »
DEHORS = {"blancs": 0.15, "gamma_max": 1.22, "saturation": 1.14}
PLANCHER_NOIR = 3         # on ne laisse pas les noirs totalement bouches
SATURATION = 1.09
NETTETE = dict(radius=1.8, percent=55, threshold=3)


def percentile(histogramme, part):
    total = sum(histogramme)
    cumul = 0
    for valeur, compte in enumerate(histogramme):
        cumul += compte
        if cumul >= total * part:
            return valeur
    return 255


def part_de_ciel(im):
    """Fraction de l'image occupee par du ciel : bleu dominant et clair,
    dans la moitie haute du cadre."""
    petite = im.copy()
    petite.thumbnail((200, 200))
    haut = petite.crop((0, 0, petite.width, petite.height // 2))
    pixels = haut.load()
    ciel = 0
    for y in range(haut.height):
        for x in range(haut.width):
            r, v, b = pixels[x, y][:3]
            if b > 110 and b > r + 14 and b >= v:
                ciel += 1
    return ciel / float(haut.width * haut.height * 2)


def gains_de_teinte(im, force):
    """Facteurs R, V, B qui ramenent l'image vers le neutre.

    Deux estimateurs, moyennes geometriquement : la moyenne generale
    (« monde gris ») et la moyenne des zones claires non brulees, qui dans
    un interieur sont les murs et les plafonds, donc blancs en realite."""
    petite = im.copy()
    petite.thumbnail((400, 400))
    moyennes = ImageStat.Stat(petite).mean[:3]

    gris = petite.convert("L")
    seuil = percentile(gris.histogram(), 0.85)
    clairs = [[], [], []]
    pixels, luminances = petite.load(), gris.load()
    for y in range(petite.height):
        for x in range(petite.width):
            if seuil <= luminances[x, y] <= 248:
                r, v, b = pixels[x, y][:3]
                clairs[0].append(r); clairs[1].append(v); clairs[2].append(b)

    gains = []
    for canal in range(3):
        general = sum(moyennes) / 3 / max(1.0, moyennes[canal])
        if clairs[canal]:
            moyenne_claire = sum(clairs[canal]) / len(clairs[canal])
            toutes = sum(sum(c) / len(c) for c in clairs) / 3
            local = toutes / max(1.0, moyenne_claire)
        else:
            local = general
        brut = (general * local) ** 0.5
        amorti = 1.0 + (brut - 1.0) * force
        gains.append(min(GAIN_MAXI, max(GAIN_MINI, amorti)))
    return gains


def courbe(noir, blanc, gamma):
    """Table de conversion : points noir et blanc, puis gamma.

    Le gamma est relache dans les hautes lumieres : sans cela, il eclaircit
    aussi le ciel et la vue par la baie vitree, qui perdent leur matiere —
    c'est exactement ce qui rend une photo « delavee » plutot que claire."""
    table = []
    for valeur in range(256):
        x = (valeur - noir) / max(1, blanc - noir)
        x = min(1.0, max(0.0, x))
        y = x ** (1.0 / gamma)
        epaule = x ** 2.2                      # 0 dans les ombres, 1 au blanc
        y = y * (1 - epaule) + x * epaule
        table.append(int(round(PLANCHER_NOIR + y * (255 - PLANCHER_NOIR))))
    return table


def retoucher(chemin):
    """Rend l'image corrigee et le detail de ce qui a ete fait."""
    with Image.open(chemin) as source:
        im = source.convert("RGB")

        ciel = part_de_ciel(im)
        dehors = ciel >= CIEL_PART
        force = DEHORS["blancs"] if dehors else BLANCS_MAX
        plafond = DEHORS["gamma_max"] if dehors else GAMMA_MAX
        saturation = DEHORS["saturation"] if dehors else SATURATION

        gains = gains_de_teinte(im, force)
        if max(abs(g - 1) for g in gains) > 0.005:
            canaux = [c.point(lambda v, g=g: min(255, int(v * g)))
                      for c, g in zip(im.split(), gains)]
            im = Image.merge("RGB", canaux)

        gris = im.convert("L")
        histogramme = gris.histogram()
        noir = min(percentile(histogramme, 0.005), 12)
        blanc = max(percentile(histogramme, 0.997), 245)

        moyenne = ImageStat.Stat(gris).mean[0]
        etendue = (moyenne - noir) / max(1, blanc - noir)
        viseé = min(0.98, CIBLE_LUMINANCE / 255)
        if 0 < etendue < viseé:
            import math
            gamma = min(plafond, math.log(etendue) / math.log(viseé))
            gamma = max(1.0, gamma)
        else:
            gamma = 1.0

        im = im.point(courbe(noir, blanc, gamma) * 3)
        im = im.filter(ImageFilter.UnsharpMask(**NETTETE))
        im = ImageEnhance.Color(im).enhance(saturation)

        apres = ImageStat.Stat(im.convert("L")).mean[0]
        return im, {"gains": [round(g, 3) for g in gains], "noir": noir,
                    "blanc": blanc, "gamma": round(gamma, 3),
                    "cadre": "plein air" if dehors else "interieur",
                    "luminance": [round(moyenne, 1), round(apres, 1)]}


def photos():
    for fichier in sorted(os.listdir(IMAGES)):
        nom, ext = os.path.splitext(fichier)
        if ext.lower() in (".jpg", ".jpeg") and not nom.startswith(IGNOREES):
            yield fichier


def main():
    appliquer = "--appliquer" in sys.argv
    refaire = "--refaire" in sys.argv
    journal = {}
    if os.path.exists(JOURNAL):
        journal = json.load(open(JOURNAL, encoding="utf-8"))

    if not appliquer:
        shutil.rmtree(ESSAI, ignore_errors=True)
        os.makedirs(ESSAI)

    faites = 0
    for fichier in photos():
        if fichier in journal and not refaire:
            print("  %-26s deja retouchee" % fichier)
            continue
        chemin = os.path.join(IMAGES, fichier)
        image, detail = retoucher(chemin)
        dest = chemin if appliquer else os.path.join(ESSAI, fichier)
        image.save(dest, "JPEG", quality=92, optimize=True, subsampling=0)
        journal[fichier] = detail
        faites += 1
        print("  %-26s %-9s teinte %s  gamma %.2f  luminance %.0f -> %.0f"
              % (fichier, detail["cadre"],
                 "/".join("%.2f" % g for g in detail["gains"]),
                 detail["gamma"], *detail["luminance"]))

    if appliquer and faites:
        with open(JOURNAL, "w", encoding="utf-8", newline="\n") as f:
            json.dump(journal, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
    print("\n%d photo(s) traitee(s), %s" % (faites,
          "originaux remplaces" if appliquer else "a relire dans images/retouchees/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
