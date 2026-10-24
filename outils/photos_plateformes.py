#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare le lot de photos a deposer sur Airbnb, Booking et l'office de tourisme.

    python3 outils/photos_plateformes.py

Produit ../photos-plateformes.zip : les memes photos que le site, numerotees
dans l'ordre de depot, avec un fichier de legendes a recopier. L'archive sort
du depot a dessein — elle n'a rien a faire sur un site public.

L'ordre compte : la premiere photo sert de couverture dans les resultats de
recherche. On montre d'abord le sejour, puis les pieces, puis la terrasse,
puis la residence, et les environs en dernier : un voyageur qui fait defiler
veut d'abord savoir ou il dort.
"""

import os
import shutil
import sys
import zipfile

from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(RACINE, "images")
SORTIE = os.path.abspath(os.path.join(RACINE, ".."))

# (fichier source, nom de depot, legende)
LOT = [
    ("terrasse-transats.jpg",      "couverture-terrasse",      "La terrasse face aux sommets de la vallée d'Aure"),
    ("canape-vue.jpg",             "sejour-vue-montagne",      "Le séjour ouvert sur la baie vitrée et la montagne"),
    ("sejour-salon.jpg",           "sejour-canapes",           "Deux canapés, coin cuisine au fond"),
    ("sejour-table.jpg",           "sejour-table",             "La table et ses quatre chaises"),
    ("sejour-tv-2026.jpg",         "sejour-television",        "Côté télévision, vu depuis la baie vitrée"),
    ("cuisine-plan-serre.jpg",     "cuisine",                  "Cuisine équipée : plaques, micro-ondes, lave-vaisselle"),
    ("salle-eau-2026.jpg",         "salle-eau",                "Salle d'eau rénovée, douche à l'italienne"),
    ("entree.jpg",                 "entree",                   "L'entrée, meuble à chaussures et patères"),
    ("terrasse-soleil.jpg",        "terrasse-soleil",          "La terrasse au soleil, 9 m² plein ciel"),
    ("terrasse-depuis-sejour.jpg", "terrasse-depuis-sejour",   "La terrasse vue depuis l'intérieur"),
    ("terrasse-cafe.jpg",          "terrasse-petit-dejeuner",  "Petit déjeuner sur la terrasse"),
    ("vue-montagne.jpeg",          "vue-vallee",               "La vallée d'Aure depuis la résidence"),
    ("residence-salon.jpeg",       "residence-salon",          "Le salon commun de la résidence et sa cheminée"),
    ("residence-bar.jpeg",         "residence-bar",            "Le bar de la résidence"),
    ("residence-billard.jpeg",     "residence-billard",        "Le billard"),
    ("residence-accueil.jpeg",     "residence-accueil",        "Le hall d'accueil"),
    ("village-vallee.jpg",         "village-vallee",           "Le village et les prairies de la vallée, vus d'en haut"),
    ("lac-neige.jpg",              "lac-neige",                "Un lac d'altitude encore pris par la neige"),
    ("marmotte.jpg",               "marmotte",                 "Une marmotte au bord d'une route de montagne"),
]

ENTETE = """ORDRE DE DÉPÔT ET LÉGENDES — Le Balcon d'Aure
====================================================

Déposez les photos dans cet ordre : la premiere sert de couverture
dans les resultats de recherche. Les legendes se saisissent une a une
apres l envoi, dans Airbnb comme dans Booking.

"""


def main():
    dossier = os.path.join(SORTIE, "photos-plateformes")
    shutil.rmtree(dossier, ignore_errors=True)
    os.makedirs(dossier)

    lignes = [ENTETE]
    for rang, (source, nom, legende) in enumerate(LOT, 1):
        chemin = os.path.join(IMAGES, source)
        if not os.path.exists(chemin):
            sys.exit("Photo introuvable : %s" % source)
        cible = "%02d-%s.jpg" % (rang, nom)
        shutil.copy2(chemin, os.path.join(dossier, cible))
        with Image.open(chemin) as im:
            large, haut = im.size
        poids = os.path.getsize(chemin) // 1024
        lignes.append("%-32s %dx%d  %-8s %4d Ko\n    %s\n"
                      % (cible, large, haut,
                         "paysage" if large >= haut else "portrait", poids, legende))

    with open(os.path.join(dossier, "ordre-et-legendes.txt"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lignes))

    archive = os.path.join(SORTIE, "photos-plateformes.zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for fichier in sorted(os.listdir(dossier)):
            z.write(os.path.join(dossier, fichier), "photos-plateformes/" + fichier)
    shutil.rmtree(dossier)

    print("%s  %d photos, %.1f Mo"
          % (archive, len(LOT), os.path.getsize(archive) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
