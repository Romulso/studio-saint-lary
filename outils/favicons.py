#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rasterise favicon.svg en PNG (Chrome mobile, Safari iOS, ecran d'accueil).

Le motif est redessine ici en Pillow plutot que rendu depuis le SVG : cela
evite une dependance de plus, et la figure est assez simple pour rester
identique aux deux endroits. Si favicon.svg change, ajuster MOTIF.

Usage :  python outils/favicons.py
"""

import os

from PIL import Image, ImageDraw

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUIT = (13, 34, 51)
LAITON = (201, 168, 106)
NEIGE = (242, 230, 205)
LAITON_FONCE = (143, 106, 28)

TAILLES = {"favicon-96.png": 96, "apple-touch-icon.png": 180,
           "icone-192.png": 192, "icone-512.png": 512}

# Coordonnees sur une grille 64x64, identiques a favicon.svg.
MOTIF = {
    "sommets": [(8, 44), (22, 24), (31, 35), (41, 19), (56, 44)],
    "neige": [(41, 19), (46, 27), (36, 27)],
    "rambarde": (8, 47, 56, 50),
    "barreaux": [(13, 50, 15.5, 57), (30.75, 50, 33.25, 57), (48.5, 50, 51, 57)],
}


def dessiner(taille, fond_transparent=False):
    """Dessine a 8x puis reduit : bords lisses sans antialiasing natif."""
    echelle = 8
    c = taille * echelle
    k = c / 64.0
    im = Image.new("RGBA", (c, c), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if not fond_transparent:
        d.rounded_rectangle([0, 0, c - 1, c - 1], radius=14 * k, fill=NUIT)

    d.polygon([(x * k, y * k) for x, y in MOTIF["sommets"]], fill=LAITON)
    d.polygon([(x * k, y * k) for x, y in MOTIF["neige"]], fill=NEIGE)

    x0, y0, x1, y1 = MOTIF["rambarde"]
    d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=1.5 * k, fill=LAITON_FONCE)
    for x0, y0, x1, y1 in MOTIF["barreaux"]:
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=1.25 * k, fill=LAITON_FONCE)

    return im.resize((taille, taille), Image.LANCZOS)


def main():
    for nom, taille in TAILLES.items():
        image = dessiner(taille)
        if nom == "apple-touch-icon.png":
            # iOS n'applique pas de transparence : fond plein obligatoire.
            fond = Image.new("RGB", image.size, NUIT)
            fond.paste(image, mask=image.split()[3])
            image = fond
        chemin = os.path.join(RACINE, nom)
        image.save(chemin)
        print("%-22s %3d x %-3d  %4d octets" % (nom, taille, taille, os.path.getsize(chemin)))


if __name__ == "__main__":
    main()
