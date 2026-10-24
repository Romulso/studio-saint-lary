#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refabrique le teaser video de la page Studio.

    python3 outils/teaser.py

Produit images/opt/teaser.mp4 (1280 x 720, muet, boucle) — c'est le
chemin que sert la page — et son affiche images/teaser-affiche.jpg, dont
outils/images.py tire ensuite les variantes WebP.

Le montage est genere image par image avec Pillow, puis assemble par
ffmpeg. Passer par Pillow plutot que par les filtres de texte de ffmpeg
evite les deboires de polices sur macOS et donne exactement la meme
typographie que le reste du site.

Il se refait a chaque changement de decor : le precedent montrait encore
le mobilier d'avant travaux et renvoyait vers l'ancienne adresse GitHub.

Prerequis :  pip3 install pillow  ·  brew install ffmpeg
"""

import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(RACINE, "images")
TRAVAIL = os.path.join("/tmp", "teaser-balcon-aure")

L, H = 1280, 720
FPS = 25
MARGE = 72

NUIT = (7, 16, 25)
LAITON_CLAIR = (224, 200, 148)
DOUX = (157, 177, 196)
BLANC = (255, 255, 255)

POLICE = "/System/Library/Fonts/Avenir Next.ttc"
SERIF = "/System/Library/Fonts/Optima.ttc"

# Chaque plan : fichier, duree en secondes, legende. None = carton.
PLANS = [
    (None,                      2.8, None),
    ("vue-montagne.jpeg",       3.4, "Saint-Lary-Soulan, au cœur de la vallée d'Aure"),
    ("terrasse-transats.jpg",   3.4, "Une terrasse de 9 m² face aux sommets"),
    ("canape-vue.jpg",          3.4, "27 m² ouverts sur la montagne"),
    ("sejour-salon.jpg",        3.4, "Meublé classé 3 étoiles, label Confort +"),
    ("cuisine-neuve.jpg",       3.4, "Cuisine équipée, lave-vaisselle, terrasse"),
    ("residence-salon.jpeg",    3.4, "Sauna, jacuzzi et piscine chauffée l'été"),
    (False,                     3.2, None),
]
FONDU = 0.45          # secondes de fondu enchaine entre deux plans


def fonte(taille, gras=False, serif=False):
    if serif:
        return ImageFont.truetype(SERIF, taille, index=3 if gras else 0)
    return ImageFont.truetype(POLICE, taille, index=5 if gras else 0)


def centre(d, y, texte, f, couleur, espacement=0):
    if espacement:
        large = sum(d.textlength(c, font=f) + espacement for c in texte) - espacement
        x = (L - large) / 2
        for c in texte:
            d.text((x, y), c, font=f, fill=couleur)
            x += d.textlength(c, font=f) + espacement
    else:
        d.text(((L - d.textlength(texte, font=f)) / 2, y), texte, font=f, fill=couleur)


def carton(ouverture=True):
    """Carton de debut ou de fin, sur fond de nuit."""
    im = Image.new("RGB", (L, H), NUIT)
    d = ImageDraw.Draw(im)
    if ouverture:
        centre(d, 300, "Le Balcon d'Aure.", fonte(64, serif=True), LAITON_CLAIR)
        centre(d, 395, "SAINT-LARY-SOULAN · VALLÉE D'AURE", fonte(18), DOUX, espacement=4)
    else:
        centre(d, 268, "Le Balcon d'Aure.", fonte(60, serif=True), LAITON_CLAIR)
        centre(d, 356, "Réservation en direct, sans commission", fonte(21), DOUX)
        centre(d, 404, "lebalcondaure.fr", fonte(30, gras=True), BLANC)
    return im


def plan_photo(nom, legende, avance):
    """Une photo recadree en 16/9, avec un leger mouvement de zoom."""
    source = Image.open(os.path.join(IMAGES, nom)).convert("RGB")
    zoom = 1.08 - 0.08 * avance            # on s'approche doucement
    cible_l, cible_h = int(L * zoom), int(H * zoom)
    ratio = max(cible_l / source.width, cible_h / source.height)
    agrandie = source.resize((max(1, round(source.width * ratio)),
                              max(1, round(source.height * ratio))), Image.LANCZOS)
    gauche = (agrandie.width - cible_l) // 2
    haut = (agrandie.height - cible_h) // 2
    im = agrandie.crop((gauche, haut, gauche + cible_l, haut + cible_h)).resize((L, H), Image.LANCZOS)

    # Voile du bas, pour que la legende reste lisible sur toute photo
    voile = Image.new("RGB", (L, 230), NUIT)
    masque = Image.new("L", (1, 230))
    for y in range(230):
        masque.putpixel((0, y), int(205 * (y / 229) ** 1.4))
    im.paste(voile, (0, H - 230), masque.resize((L, 230)))

    d = ImageDraw.Draw(im)
    d.text((MARGE, H - 92), legende, font=fonte(26), fill=BLANC)
    d.line([(MARGE, H - 120), (MARGE + 54, H - 120)], fill=LAITON_CLAIR, width=3)
    return im


def image_du_plan(plan, avance):
    fichier, _, legende = plan
    if fichier is None:
        return carton(True)
    if fichier is False:
        return carton(False)
    return plan_photo(fichier, legende, avance)


def main():
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg est introuvable : brew install ffmpeg")
    shutil.rmtree(TRAVAIL, ignore_errors=True)
    os.makedirs(TRAVAIL)

    fondu = int(FONDU * FPS)
    rang = 0
    for i, plan in enumerate(PLANS):
        total = int(plan[1] * FPS)
        suivant = PLANS[i + 1] if i + 1 < len(PLANS) else None
        for n in range(total):
            im = image_du_plan(plan, n / max(1, total - 1))
            # Fondu enchaine avec le plan suivant sur les derniers cadres
            reste = total - n
            if suivant and reste <= fondu:
                autre = image_du_plan(suivant, 0)
                im = Image.blend(im, autre, (fondu - reste + 1) / (fondu + 1))
            im.save(os.path.join(TRAVAIL, "%05d.jpg" % rang), "JPEG", quality=92)
            rang += 1

    sortie = os.path.join(IMAGES, "opt", "teaser.mp4")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-v", "error", "-y",
        "-framerate", str(FPS), "-i", os.path.join(TRAVAIL, "%05d.jpg"),
        "-c:v", "libx264", "-crf", "29", "-preset", "slow",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", sortie,
    ], check=True)

    # L'affiche est le premier cadre : ce que l'on voit avant lecture.
    carton(True).save(os.path.join(IMAGES, "teaser-affiche.jpg"),
                      "JPEG", quality=92, optimize=True)
    shutil.rmtree(TRAVAIL, ignore_errors=True)
    print("  opt/teaser.mp4   %d images, %.1f s, %d Ko"
          % (rang, rang / FPS, os.path.getsize(sortie) // 1024))


if __name__ == "__main__":
    main()
