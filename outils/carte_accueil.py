#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carte d'accueil 13x18 cm, une seule face, a poser dans le studio.

    python3 outils/carte_accueil.py

Produit ../carte-accueil-13x18.jpg en 1535 x 2126 px, soit 13 x 18 cm a
300 points par pouce : un format de tirage photo courant, que n'importe
quel labo imprime pour quelques centimes sur papier epais.

Une seule face : le locataire la lit d'un coup d'oeil, posee sur la
table. Tout ce qui demande une page entiere — equipements, services de
la residence, adresses de la vallee — vit dans le livret en ligne, ou
mene le QR code.

La carte sort VOLONTAIREMENT du depot : elle porte le code du wifi, et
tout ce qui vit dans le depot est publie sur lebalcondaure.fr. Elle
s'imprime depuis ../carte-accueil.html, en local.

Le code lui-meme n'est pas dans ce fichier non plus : il se lit dans
../carte-accueil-wifi.txt, deux lignes, hors du depot —

    reseau: le nom du reseau
    code: le mot de passe

Sans ce fichier, la carte sort avec deux lignes vides a remplir au
feutre : c'est ce qu'il faut pour une carte montree en exemple.

Le dessin est decrit aux cotes du 10 x 15 d'origine et mis a l'echelle
par ECHELLE : changer de format ne demande que de changer L, H et ce
facteur.

Prerequis :  pip3 install qrcode pillow
"""

import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.abspath(os.path.join(RACINE, ".."))
WIFI = os.path.join(SORTIE, "carte-accueil-wifi.txt")

L, H = 1535, 2126            # 13 x 18 cm a 300 ppp
ECHELLE = H / 1772.0         # le dessin a ete regle pour un 10 x 15
MARGE = 89

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


def acces_wifi():
    """Rend (reseau, code), chaines vides si le fichier n'existe pas."""
    valeurs = {"reseau": "", "code": ""}
    if os.path.exists(WIFI):
        for ligne in open(WIFI, encoding="utf-8"):
            if ":" in ligne:
                cle, _, valeur = ligne.partition(":")
                cle = cle.strip().lower()
                if cle in valeurs:
                    valeurs[cle] = valeur.strip()
    return valeurs["reseau"], valeurs["code"]


def e(valeur):
    """Une cote du dessin d'origine, portee au format courant."""
    return int(round(valeur * ECHELLE))


def fonte(taille, gras=False, serif=False):
    if serif:
        return ImageFont.truetype(SERIF, e(taille), index=3 if gras else 0)
    return ImageFont.truetype(POLICE, e(taille), index=5 if gras else 0)


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
    texte(d, (MARGE, y), mot, fonte(19, gras=True), LAITON, espacement=e(3))
    return y + e(40)


def qr_livret(taille):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q,
                       box_size=10, border=2)
    qr.add_data("https://lebalcondaure.fr/livret/")
    qr.make(fit=True)
    im = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return im.resize((taille, taille), Image.NEAREST)


def carte():
    reseau, code = acces_wifi()
    im = Image.new("RGB", (L, H), JOUR)
    d = ImageDraw.Draw(im)
    pleine = L - 2 * MARGE

    # ---------------- Bandeau de tete ----------------
    d.rectangle([0, 0, L, e(300)], fill=NUIT)
    y = texte(d, (MARGE, e(56)), "SAINT-LARY-SOULAN · VALLÉE D'AURE",
              fonte(19), LAITON_CLAIR, espacement=e(3))
    y = texte(d, (MARGE, y + e(16)), "Bienvenue", fonte(66, gras=True), BLANC,
              interligne=1.02)
    texte(d, (MARGE, y - e(4)), "au Balcon d'Aure.", fonte(58, serif=True), LAITON_CLAIR)

    # ---------------- Contact ----------------
    y = etiquette(d, e(352), "NOUS JOINDRE")
    y = texte(d, (MARGE, y), "06 42 84 55 42   ·   06 27 35 23 28",
              fonte(40, gras=True), ENCRE)
    y = texte(d, (MARGE, y + e(2)), "Karine et Romuald — appel, SMS ou WhatsApp",
              fonte(22), TENU)

    # ---------------- Wifi ----------------
    y += e(26)
    haut_cadre = e(150)
    d.rounded_rectangle([MARGE, int(y), L - MARGE, int(y) + haut_cadre],
                        radius=e(16), outline=(197, 210, 222), width=e(3))
    texte(d, (MARGE + e(28), y + e(22)), "WIFI", fonte(19, gras=True), LAITON,
          espacement=e(3))
    colonne = MARGE + e(270)
    for decalage, mot, valeur in ((e(62), "Réseau", reseau),
                                  (e(104), "Mot de passe", code)):
        texte(d, (MARGE + e(28), y + decalage), mot, fonte(24), TENU)
        if valeur:
            texte(d, (colonne, y + decalage - e(3)), valeur, fonte(27, gras=True), ENCRE)
        else:
            d.line([(colonne, y + decalage + e(28)), (L - MARGE - e(28), y + decalage + e(28))],
                   fill=(170, 186, 200), width=e(2))
    y += haut_cadre

    # ---------------- Urgences, sur une ligne ----------------
    y = etiquette(d, y + e(30), "URGENCES")
    pas = pleine // 4
    gras42 = fonte(42, gras=True)
    for i, (numero, quoi) in enumerate([("15", "SAMU"), ("18", "Pompiers"),
                                        ("17", "Police"), ("112", "Européen")]):
        x = MARGE + i * pas
        d.text((x, y), numero, font=gras42, fill=ENCRE)
        d.text((x + d.textlength(numero, font=gras42) + e(12), y + e(16)),
               quoi, font=fonte(21), fill=TENU)
    y += e(72)

    # ---------------- Depart ----------------
    d.line([(MARGE, y + e(18)), (L - MARGE, y + e(18))], fill=(201, 168, 106), width=e(2))
    y = etiquette(d, y + e(48), "AVANT DE PARTIR")
    y = texte(d, (MARGE, y - e(6)), "Départ avant 10 h", fonte(36, gras=True), ENCRE)
    y += e(16)
    for ligne in ["Lave-vaisselle vidé et rangé",
                  "Poubelles déposées au local",
                  "Draps retirés, lit laissé ouvert",
                  "Multiprises débranchées",
                  "Frigo vidé, thermostat sur 0, porte entrouverte",
                  "Clés remises dans la boîte à clés"]:
        d.ellipse([MARGE + e(4), int(y) + e(13), MARGE + e(14), int(y) + e(23)], fill=LAITON)
        y = texte(d, (MARGE + e(36), y), ligne, fonte(26), ENCRE) + e(4)
    y = texte(d, (MARGE, y + e(8)),
              "Le ménage est en option : sinon, suivez ce que nous avons convenu.",
              fonte(21), TENU, largeur=pleine, interligne=1.38)

    # ---------------- Regles ----------------
    d.line([(MARGE, y + e(20)), (L - MARGE, y + e(20))], fill=(201, 168, 106), width=e(2))
    y = etiquette(d, y + e(48), "LA MAISON")
    gras25 = fonte(25, gras=True)
    for titre, detail in [("Non-fumeur", "merci de fumer sur la terrasse"),
                          ("Trois personnes", "le nombre convenu à la réservation"),
                          ("Chiens l'été seulement", "sur accord, jamais en hiver"),
                          ("Calme après 22 h", "la résidence est habitée à l'année")]:
        d.text((MARGE, y), titre, font=gras25, fill=ENCRE)
        d.text((MARGE + d.textlength(titre, font=gras25) + e(16), y + e(3)),
               "·  " + detail, font=fonte(22), fill=TENU)
        y += e(38)

    # ---------------- Livret et avis ----------------
    pied = H - e(300)
    if y > pied - e(10):
        raise SystemExit("Le contenu deborde sur le pied de page : %d > %d" % (y, pied))
    d.rectangle([0, pied, L, H], fill=NUIT)
    taille = e(186)
    im.paste(qr_livret(taille), (MARGE, pied + e(58)))
    tx = MARGE + taille + e(36)
    yy = pied + e(56)
    texte(d, (tx, yy), "LE LIVRET COMPLET", fonte(19, gras=True), LAITON_CLAIR,
          espacement=e(3))
    texte(d, (tx, yy + e(40)),
          "Équipements, services de la résidence, nos adresses dans la vallée.",
          fonte(22), DOUX, largeur=L - MARGE - tx, interligne=1.35)
    texte(d, (tx, yy + e(116)), "lebalcondaure.fr/livret", fonte(26, gras=True), BLANC)
    texte(d, (tx, yy + e(160)),
          "Votre séjour vous a plu ? lebalcondaure.fr/livre-d-or",
          fonte(21), DOUX, largeur=L - MARGE - tx, interligne=1.35)

    return im


if __name__ == "__main__":
    image = carte()
    chemin = os.path.join(SORTIE, "carte-accueil-13x18.jpg")
    image.save(chemin, "JPEG", quality=94, optimize=True, dpi=(300, 300))
    print("  %-26s %d x %d px  %d Ko  (wifi : %s)"
          % (os.path.basename(chemin), image.width, image.height,
             os.path.getsize(chemin) // 1024,
             "rempli" if acces_wifi()[0] else "lignes vides"))
