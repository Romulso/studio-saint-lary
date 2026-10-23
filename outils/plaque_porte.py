#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plaque de porte A5 : le nom du logement, et un QR code vers le site.

    python3 outils/plaque_porte.py

Produit images/plaque-porte.jpg en 1748 x 2480 px, soit 148 x 210 mm
(A5) a 300 points par pouce.

Elle s'adresse aux gens qui passent dans le couloir de la residence, pas
aux locataires : le QR code mene donc au site, pas au livret d'accueil.
Un voisin qui flashe devient un client, ou en parle autour de lui.

Tape-a-l'oeil veut dire lisible a trois metres : une photo plein cadre,
le nom en grand sur un fond sombre, et une seule invitation. Tout le
reste encombrerait.

Prerequis :  pip3 install qrcode pillow
"""

import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(RACINE, "images")

L, H = 1748, 2480            # A5 a 300 ppp
MARGE = 120
PHOTO = os.path.join(IMAGES, "terrasse-transats.jpg")

NUIT = (7, 16, 25)
LAITON_CLAIR = (224, 200, 148)
LAITON = (201, 168, 106)
DOUX = (157, 177, 196)
BLANC = (255, 255, 255)

POLICE = "/System/Library/Fonts/Avenir Next.ttc"
SERIF = "/System/Library/Fonts/Optima.ttc"


def fonte(taille, gras=False, serif=False):
    if serif:
        return ImageFont.truetype(SERIF, taille, index=3 if gras else 0)
    return ImageFont.truetype(POLICE, taille, index=5 if gras else 0)


def ecrire(d, xy, texte, f, couleur, espacement=0):
    x, y = xy
    if not espacement:
        d.text((x, y), texte, font=f, fill=couleur)
        return x + d.textlength(texte, font=f)
    for lettre in texte:
        d.text((x, y), lettre, font=f, fill=couleur)
        x += d.textlength(lettre, font=f) + espacement
    return x


def photo_cadree(largeur, hauteur):
    """Recadre la photo au format voulu, sans la deformer."""
    im = Image.open(PHOTO).convert("RGB")
    ratio = max(largeur / im.width, hauteur / im.height)
    im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.LANCZOS)
    gauche = (im.width - largeur) // 2
    haut = max(0, (im.height - hauteur) // 2 - round(im.height * 0.04))
    return im.crop((gauche, haut, gauche + largeur, haut + hauteur))


def fondu_vers_le_bas(im, depart, couleur):
    """Assombrit progressivement le bas de la photo, pour que le texte tienne."""
    hauteur = im.height - depart
    voile = Image.new("RGB", (im.width, hauteur), couleur)
    masque = Image.new("L", (1, hauteur))
    for y in range(hauteur):
        t = y / max(1, hauteur - 1)
        masque.putpixel((0, y), int(255 * (t ** 1.5)))
    im.paste(voile, (0, depart), masque.resize((im.width, hauteur)))


def qr_site(taille):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
                       box_size=10, border=2)
    qr.add_data("https://lebalcondaure.fr/")
    qr.make(fit=True)
    im = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return im.resize((taille, taille), Image.NEAREST)


def plaque():
    im = Image.new("RGB", (L, H), NUIT)

    # Photo sur la moitie haute, fondue vers le noir : le nom doit se lire
    # de loin, donc il se pose sur le fond sombre, jamais sur la photo.
    haut_photo = 1150
    im.paste(photo_cadree(L, haut_photo), (0, 0))
    fondu_vers_le_bas(im, 760, NUIT)

    d = ImageDraw.Draw(im)

    # Le nom, en grand
    ecrire(d, (MARGE, 1206), "SAINT-LARY-SOULAN", fonte(30), LAITON_CLAIR, espacement=7)
    d.text((MARGE, 1262), "Le Balcon", font=fonte(148, gras=True), fill=BLANC)
    d.text((MARGE, 1424), "d'Aure.", font=fonte(136, serif=True), fill=LAITON_CLAIR)

    # Filet puis ce que c'est
    d.line([(MARGE, 1660), (L - MARGE, 1660)], fill=LAITON, width=3)
    d.text((MARGE, 1700), "Studio 27 m²  ·  balcon vue montagne  ·  3 personnes",
           font=fonte(42), fill=DOUX)
    d.text((MARGE, 1762), "200 m des remontées  ·  150 m des thermes",
           font=fonte(42), fill=DOUX)

    # L'invitation et le QR : la raison d'etre de la plaque
    y, taille, cadre = 1880, 400, 24
    d.rounded_rectangle([MARGE - cadre, y - cadre,
                         MARGE + taille + cadre, y + taille + cadre],
                        radius=24, fill=BLANC)
    im.paste(qr_site(taille), (MARGE, y))

    tx = MARGE + taille + 96
    d.text((tx, y + 20), "À LOUER", font=fonte(34, gras=True), fill=LAITON_CLAIR)
    d.text((tx, y + 70), "Flashez", font=fonte(92, gras=True), fill=BLANC)
    d.text((tx, y + 170), "pour visiter.", font=fonte(80, serif=True), fill=LAITON_CLAIR)
    d.text((tx, y + 290), "lebalcondaure.fr", font=fonte(44, gras=True), fill=BLANC)

    # Pied discret
    d.text((MARGE, 2380), "Karine et Romuald  ·  06 42 84 55 42",
           font=fonte(34), fill=DOUX)

    return im


if __name__ == "__main__":
    image = plaque()
    chemin = os.path.join(IMAGES, "plaque-porte.jpg")
    image.save(chemin, "JPEG", quality=94, optimize=True, dpi=(300, 300))
    print("  %-22s %d x %d px  %d Ko"
          % (os.path.basename(chemin), image.width, image.height,
             os.path.getsize(chemin) // 1024))
