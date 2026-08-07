#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Registre des pages du site : une entree par URL.

C'est ici que se decident l'arborescence, les titres, les descriptions et
la place de chaque page dans le menu. Le contenu, lui, vit dans pages/.

Champs :
  slug        chemin de l'URL sans langue ni slash ("" = accueil,
              "guide/velo" = /guide/velo/)
  fichier     fragment de contenu dans pages/
  bilingue    True si une version anglaise existe. Sinon la page n'est
              generee qu'en francais et ne declare aucun hreflang alterne
              (annoncer une traduction inexistante casse le cluster).
  menu        libelle dans le menu principal, ou None
  fil         libelle dans le fil d'Ariane
  parent      slug du parent pour le fil d'Ariane
  jsonld      "logement" | "article" | "contact" | None
  titre / description / h1  par langue
"""

DOMAINE = "https://lebalcondaure.fr"

# --------------------------------------------------------------------------

PAGES = [
    # ---------------------------------------------------------------- socle
    {
        "slug": "",
        "fichier": "accueil.html",
        "bilingue": True,
        "menu": None,
        "fil": {"fr": "Accueil", "en": "Home"},
        "parent": None,
        "jsonld": "logement",
        "fr": {
            "titre": "Studio à louer à Saint-Lary-Soulan, 200 m des pistes",
            "description": "Studio 27 m² avec balcon vue montagne à Saint-Lary-Soulan, vallée d'Aure, à 200 m des "
                           "remontées. Sauna, jacuzzi, thermes à 150 m. Location en direct.",
            "og_titre": "Le Balcon d'Aure — studio à Saint-Lary-Soulan, 200 m des pistes",
        },
        "en": {
            "titre": "Ski studio to rent in Saint-Lary-Soulan, Pyrenees",
            "description": "27 m² studio flat with mountain-view balcony in Saint-Lary-Soulan, 200 m from "
                           "the ski lifts. Sauna, jacuzzi, thermal baths 150 m away. Book direct, no fees.",
            "og_titre": "Le Balcon d'Aure — studio flat in Saint-Lary-Soulan",
        },
    },
    {
        "slug": "studio",
        "fichier": "studio.html",
        "bilingue": True,
        "menu": {"fr": "Le studio", "en": "The flat"},
        "fil": {"fr": "Le studio", "en": "The flat"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Studio 27 m² en vallée d'Aure, balcon et 3 couchages",
            "description": "Visite du studio en vallée d'Aure : séjour, cuisine équipée, salle d'eau, "
                           "balcon de 9 m² vue montagne. Couchages pour 3, premier étage, résidence Royal Milan.",
            "og_titre": "Le studio en détail — 27 m² et un balcon sur les sommets",
        },
        "en": {
            "titre": "The flat: 27 m², 9 m² balcony, sleeps 3 | Le Balcon d'Aure",
            "description": "A detailed tour of the studio: living area, fitted kitchenette, shower room and "
                           "a 9 m² mountain-view balcony. Sleeps 3, first floor, Royal Milan residence.",
            "og_titre": "The flat in detail — 27 m² and a balcony facing the peaks",
        },
    },
    {
        "slug": "residence-royal-milan",
        "fichier": "residence.html",
        "bilingue": True,
        "menu": {"fr": "La résidence", "en": "The residence"},
        "fil": {"fr": "La résidence", "en": "The residence"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Résidence Royal Milan, vallée d'Aure : sauna, jacuzzi",
            "description": "La résidence Royal Milan en vallée d'Aure : sauna et jacuzzi en accès libre, "
                           "piscine chauffée l'été, salle de sport, billard et casier à skis.",
            "og_titre": "La résidence Royal Milan, ses espaces communs et son bien-être",
        },
        "en": {
            "titre": "Royal Milan residence, Saint-Lary: sauna and jacuzzi",
            "description": "The Royal Milan residence in Saint-Lary-Soulan: free sauna and jacuzzi, heated "
                           "outdoor pool in summer, fitness room, billiards and ski locker.",
            "og_titre": "The Royal Milan residence and its shared spaces",
        },
    },
    {
        "slug": "tarifs-disponibilites",
        "fichier": "tarifs.html",
        "bilingue": True,
        "menu": {"fr": "Tarifs & dispos", "en": "Rates & dates"},
        "fil": {"fr": "Tarifs et disponibilités", "en": "Rates and availability"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Tarifs et disponibilités — studio en vallée d'Aure",
            "description": "De 300 € à 700 € la semaine en vallée d'Aure, en direct et sans commission. "
                           "Calendrier des disponibilités, ménage, dépôt de garantie et conditions.",
            "og_titre": "Tarifs et calendrier — location en direct, sans commission",
        },
        "en": {
            "titre": "Rates and availability, Saint-Lary studio | Le Balcon d'Aure",
            "description": "From €300 to €700 per week depending on the season, booked directly with no agency "
                           "fee. Live availability calendar, cleaning, deposit and booking conditions.",
            "og_titre": "Rates and calendar — booked directly, no commission",
        },
    },
    # ------------------------------------------------------------- saisons
    {
        "slug": "hiver",
        "fichier": "hiver.html",
        "bilingue": True,
        "menu": {"fr": "Hiver", "en": "Winter"},
        "fil": {"fr": "Séjour en hiver", "en": "Winter stay"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Location au ski à Saint-Lary, 200 m des remontées",
            "description": "Studio en vallée d'Aure, à 200 m du télécabine. 100 km de pistes sur le Pla "
                           "d'Adet, Espiaube et le Vallon du Portet. Casier à skis, sauna et jacuzzi.",
            "og_titre": "Séjour au ski à Saint-Lary — 200 m des remontées",
        },
        "en": {
            "titre": "Ski rental in Saint-Lary, 200 m from the lifts",
            "description": "A studio 200 m from the cable car, skis on your shoulder. 100 km of runs across "
                           "Pla d'Adet, Espiaube and Vallon du Portet. Ski locker, sauna and jacuzzi.",
            "og_titre": "Ski holidays in Saint-Lary — 200 m from the lifts",
        },
    },
    {
        "slug": "ete",
        "fichier": "ete.html",
        "bilingue": True,
        "menu": {"fr": "Été", "en": "Summer"},
        "fil": {"fr": "Séjour en été", "en": "Summer stay"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Location été vallée d'Aure : randonnée, lacs, Saint-Lary",
            "description": "Studio en vallée d'Aure à 300 € la semaine l'été, au départ des lacs du Néouvielle. "
                           "Piscine chauffée à la résidence, thermes à 150 m.",
            "og_titre": "L'été à Saint-Lary — randonnée, lacs et piscine chauffée",
        },
        "en": {
            "titre": "Summer rental in the Aure valley: hiking and lakes",
            "description": "A studio from €300 a week in summer, at the foot of the Néouvielle lakes and Lac de "
                           "l'Oule. Heated outdoor pool at the residence, thermal baths 150 m away.",
            "og_titre": "Summer in Saint-Lary — hiking, lakes and a heated pool",
        },
    },
    {
        "slug": "cure-thermale",
        "fichier": "cure.html",
        "bilingue": False,
        "menu": {"fr": "Cure thermale"},
        "fil": {"fr": "Séjour en cure"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Cure thermale à Saint-Lary : studio à 150 m des bains",
            "description": "Studio calme à 150 m des thermes de Saint-Lary, pensé pour un séjour de cure : "
                           "tarif dégressif à la semaine, coin cuisine équipé, tout à pied, sans voiture.",
            "og_titre": "Un studio à 150 m des thermes pour votre cure",
        },
    },
    {
        "slug": "velo",
        "fichier": "velo.html",
        "bilingue": False,
        "menu": {"fr": "Vélo"},
        "fil": {"fr": "Séjour vélo"},
        "parent": "",
        "jsonld": "logement",
        "fr": {
            "titre": "Séjour vélo à Saint-Lary : Aspin, Peyresourde, Azet",
            "description": "Camp de base cycliste en vallée d'Aure : Pla d'Adet, Aspin, Peyresourde, Azet. "
                           "Local à vélos fermé, sauna et jacuzzi, 300 € la semaine.",
            "og_titre": "Les cols d'Aure à vélo, depuis le pied de la montée",
        },
    },
    # --------------------------------------------------------------- guides
    # Page d index de la rubrique. Sa presence rend le maillon « Guide de la
    # vallee » cliquable et pourvu d une URL : il repasse donc automatiquement
    # dans le fil d Ariane structure, la ou il en etait exclu faute de page.
    {
        "slug": "guide",
        "fichier": "guide.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Guide de la vallée"},
        "parent": "",
        "jsonld": None,
        "fr": {
            "titre": "Guide de la vallée d'Aure : ski, lacs, accès",
            "description": "Quatre guides pour préparer votre séjour en vallée d'Aure : les secteurs de ski, les "
                           "lacs du Néouvielle, les idées de mauvais temps et comment venir.",
            "og_titre": "Le guide de la vallée d'Aure, par des propriétaires",
        },
    },
    {
        "slug": "guide/skier-a-saint-lary",
        "fichier": "guide/skier.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Skier à Saint-Lary"},
        "parent": "guide",
        "jsonld": "article",
        "fr": {
            "titre": "Skier à Saint-Lary : les 3 secteurs, quel niveau où",
            "description": "Pla d'Adet, Espiaube, Vallon du Portet : à quoi ressemble chaque secteur, où aller "
                           "selon son niveau, comment monter depuis le village et où se garer.",
            "og_titre": "Skier à Saint-Lary : le guide des trois secteurs",
        },
    },
    {
        "slug": "guide/lacs-du-neouvielle",
        "fichier": "guide/neouvielle.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Les lacs du Néouvielle"},
        "parent": "guide",
        "jsonld": "article",
        "fr": {
            "titre": "Randonnée des lacs du Néouvielle, depuis Saint-Lary",
            "description": "Aumar, Aubert et la réserve naturelle du Néouvielle : accès depuis Saint-Lary, "
                           "navette, durée, difficulté et conseils pour partir au bon moment.",
            "og_titre": "Les lacs du Néouvielle, le grand classique des Pyrénées",
        },
    },
    {
        "slug": "guide/saint-lary-quand-il-pleut",
        "fichier": "guide/pluie.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Quand il pleut"},
        "parent": "guide",
        "jsonld": "article",
        "fr": {
            "titre": "Que faire à Saint-Lary quand il pleut ? 8 idées",
            "description": "Thermes Sensoria, Balnéa, gouffre d'Esparros, grottes de Gargas, Ludéo : ce qui "
                           "sauve une journée de mauvais temps dans la vallée d'Aure, à moins de 40 minutes.",
            "og_titre": "Saint-Lary sous la pluie : huit idées qui marchent",
        },
    },
    {
        "slug": "guide/venir-a-saint-lary",
        "fichier": "guide/venir.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Venir à Saint-Lary"},
        "parent": "guide",
        "jsonld": "article",
        "fr": {
            "titre": "Venir à Saint-Lary : train, voiture, navette",
            "description": "Comment rejoindre Saint-Lary depuis Toulouse, Tarbes ou Paris : gare de Lannemezan, "
                           "autoroute, temps de trajet, et comment se passer de voiture sur place.",
            "og_titre": "Venir à Saint-Lary, avec ou sans voiture",
        },
    },
    # ------------------------------------------------------------ services
    {
        "slug": "livre-d-or",
        "fichier": "livre-or.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Livre d'or"},
        "parent": "",
        "jsonld": None,
        "fr": {
            "titre": "Livre d'or : les avis de nos locataires | Le Balcon d'Aure",
            "description": "Les retours de ceux qui ont séjourné au Balcon d'Aure, publiés tels quels, "
                           "sur le studio comme sur les bons plans de la vallée d'Aure.",
            "og_titre": "Ils ont séjourné au Balcon d'Aure",
        },
    },
    {
        "slug": "contact",
        "fichier": "contact.html",
        "bilingue": True,
        "menu": None,
        "fil": {"fr": "Contact", "en": "Contact"},
        "parent": "",
        "jsonld": "contact",
        "fr": {
            "titre": "Nous contacter et réserver le studio | Le Balcon d'Aure",
            "description": "Karine et Romuald répondent eux-mêmes, par téléphone, WhatsApp ou formulaire. "
                           "Dites-nous vos dates, nous posons une option immédiatement.",
            "og_titre": "Contactez-nous — nous répondons nous-mêmes",
        },
        "en": {
            "titre": "Contact us and book the flat | Le Balcon d'Aure",
            "description": "Karine and Romuald answer in person, by phone, WhatsApp or contact form. "
                           "Tell us your dates and we will hold them straight away.",
            "og_titre": "Get in touch — we answer in person",
        },
    },
    {
        "slug": "mentions-legales",
        "fichier": "mentions.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Mentions légales"},
        "parent": "",
        "jsonld": None,
        "fr": {
            "titre": "Mentions légales et confidentialité | Le Balcon d'Aure",
            "description": "Éditeur du site, hébergement, traitement des données personnelles et conditions "
                           "de location du studio Le Balcon d'Aure à Saint-Lary-Soulan.",
            "og_titre": "Mentions légales",
        },
    },
]

# Rubrique sans page propre, presente uniquement dans le fil d'Ariane.
RUBRIQUES = {
    "guide": {"fr": "Guide de la vallée", "en": "Valley guide"},
}


def par_slug():
    return {p["slug"]: p for p in PAGES}


def url(slug, langue):
    """URL absolue d'une page."""
    base = DOMAINE + ("/en" if langue == "en" else "")
    return base + "/" + (slug + "/" if slug else "")


def chemin(slug, langue):
    """Chemin relatif du fichier a ecrire."""
    parts = ([] if langue == "fr" else ["en"]) + ([slug] if slug else [])
    return "/".join(parts + ["index.html"])
