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
            "titre": "Studio à Saint-Lary-Soulan, 200 m des remontées",
            "description": "Studio 27 m² avec balcon vue montagne à Saint-Lary-Soulan, vallée d'Aure, à 200 m des "
                           "remontées. Sauna, thermes à 150 m. Location en direct.",
            "og_titre": "Le Balcon d'Aure — studio à Saint-Lary-Soulan, 200 m des remontées",
        },
        "en": {
            "titre": "Ski studio to rent in Saint-Lary-Soulan, Pyrenees",
            "description": "27 m² studio flat with mountain-view balcony in Saint-Lary-Soulan, 200 m from "
                           "the ski lifts. Sauna, thermal baths 150 m away. Book direct, no fees.",
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
            "titre": "Résidence Royal Milan, vallée d'Aure : sauna et piscine",
            "description": "La résidence Royal Milan en vallée d'Aure : sauna en accès libre, "
                           "piscine chauffée l'été, salle de sport, billard et casier à skis.",
            "og_titre": "La résidence Royal Milan, ses espaces communs et son bien-être",
        },
        "en": {
            "titre": "Royal Milan residence, Saint-Lary: sauna and pool",
            "description": "The Royal Milan residence in Saint-Lary-Soulan: free sauna, heated "
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
            "description": "De 270 € à 700 € la semaine en vallée d'Aure, en direct et sans commission. "
                           "Calendrier des disponibilités, ménage, dépôt de garantie et conditions.",
            "og_titre": "Tarifs et calendrier — location en direct, sans commission",
        },
        "en": {
            "titre": "Rates and availability, Saint-Lary studio | Le Balcon d'Aure",
            "description": "From €270 to €700 per week depending on the season, booked directly with no agency "
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
                           "d'Adet, Espiaube et le Vallon du Portet. Casier à skis et sauna.",
            "og_titre": "Séjour au ski à Saint-Lary — 200 m des remontées",
        },
        "en": {
            "titre": "Ski rental in Saint-Lary, 200 m from the lifts",
            "description": "A studio 200 m from the cable car, skis on your shoulder. 100 km of runs across "
                           "Pla d'Adet, Espiaube and Vallon du Portet. Ski locker and sauna.",
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
            "description": "Studio en vallée d'Aure dès 300 € la semaine l'été, au départ des lacs du Néouvielle. "
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
                           "Le Tour y arrive au col du Portet le 22 juillet 2027. Local à vélos fermé et sauna.",
            "og_titre": "Les cols d'Aure à vélo, depuis le pied de la montée",
        },
    },
    {
        "slug": "bons-plans-vallee-d-aure",
        "fichier": "bons-plans.html",
        "bilingue": False,
        "menu": {"fr": "Bons plans"},
        "fil": {"fr": "Bons plans de la vallée"},
        "parent": "",
        "jsonld": None,
        "fr": {
            "titre": "Bons plans vallée d'Aure : où manger, que visiter",
            "description": "Nos adresses et celles de nos locataires à Saint-Lary-Soulan et dans la vallée "
                           "d'Aure : restaurants, activités, visites, marchés et producteurs.",
            "og_titre": "Les bons plans de la vallée d'Aure, testés et partagés",
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
        "faq": [
            ("Peut-on monter en voiture aux lacs d'Aumar et d'Aubert ?",
             "Oui, mais seulement avant 9 h 30 ou après 18 h, de juin à septembre. Entre ces deux "
             "heures, la route entre Orédon et Aubert est interdite à la montée aux véhicules à "
             "moteur : on se gare au parking d'Orédon, payant, et on monte en navette ou à pied."),
            ("Combien coûte la navette du Néouvielle ?",
             "7 € l'aller-retour, 4 € l'aller simple ou le retour simple, gratuit jusqu'à 6 ans. "
             "Les billets s'achètent au péage d'Orédon, et la descente seule se règle au chauffeur."),
            ("Combien de temps à pied entre Orédon et Aubert ?",
             "Une heure trente par le sentier des Laquettes. Le tour du lac d'Orédon demande aussi "
             "1 h 30, sans dénivelé notable."),
            ("Les chiens sont-ils admis dans la réserve du Néouvielle ?",
             "Non, même tenus en laisse. La garderie pour chiens du péage d'Orédon ne fonctionne "
             "plus depuis 2026 en raison de travaux sur le site."),
            ("Peut-on bivouaquer au bord des lacs du Néouvielle ?",
             "Le bivouac est toléré sur des emplacements délimités au bord des lacs d'Orédon et "
             "d'Aubert, installation après 19 h et démontage avant 9 h. Le camping est interdit, "
             "les feux strictement interdits, et la nuit en véhicule est interdite sur les parkings."),
            ("À quelle distance les lacs du Néouvielle sont-ils de Saint-Lary-Soulan ?",
             "Environ trois quarts d'heure de route par la D929, en passant par Fabian et "
             "Aragnouet. C'est une sortie à la journée depuis le village."),
        ],
        "fr": {
            "titre": "Lacs du Néouvielle : accès, navette, horaires et tarifs",
            "description": "La règle d'accès de juin à septembre, les horaires et tarifs de la navette "
                           "d'Orédon, le sentier des Laquettes, les règles de la réserve et les "
                           "contacts utiles. Vérifié sur les sources officielles.",
            "og_titre": "Lacs du Néouvielle : la règle d'accès que tout le monde rate",
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
    {
        "slug": "tour-de-france-2027-saint-lary",
        "fichier": "tour2027.html",
        "bilingue": False,
        "menu": None,
        "fil": {"fr": "Tour de France 2027"},
        "parent": "velo",
        "jsonld": "logement",
        "faq": [
            ("Quand le Tour de France passe-t-il à Saint-Lary-Soulan en 2027 ?",
             "Le jeudi 22 juillet 2027. La 18e étape part de Pau et arrive au col du Portet, "
             "au-dessus de Saint-Lary-Soulan, après 174 kilomètres et 5 400 mètres de dénivelé."),
            ("Quelle semaine faut-il réserver pour voir l'étape ?",
             "La semaine du samedi 17 au samedi 24 juillet 2027, qui contient le jour de l'étape. "
             "Les séjours vont du samedi au samedi pendant les vacances scolaires."),
            ("Peut-on monter au col du Portet le jour de l'étape ?",
             "La route est fermée à la circulation plusieurs heures avant le passage de la course, "
             "et l'accès au sommet se fait à pied ou à vélo, très tôt le matin."),
            ("Faut-il une voiture pendant la semaine du Tour à Saint-Lary ?",
             "Non. La résidence a son parking, et les commerces, les thermes et les remontées "
             "mécaniques sont accessibles à pied depuis le studio."),
            ("Combien coûte la semaine du Tour de France au Balcon d'Aure ?",
             "950 € la semaine pour trois personnes, en direct et sans commission. Le ménage est "
             "en option à 50 €, la taxe de séjour s'ajoute."),
            ("Le studio convient-il à des cyclistes ?",
             "Oui. La résidence dispose d'un local fermé pour les vélos, et les cols d'Aspin, "
             "d'Azet, de Peyresourde, la Hourquette d'Ancizan et la montée du Pla d'Adet partent "
             "du village."),
        ],
        "fr": {
            "titre": "Tour de France 2027 à Saint-Lary : louer la semaine",
            "description": "Jeudi 22 juillet 2027, l'étape reine Pau — col du Portet arrive au-dessus de "
                           "Saint-Lary. Studio pour 3 au village, semaine du 17 au 24 juillet, en direct.",
            "og_titre": "Tour de France 2027 au col du Portet — se loger à Saint-Lary",
        },
    },
    {
        # Livret d'accueil des locataires : accessible uniquement par le QR code
        # affiche dans le studio. "prive" la sort du sitemap et lui ajoute un
        # noindex. Aucune autre page du site ne doit pointer vers elle, sans quoi
        # Google la decouvrirait malgre le noindex et la traiterait comme une
        # page mince, au detriment du reste du site.
        "slug": "livret",
        "fichier": "livret.html",
        "bilingue": False,
        "menu": None,
        "prive": True,
        "fil": {"fr": "Livret d'accueil"},
        "parent": "",
        "jsonld": None,
        "fr": {
            "titre": "Livret d'accueil | Le Balcon d'Aure",
            "description": "Informations pratiques du séjour : arrivée, équipements du studio, "
                           "services de la résidence, consignes de départ.",
            "og_titre": "Livret d'accueil",
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
