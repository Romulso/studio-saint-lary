# -*- coding: utf-8 -*-
"""Genere les QR codes du site, en SVG (net a n'importe quelle taille d'impression).

    python3 outils/qr.py

Prerequis :  pip3 install qrcode

Deux QR distincts, et il ne faut pas les confondre :

  images/qr-site.svg    -> la page d'accueil. Celui des flyers et de l'affiche,
                           destine aux gens qui ne connaissent pas encore le studio.
  images/qr-livret.svg  -> le livret d'accueil. Celui affiche DANS le studio,
                           destine aux locataires deja sur place.

Correction d'erreur en niveau Q (25 % du code restaurable) : un QR imprime puis
plastifie prend des rayures, et celui du studio va durer des annees.
Bordure de 4 modules : c'est la zone blanche que les lecteurs exigent autour du
motif. La rogner fait echouer la lecture sur certains telephones.
"""

import os

import qrcode
import qrcode.image.svg

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# qr-site.svg n'est volontairement PAS regenere ici : il est deja en place dans
# les trois imprimes (flyer A5, flyer A6, affiche A4), a une taille calee sur ces
# maquettes. Le refabriquer avec d'autres reglages changerait ses dimensions et
# decalerait les mises en page. Pour le refaire un jour, ajouter la ligne
#   "qr-site.svg": "https://lebalcondaure.fr/",
# et verifier les trois imprimes avant d'imprimer quoi que ce soit.
CODES = {
    "qr-livret.svg": "https://lebalcondaure.fr/livret/",
}


def generer(nom, url):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(url)
    qr.make(fit=True)
    cible = os.path.join(RACINE, "images", nom)
    qr.make_image().save(cible)
    print("  %-16s  %-38s  version %d, %d modules"
          % (nom, url, qr.version, qr.modules_count))


if __name__ == "__main__":
    for nom, url in CODES.items():
        generer(nom, url)
