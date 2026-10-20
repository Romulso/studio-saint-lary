#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carte d'accueil 10x15 cm, une seule face, a poser dans le studio.

    python3 outils/carte_accueil.py

Produit images/carte-accueil.jpg en 1181 x 1772 px, soit 10 x 15 cm a
300 points par pouce : le format d'un tirage photo ordinaire, que
n'importe quel labo imprime pour quelques centimes sur papier epais.

Une seule face : le locataire la lit d'un coup d'oeil, posee sur la
table. Tout ce qui demande une page entiere — equipements, services de
la residence, adresses de la vallee — vit dans le livret en ligne, ou
mene le QR code.

La ligne du wifi reste vide a dessein : la carte s'imprime une fois pour
toutes et le code s'ecrit au feutre effacable, ou se remplit ici quand il
sera connu.

Prerequis :  pip3 install qrcode pillow
"""

import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "images")

L, H = 1181, 1772            # 10 x 15 cm a 300 ppp
MARGE = 74

NUIT = (7, 16, 25)
JOUR = (245, 248, 251)
ENCRE = (13, 34, 51)
LAITON = (143, 106, 28)
LAITON_CLAIR = (224, 200, 148)
DOUX = (157, 177, 196)
TENU = (120, 141, 160)
BLANC = (255, 255, 255)

POLICE = "/System/Library/Fonts/Avenir Next.ttc"
SERIF = "/System/Library/Fonts/Optima.ttc"


def fonte(taille, gras=False, serif=False):
    if serif:
        return ImageFont.truetype(SERIF, taille, index=3 if gras else 0)
    return ImageFont.truetype(POLICE, taille, index=5 if gras else 0)


def texte(d, xy, contenu, f, couleur, interligne=1.32, largeur=None, espacement=0):
    """Ecrit un texte, le coupe a `largeur` si besoin, renvoie le bas atteint."""
    x, y = xy
    lignes = []
    for paragraphe in contenu.split("\n"):
        if largeur is None:
            lignes.append(paragraphe)
            continue
        courante = ""
        for mot in paragraphe.split(" "):
            essai = (courante + " " + mot).strip()
            if d.textlength(essai, font=f) <= largeur or not courante:
                courante = essai
            else:
                lignes.append(courante)
                courante = mot
        lignes.append(courante)
    haut = f.size * interligne
    for ligne in lignes:
        if espacement:
            cx = x
            for lettre in ligne:
                d.text((cx, y), lettre, font=f, fill=couleur)
                cx += d.textlength(lettre, font=f) + espacement
        else:
            d.text((x, y), ligne, font=f, fill=couleur)
        y += haut
    return y


def etiquette(d, y, mot):
    """Petit intertitre dore en capitales espacees."""
    texte(d, (MARGE, y), mot, fonte(19, gras=True), LAITON, espacement=3)
    return y + 40


def qr_livret(taille):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
                       box_size=10, border=2)
    qr.add_data("https://lebalcondaure.fr/livret/")
    qr.make(fit=True)
    im = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return im.resize((taille, taille), Image.NEAREST)


def carte():
    im = Image.new("RGB", (L, H), JOUR)
    d = ImageDraw.Draw(im)
    pleine = L - 2 * MARGE

    # ---------------- Bandeau de tete ----------------
    d.rectangle([0, 0, L, 300], fill=NUIT)
    y = texte(d, (MARGE, 56), "SAINT-LARY-SOULAN \u00b7 VALL\u00c9E D'AURE",
              fonte(19), LAITON_CLAIR, espacement=3)
    y = texte(d, (MARGE, y + 16), "Bienvenue", fonte(66, gras=True), BLANC, interligne=1.02)
    texte(d, (MARGE, y - 4), "au Balcon d'Aure.", fonte(58, serif=True), LAITON_CLAIR)

    # ---------------- Contact ----------------
    y = etiquette(d, 352, "NOUS JOINDRE")
    y = texte(d, (MARGE, y), "06 42 84 55 42   \u00b7   06 27 35 23 28",
              fonte(40, gras=True), ENCRE)
    y = texte(d, (MARGE, y + 2), "Karine et Romuald \u2014 appel, SMS ou WhatsApp",
              fonte(22), TENU)

    # ---------------- Wifi, a remplir ----------------
    y += 26
    d.rounded_rectangle([MARGE, int(y), L - MARGE, int(y) + 150], radius=16,
                        outline=(197, 210, 222), width=3)
    texte(d, (MARGE + 28, y + 22), "WIFI", fonte(19, gras=True), LAITON, espacement=3)
    texte(d, (MARGE + 28, y + 62), "R\u00e9seau", fonte(24), ENCRE)
    texte(d, (MARGE + 28, y + 104), "Mot de passe", fonte(24), ENCRE)
    for ligne_y in (y + 90, y + 132):
        d.line([(MARGE + 270, ligne_y), (L - MARGE - 28, ligne_y)],
               fill=(170, 186, 200), width=2)
    y += 150

    # ---------------- Urgences, sur une ligne ----------------
    y = etiquette(d, y + 30, "URGENCES")
    pas = pleine // 4
    for i, (numero, quoi) in enumerate([("15", "SAMU"), ("18", "Pompiers"),
                                        ("17", "Police"), ("112", "Europ\u00e9en")]):
        x = MARGE + i * pas
        d.text((x, y), numero, font=fonte(42, gras=True), fill=ENCRE)
        d.text((x + d.textlength(numero, font=fonte(42, gras=True)) + 12, y + 16),
               quoi, font=fonte(21), fill=TENU)
    y += 72

    # ---------------- Depart ----------------
    d.line([(MARGE, y + 18), (L - MARGE, y + 18)], fill=(201, 168, 106), width=2)
    y = etiquette(d, y + 48, "AVANT DE PARTIR")
    y = texte(d, (MARGE, y - 6), "D\u00e9part avant 10 h", fonte(36, gras=True), ENCRE)
    y += 16
    for ligne in ["Lave-vaisselle vid\u00e9 et rang\u00e9",
                  "Poubelles d\u00e9pos\u00e9es au local",
                  "Draps retir\u00e9s, lit laiss\u00e9 ouvert",
                  "Multiprises d\u00e9branch\u00e9es",
                  "Frigo vid\u00e9, thermostat sur 0, porte entrouverte",
                  "Cl\u00e9s remises dans la bo\u00eete \u00e0 cl\u00e9s"]:
        d.ellipse([MARGE + 4, int(y) + 13, MARGE + 14, int(y) + 23], fill=LAITON)
        y = texte(d, (MARGE + 36, y), ligne, fonte(26), ENCRE) + 4
    y = texte(d, (MARGE, y + 8),
              "Le m\u00e9nage est en option : sinon, suivez ce que nous avons convenu.",
              fonte(21), TENU, largeur=pleine, interligne=1.38)

    # ---------------- Regles ----------------
    d.line([(MARGE, y + 20), (L - MARGE, y + 20)], fill=(201, 168, 106), width=2)
    y = etiquette(d, y + 48, "LA MAISON")
    for titre, detail in [("Non-fumeur", "merci de fumer sur la terrasse"),
                          ("Trois personnes", "le nombre convenu \u00e0 la r\u00e9servation"),
                          ("Chiens l'\u00e9t\u00e9 seulement", "sur accord, jamais en hiver"),
                          ("Calme apr\u00e8s 22 h", "la r\u00e9sidence est habit\u00e9e \u00e0 l'ann\u00e9e")]:
        d.text((MARGE, y), titre, font=fonte(25, gras=True), fill=ENCRE)
        d.text((MARGE + d.textlength(titre, font=fonte(25, gras=True)) + 16, y + 3),
               "\u00b7  " + detail, font=fonte(22), fill=TENU)
        y += 38

    # ---------------- Livret et avis ----------------
    d.rectangle([0, H - 300, L, H], fill=NUIT)
    taille = 186
    im.paste(qr_livret(taille), (MARGE, H - 300 + 58))
    tx = MARGE + taille + 36
    yy = H - 300 + 56
    texte(d, (tx, yy), "LE LIVRET COMPLET", fonte(19, gras=True), LAITON_CLAIR, espacement=3)
    texte(d, (tx, yy + 40),
          "\u00c9quipements, services de la r\u00e9sidence, nos adresses dans la vall\u00e9e.",
          fonte(22), DOUX, largeur=L - MARGE - tx, interligne=1.35)
    texte(d, (tx, yy + 116), "lebalcondaure.fr/livret", fonte(26, gras=True), BLANC)
    texte(d, (tx, yy + 160),
          "Votre s\u00e9jour vous a plu ? lebalcondaure.fr/livre-d-or",
          fonte(21), DOUX, largeur=L - MARGE - tx, interligne=1.35)

    return im


if __name__ == "__main__":
    image = carte()
    chemin = os.path.join(SORTIE, "carte-accueil.jpg")
    image.save(chemin, "JPEG", quality=94, optimize=True, dpi=(300, 300))
    print("  %-24s %d x %d px  %d Ko"
          % (os.path.basename(chemin), image.width, image.height,
             os.path.getsize(chemin) // 1024))
