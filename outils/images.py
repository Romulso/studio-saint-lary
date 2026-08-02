#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere les variantes WebP des photos du site.

Pour chaque JPEG de images/, produit images/opt/<nom>-<largeur>.webp
aux largeurs utiles (limitees a la taille de l'original). Les originaux
ne sont jamais modifies : ils restent la source, et servent aux flyers.

Usage :  python outils/images.py
"""

import json
import os
import sys

from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(RACINE, "images")
SORTIE = os.path.join(SOURCE, "opt")

LARGEURS = [1600, 1200, 800, 500]
QUALITE = 72

# Budget de poids par largeur, en octets. Une photo tres texturee (neige,
# feuillage, grain) peut peser trois fois plus qu'une autre a qualite egale :
# on baisse la qualite de ces seules images jusqu'a rentrer dans le budget.
BUDGET = {1600: 260_000, 1448: 230_000, 1200: 170_000, 800: 90_000, 500: 45_000}
PALIERS = [72, 66, 60, 55, 50, 45, 40]

# La photo d'ouverture est vue par tous les visiteurs, en plein cadre : elle
# merite une qualite superieure et un budget plus large que les vignettes.
SOIGNEES = {"balcon-fleuri": {"qualite": 84, "budget": 1.9}}


def variantes(chemin):
    """Genere les WebP d'une image et renvoie ses metadonnees."""
    nom = os.path.splitext(os.path.basename(chemin))[0]
    with Image.open(chemin) as im:
        im = im.convert("RGB")
        large, haut = im.size
        # Si l'original tombe entre deux paliers (1448 px par exemple), on
        # ajoute sa largeur native : sans elle on plafonnerait a 1200 px et
        # on jetterait de la definition deja disponible.
        cibles = [c for c in LARGEURS if c <= large]
        if large not in cibles and (not cibles or large > cibles[0] * 1.08):
            cibles = sorted(set(cibles + [large]), reverse=True)

        soin = SOIGNEES.get(nom)
        paliers = ([soin["qualite"]] + PALIERS) if soin else PALIERS

        produites = []
        for cible in cibles:
            if cible > large:
                continue
            hauteur = round(haut * cible / large)
            copie = im.resize((cible, hauteur), Image.LANCZOS)
            dest = os.path.join(SORTIE, "%s-%d.webp" % (nom, cible))
            budget = BUDGET.get(cible)
            if budget and soin:
                budget = int(budget * soin["budget"])
            for qualite in paliers:
                copie.save(dest, "WEBP", quality=qualite, method=6)
                if budget is None or os.path.getsize(dest) <= budget:
                    break
            produites.append(cible)
        if not produites:  # image plus petite que la plus petite cible
            dest = os.path.join(SORTIE, "%s-%d.webp" % (nom, large))
            im.save(dest, "WEBP", quality=QUALITE, method=6)
            produites.append(large)
    return {"largeur": large, "hauteur": haut, "variantes": sorted(produites, reverse=True)}


def image_partage():
    """Vignette 1200x630 pour Facebook, WhatsApp, LinkedIn et Twitter.

    En JPEG et non en WebP : plusieurs robots d'apercu ne lisent toujours pas
    le WebP et afficheraient un lien sans image."""
    source = os.path.join(SOURCE, "vue-montagne.jpeg")
    if not os.path.isfile(source):
        return
    # Cadrage choisi a la main sur l'original 2200x1650 : on garde le sommet,
    # le ciel et les arbres, on coupe la toiture en gravier du bas qui ne dit
    # rien de bon dans un apercu de lien. Ratio 1,905 ~ 1200x630.
    CADRE = (400, 60, 2200, 1005)
    with Image.open(source) as im:
        im = im.convert("RGB").crop(CADRE).resize((1200, 630), Image.LANCZOS)
        dest = os.path.join(SORTIE, "og-image.jpg")
        im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
    print("og-image.jpg             1200 x 630                 %4d Ko" % (os.path.getsize(dest) // 1024))


def main():
    if not os.path.isdir(SOURCE):
        sys.exit("Dossier images/ introuvable")
    os.makedirs(SORTIE, exist_ok=True)

    manifeste = {}
    avant = apres = 0

    for fichier in sorted(os.listdir(SOURCE)):
        if not fichier.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        chemin = os.path.join(SOURCE, fichier)
        nom = os.path.splitext(fichier)[0]
        infos = variantes(chemin)
        manifeste[nom] = infos

        poids_source = os.path.getsize(chemin)
        poids_max = os.path.getsize(
            os.path.join(SORTIE, "%s-%d.webp" % (nom, infos["variantes"][0]))
        )
        avant += poids_source
        apres += poids_max
        print(
            "%-24s %5d x %-5d  %4d Ko -> %4d Ko  (%s)"
            % (
                fichier,
                infos["largeur"],
                infos["hauteur"],
                poids_source // 1024,
                poids_max // 1024,
                ", ".join(str(v) for v in infos["variantes"]),
            )
        )

    image_partage()

    with open(os.path.join(SORTIE, "manifeste.json"), "w", encoding="utf-8") as f:
        json.dump(manifeste, f, ensure_ascii=False, indent=2, sort_keys=True)

    print("\nTotal (variante la plus large) : %d Ko -> %d Ko" % (avant // 1024, apres // 1024))


if __name__ == "__main__":
    main()
