#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carte d'accueil 10x15 cm, recto-verso, a poser dans le studio.

    python3 outils/carte_accueil.py

Produit images/carte-accueil-recto.jpg et images/carte-accueil-verso.jpg,
en 1181 x 1772 px, soit 10 x 15 cm a 300 points par pouce : le format
d'un tirage photo ordinaire, que n'importe quel labo imprime pour
quelques centimes sur papier epais.

Deux faces plutot qu'une : tout faire tenir au recto obligerait a un
corps de texte si petit qu'il ne se lirait plus. Le recto porte ce qu'on
cherche en arrivant (contact, wifi, urgences, QR du livret), le verso ce
qu'on lit la veille du depart (consignes et regles).

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
MARGE = 86

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
    # Avenir Next.ttc : 0 = Regular, 1 = Medium, 4 = Demi Bold, 5 = Bold
    return ImageFont.truetype(POLICE, taille, index=5 if gras else 0)


def texte(d, xy, contenu, f, couleur, interligne=1.35, largeur=None, espacement=0):
    """Ecrit un texte, le coupe a `largeur` si besoin, renvoie le bas atteint."""
    x, y = xy
    lignes = []
    for paragraphe in contenu.split("\n"):
        if largeur is None:
            lignes.append(paragraphe)
            continue
        mots, courante = paragraphe.split(" "), ""
        for mot in mots:
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


def filet(d, y, x1=MARGE, x2=L - MARGE, couleur=(201, 168, 106), epaisseur=2):
    d.line([(x1, y), (x2, y)], fill=couleur, width=epaisseur)


def qr_livret(taille):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
                       box_size=10, border=2)
    qr.add_data("https://lebalcondaure.fr/livret/")
    qr.make(fit=True)
    im = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return im.resize((taille, taille), Image.NEAREST)


# --------------------------------------------------------------------------

def recto():
    im = Image.new("RGB", (L, H), JOUR)
    d = ImageDraw.Draw(im)

    # Bandeau de tete
    d.rectangle([0, 0, L, 470], fill=NUIT)
    y = texte(d, (MARGE, 92), "SAINT-LARY-SOULAN · VALLÉE D'AURE",
              fonte(21), LAITON_CLAIR, espacement=3)
    y = texte(d, (MARGE, y + 26), "Bienvenue", fonte(86, gras=True), BLANC, interligne=1.05)
    y = texte(d, (MARGE, y - 6), "au Balcon d'Aure.", fonte(74, serif=True), LAITON_CLAIR,
              interligne=1.1)
    texte(d, (MARGE, y + 18),
          "Pour le ski, la randonnée ou simplement souffler : faites comme chez vous.",
          fonte(25), DOUX, largeur=L - 2 * MARGE, interligne=1.45)

    # Contact
    y = 540
    texte(d, (MARGE, y), "NOUS JOINDRE", fonte(21, gras=True), LAITON, espacement=3)
    y = texte(d, (MARGE, y + 46), "Karine et Romuald", fonte(30), ENCRE)
    y = texte(d, (MARGE, y + 4), "06 42 84 55 42   ·   06 27 35 23 28",
              fonte(40, gras=True), ENCRE)
    y = texte(d, (MARGE, y + 2), "Appel, SMS ou WhatsApp — n'hésitez jamais.",
              fonte(23), TENU)

    # Wifi, a remplir
    y += 36
    d.rounded_rectangle([MARGE, int(y), L - MARGE, int(y) + 190], radius=18,
                        outline=(197, 210, 222), width=3)
    texte(d, (MARGE + 34, y + 28), "WIFI", fonte(21, gras=True), LAITON, espacement=3)
    texte(d, (MARGE + 34, y + 74), "Réseau", fonte(26), ENCRE)
    texte(d, (MARGE + 34, y + 126), "Mot de passe", fonte(26), ENCRE)
    for ligne_y in (y + 104, y + 156):
        d.line([(MARGE + 300, ligne_y), (L - MARGE - 34, ligne_y)],
               fill=(170, 186, 200), width=2)
    y += 190

    # Urgences
    y += 46
    texte(d, (MARGE, y), "URGENCES", fonte(21, gras=True), LAITON, espacement=3)
    y += 52
    colonnes = [("15", "SAMU"), ("18", "Pompiers"), ("17", "Police"), ("112", "Européen")]
    pas = (L - 2 * MARGE) // 4
    for i, (numero, quoi) in enumerate(colonnes):
        x = MARGE + i * pas
        d.text((x, y), numero, font=fonte(52, gras=True), fill=ENCRE)
        d.text((x, y + 66), quoi, font=fonte(22), fill=TENU)
    y += 120

    # QR du livret
    filet(d, y + 20)
    taille = 230
    qr = qr_livret(taille)
    im.paste(qr, (MARGE, int(y) + 56))
    tx = MARGE + taille + 44
    texte(d, (tx, y + 72), "LE LIVRET COMPLET", fonte(21, gras=True), LAITON, espacement=3)
    texte(d, (tx, y + 116),
          "Équipements, services de la résidence, nos adresses dans la vallée.",
          fonte(25), ENCRE, largeur=L - MARGE - tx, interligne=1.4)
    texte(d, (tx, y + 216), "lebalcondaure.fr/livret", fonte(25, gras=True), LAITON)

    # Pied : sans lui, le bas de la carte reste vide
    d.rectangle([0, H - 196, L, H], fill=NUIT)
    texte(d, (MARGE, H - 142), "lebalcondaure.fr", fonte(34, serif=True), BLANC)
    texte(d, (MARGE, H - 86),
          "Résidence Royal Milan  ·  Meublé de tourisme n° 65388002324GP",
          fonte(21), DOUX)

    return im


def verso():
    im = Image.new("RGB", (L, H), JOUR)
    d = ImageDraw.Draw(im)

    y = 110
    texte(d, (MARGE, y), "AVANT DE PARTIR", fonte(21, gras=True), LAITON, espacement=3)
    y = texte(d, (MARGE, y + 46), "Départ avant 10 h", fonte(44, gras=True), ENCRE)
    y += 18
    consignes = [
        "Vider et ranger le lave-vaisselle",
        "Sortir les poubelles et les déposer au local",
        "Retirer les draps du lit et le laisser ouvert",
        "Débrancher les multiprises",
        "Vider le frigo, thermostat sur 0, porte entrouverte",
        "Laisser la porte de la salle d'eau ouverte",
        "Remettre les clés dans la boîte à clés",
    ]
    for ligne in consignes:
        d.ellipse([MARGE + 4, int(y) + 16, MARGE + 16, int(y) + 28], fill=LAITON)
        y = texte(d, (MARGE + 42, y), ligne, fonte(27), ENCRE,
                  largeur=L - MARGE - (MARGE + 42)) + 20

    y += 10
    texte(d, (MARGE, y),
          "Vous avez pris le forfait ménage ? Nous nous occupons du reste. "
          "Sinon, suivez ce que nous avons convenu ensemble avant votre arrivée.",
          fonte(23), TENU, largeur=L - 2 * MARGE, interligne=1.4)

    # Regles
    y += 128
    filet(d, y)
    y += 54
    texte(d, (MARGE, y), "LA MAISON", fonte(21, gras=True), LAITON, espacement=3)
    y += 52
    regles = [
        ("Non-fumeur", "Le studio est strictement non-fumeur. Merci de fumer "
                       "sur la terrasse et de ne pas laisser de mégots."),
        ("Animaux", "Chiens acceptés l'été uniquement, sur accord écrit. "
                    "Aucun animal en hiver."),
        ("Trois personnes", "Le nombre d'occupants convenu à la réservation "
                            "doit être respecté."),
        ("Le voisinage", "La résidence est habitée à l'année : merci pour "
                         "le calme après 22 h."),
    ]
    for titre, detail in regles:
        y = texte(d, (MARGE, y), titre, fonte(28, gras=True), ENCRE)
        y = texte(d, (MARGE, y + 4), detail, fonte(23), TENU,
                  largeur=L - 2 * MARGE, interligne=1.38) + 34

    # Avis
    y = H - 330
    d.rectangle([0, int(y), L, H], fill=NUIT)
    texte(d, (MARGE, y + 56), "VOTRE SÉJOUR VOUS A PLU ?", fonte(21, gras=True),
          LAITON_CLAIR, espacement=3)
    texte(d, (MARGE, y + 106),
          "Quelques mots nous aident énormément, et aident les prochains à choisir.",
          fonte(25), DOUX, largeur=L - 2 * MARGE, interligne=1.4)
    texte(d, (MARGE, y + 196), "lebalcondaure.fr/livre-d-or",
          fonte(32, gras=True), BLANC)
    texte(d, (MARGE, y + 244), "ou directement sur Airbnb", fonte(23), DOUX)

    return im


if __name__ == "__main__":
    for nom, image in (("recto", recto()), ("verso", verso())):
        chemin = os.path.join(SORTIE, "carte-accueil-%s.jpg" % nom)
        image.save(chemin, "JPEG", quality=94, optimize=True, dpi=(300, 300))
        print("  %-28s %d x %d px  %d Ko"
              % (os.path.basename(chemin), image.width, image.height,
                 os.path.getsize(chemin) // 1024))
