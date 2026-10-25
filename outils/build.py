#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere le site publie.

    python outils/build.py

Assemble, pour chaque entree de outils/pages.py :
    gabarits/base.html  +  pages/<fragment>  ->  <slug>/index.html

Chaque page existe en francais, et en anglais seulement si elle est
declaree bilingue. Une page monolingue ne declare aucun hreflang alterne :
annoncer une traduction inexistante fait ignorer tout le cluster par Google.

Les fragments portent data-fr / data-en sur les elements propres a une
langue ; le build retire ceux de l'autre langue.

Ne jamais modifier les fichiers generes : ils sont ecrases a chaque build.
"""

import datetime
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages as registre  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GABARIT = os.path.join(RACINE, "gabarits", "base.html")
FRAGMENTS = os.path.join(RACINE, "pages")
GUIDE_JSON = os.path.join(RACINE, "guide.json")
AGENDA_JSON = os.path.join(RACINE, "agenda.json")
RESERVATIONS = os.path.join(RACINE, "reservations.json")

DOMAINE = registre.DOMAINE

VIDES = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

LOCALES = {"fr": "fr_FR", "en": "en_GB", "es": "es_ES"}

LIBELLES = {
    "fr": {
        "reserver": "Réserver",
        "avis_vide": "Votre avis inaugurera ce livre d’or : un message suffit.",
        "reduction": "Réduction avec notre code",
        "fil": "Fil d’Ariane",
        "pied_sejours": "Séjours",
        "pied_lieu": "Le logement",
        "pied_guide": "Guide de la vallée",
        "pied_infos": "Informations",
    },
    "en": {
        "reserver": "Book",
        "avis_vide": "Your review will open this guest book: just send us a message.",
        "reduction": "Discount with our code",
        "fil": "Breadcrumb",
        "pied_sejours": "Stays",
        "pied_lieu": "The property",
        "pied_guide": "Valley guide",
        "pied_infos": "Information",
    },
    "es": {
        "reserver": "Reservar",
        "avis_vide": "Tu opinión estrenará este libro de visitas: basta con un mensaje.",
        "reduction": "Descuento con nuestro código",
        "fil": "Ruta de navegación",
        "pied_sejours": "Estancias",
        "pied_lieu": "El alojamiento",
        "pied_guide": "Guía del valle",
        "pied_infos": "Información",
    },
}


# --------------------------------------------------------------------------
# Retrait des elements d'une langue
# --------------------------------------------------------------------------

def _masquer_scripts(doc):
    gardes = []

    def prendre(m):
        gardes.append(m.group(2))
        return "%s\x00%d\x00%s" % (m.group(1), len(gardes) - 1, m.group(3))

    doc = re.sub(r"(<script\b[^>]*>)(.*?)(</script>)", prendre, doc, flags=re.S | re.I)
    return doc, gardes


def _rendre_scripts(doc, gardes):
    return re.sub(r"\x00(\d+)\x00", lambda m: gardes[int(m.group(1))], doc)


BALISE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>")


def retirer(doc, attribut):
    """Supprime tout element portant `attribut` et son sous-arbre."""
    doc, gardes = _masquer_scripts(doc)
    presence = re.compile(r"(?:^|\s)%s(?=[\s=>/]|$)" % re.escape(attribut))

    sortie, position = [], 0
    while True:
        m = BALISE.search(doc, position)
        if not m:
            sortie.append(doc[position:])
            break
        fermante, nom, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if fermante or not presence.search(attrs):
            sortie.append(doc[position:m.end()])
            position = m.end()
            continue
        sortie.append(doc[position:m.start()])
        if nom in VIDES or attrs.rstrip().endswith("/"):
            position = m.end()
            continue
        profondeur, curseur = 1, m.end()
        while profondeur:
            suivante = BALISE.search(doc, curseur)
            if not suivante:
                raise ValueError("balise <%s> non fermee (attribut %s)" % (nom, attribut))
            if suivante.group(2).lower() == nom:
                if suivante.group(1):
                    profondeur -= 1
                elif not (nom in VIDES or suivante.group(3).rstrip().endswith("/")):
                    profondeur += 1
            curseur = suivante.end()
        position = curseur
    return _rendre_scripts("".join(sortie), gardes)


EXTERNE = ("/", "http:", "https:", "//", "data:")


def srcset_absolu(valeur):
    """Passe chaque candidate d'un srcset en chemin racine-absolu.

    Decoupage explicite plutot qu'une expression reguliere : une regex sur
    « virgule suivie d'espaces optionnels » inserait un slash devant l'espace
    quand le chemin etait deja absolu, produisant « 500w,/ /images/... ».
    Le navigateur jetait alors toutes les candidates sauf la premiere et
    affichait la vignette 500 px en pleine largeur.
    """
    candidates = []
    for brut in valeur.split(","):
        brut = brut.strip()
        if not brut:
            continue
        morceaux = brut.split(None, 1)
        url = morceaux[0]
        descripteur = " " + morceaux[1] if len(morceaux) > 1 else ""
        if not url.startswith(EXTERNE):
            url = "/" + url
        candidates.append(url + descripteur)
    return ", ".join(candidates)


def att(texte):
    """Echappe pour un attribut, sans toucher a l'apostrophe."""
    return (str(texte).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def e(texte):
    return html.escape(str(texte), quote=True)


# --------------------------------------------------------------------------
# En-tete
# --------------------------------------------------------------------------

def metas(page, langue):
    infos = page[langue]
    url = registre.url(page["slug"], langue)
    image = DOMAINE + "/images/opt/og-image.jpg"

    lignes = [
        "<title>%s</title>" % att(infos["titre"]),
        '<meta name="description" content="%s">' % att(infos["description"]),
        '<link rel="canonical" href="%s">' % url,
    ]

    # Page reservee aux locataires (livret d'accueil) : hors index, et surtout
    # nofollow pour qu'elle ne fasse pas decouvrir a Google des URL par ce biais.
    if page.get("prive"):
        lignes.append('<meta name="robots" content="noindex, nofollow">')

    # hreflang uniquement si la traduction existe reellement
    disponibles = registre.langues(page)
    if len(disponibles) > 1:
        lignes += ['<link rel="alternate" hreflang="%s" href="%s">'
                   % (l, registre.url(page["slug"], l)) for l in disponibles]
        lignes.append('<link rel="alternate" hreflang="x-default" href="%s">'
                      % registre.url(page["slug"], "fr"))

    lignes += [
        '<meta property="og:type" content="%s">' % ("article" if page["jsonld"] == "article" else "website"),
        '<meta property="og:site_name" content="Le Balcon d\'Aure">',
        '<meta property="og:title" content="%s">' % att(infos.get("og_titre", infos["titre"])),
        '<meta property="og:description" content="%s">' % att(infos["description"]),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s">' % image,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:locale" content="%s">' % LOCALES[langue],
    ]
    lignes += ['<meta property="og:locale:alternate" content="%s">' % LOCALES[l]
               for l in disponibles if l != langue]
    lignes += [
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="%s">' % image,
    ]
    return "\n".join(lignes)


def plus_grande_variante(nom):
    """Chemin de la plus large variante WebP disponible pour une photo.

    Toutes n'ont pas la meme definition : un recadrage serre plafonne a sa
    largeur native, et coder 1200 en dur pointait alors vers un fichier
    inexistant."""
    import glob as _glob
    motif = os.path.join(RACINE, "images", "opt", nom + "-*.webp")
    largeurs = []
    for chemin in _glob.glob(motif):
        reste = os.path.basename(chemin)[len(nom) + 1:-5]
        if reste.isdigit():
            largeurs.append(int(reste))
    if not largeurs:
        raise SystemExit("Photo absente de images/opt : %s" % nom)
    return "/images/opt/%s-%d.webp" % (nom, max(largeurs))


def bloc_logement(page, langue, avis):
    photos = ["vue-montagne", "sejour-salon", "canape-vue", "cuisine-plan-serre",
              "terrasse-transats"]
    if langue == "fr":
        description = ("Studio de 27 m² avec balcon de 9 m² vue montagne, au premier étage de la "
                       "résidence Royal Milan à Saint-Lary-Soulan. 200 m des remontées mécaniques, "
                       "thermes Sensoria à 150 m, sauna en accès libre, piscine chauffée "
                       "l'été. Location en direct auprès des propriétaires, sans commission.")
        animaux = "Chiens acceptés l'été uniquement, sous conditions ; pas d'animaux en hiver"
        logement = "Studio avec balcon, couchages dans la pièce de vie"
        equipements = ["Balcon de 9 m² vue montagne", "Sauna (résidence)",
                       "Piscine extérieure chauffée l'été", "Salle de sport", "Lave-vaisselle",
                       "Casier à skis", "Parking", "Wifi"]
    else:
        description = ("27 m² studio flat with a 9 m² mountain-view balcony, on the first floor of the "
                       "Royal Milan residence in Saint-Lary-Soulan, French Pyrenees. 200 m from the ski "
                       "lifts, Sensoria thermal baths 150 m away, free access to the sauna, "
                       "heated outdoor pool in summer. Booked directly with the owners, no agency fees.")
        animaux = "Dogs welcome in summer only, under conditions; no pets in winter"
        logement = "Studio flat with balcony, beds in the living area"
        equipements = ["9 m² mountain-view balcony", "Sauna (residence)",
                       "Heated outdoor pool in summer", "Fitness room", "Dishwasher",
                       "Ski locker", "Car park", "Wi-Fi"]

    # LodgingBusiness plutot que VacationRental : ce dernier n est exploite que
    # par le programme partenaire Google Vacation Rentals, reserve aux societes
    # de gestion locative disposant d un acces Hotel Center. Un particulier n y
    # sera jamais eligible, et Search Console signalait donc en permanence sept
    # champs « manquants » impossibles a satisfaire utilement. LodgingBusiness
    # decrit le meme bien, accepte les memes proprietes, et n a pas de rapport
    # dedie susceptible de rester rouge.
    ld = {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "@id": DOMAINE + "/#logement",
        "name": "Le Balcon d'Aure",
        "url": registre.url(page["slug"], langue),
        "inLanguage": langue,
        "description": description,
        "image": [DOMAINE + plus_grande_variante(p) for p in photos],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Résidence Royal Milan, chemin de Vielle-Aure",
            "addressLocality": "Saint-Lary-Soulan",
            "postalCode": "65170",
            "addressRegion": "Hautes-Pyrénées",
            "addressCountry": "FR",
        },
        "hasMap": ("https://www.google.com/maps/search/?api=1&query="
                   "R%C3%A9sidence+Royal+Milan%2C+chemin+de+Vielle-Aure%2C+65170+Saint-Lary-Soulan"),
        "telephone": ["+33642845542", "+33627352328"],
        "numberOfRooms": 1,
        "petsAllowed": animaux,
        "priceRange": "270 € – 700 €",
        "currenciesAccepted": "EUR",
        # Classement prefectoral du meuble de tourisme : Google s en sert pour
        # qualifier l hebergement, au meme titre que les etoiles d un hotel.
        "starRating": {"@type": "Rating", "ratingValue": 3, "bestRating": 5},
        # Label propre a la station, distinct du classement prefectoral.
        "award": "Label Qualité Confort Hébergement de Saint-Lary — 4 diamants sur 5, niveau Confort +",
        "checkinTime": "15:00:00",
        "checkoutTime": "10:00:00",
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in equipements
        ],
        "containsPlace": {
            "@type": "Accommodation",
            "name": logement,
            "floorSize": {"@type": "QuantitativeValue", "value": 27, "unitCode": "MTK"},
            # "value" en plus de "maxValue" : Google signale le premier comme
            # manquant lorsque seul le second est fourni.
            "occupancy": {"@type": "QuantitativeValue", "value": 3, "maxValue": 3},
            "numberOfBedrooms": 0,
            "numberOfBathroomsTotal": 1,
        },
        "makesOffer": {
            "@type": "Offer",
            "priceCurrency": "EUR",
            "priceSpecification": {
                "@type": "UnitPriceSpecification", "priceCurrency": "EUR",
                "minPrice": 300, "maxPrice": 700, "unitCode": "WEE",
            },
        },
    }

    notes = [v["note"] for v in avis if v.get("note")]
    if notes:
        ld["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(notes) / len(notes), 1),
            "reviewCount": len(notes), "bestRating": 5, "worstRating": 1,
        }
    if avis:
        ld["review"] = [
            dict(
                {"@type": "Review", "reviewBody": v["texte"],
                 "author": {"@type": "Person", "name": v.get("auteur") or "Voyageur"}},
                **({"datePublished": v["date"]}
                   if re.match(r"^\d{4}-\d{2}(-\d{2})?$", str(v.get("date", ""))) else {}),
                **({"reviewRating": {"@type": "Rating", "ratingValue": v["note"],
                                     "bestRating": 5, "worstRating": 1}} if v.get("note") else {})
            ) for v in avis
        ]
    return ld


def bloc_article(page, langue):
    infos = page[langue]
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": infos.get("og_titre", infos["titre"]),
        "description": infos["description"],
        "inLanguage": langue,
        "mainEntityOfPage": registre.url(page["slug"], langue),
        "image": DOMAINE + "/images/opt/og-image.jpg",
        "author": {"@type": "Person", "name": "Karine et Romuald Lambert"},
        "publisher": {"@type": "Organization", "name": "Le Balcon d'Aure",
                      "url": DOMAINE + "/"},
        "about": {"@type": "Place", "name": "Saint-Lary-Soulan",
                  "address": {"@type": "PostalAddress", "addressLocality": "Saint-Lary-Soulan",
                              "postalCode": "65170", "addressCountry": "FR"}},
    }


def bloc_fil(page, langue):
    """BreadcrumbList : reconstruit la chaine des parents."""
    chaine, courant = [], page
    vus = set()
    while courant is not None:
        chaine.insert(0, courant)
        parent = courant.get("parent")
        if parent is None or parent in vus:
            break
        vus.add(parent)
        courant = registre.par_slug().get(parent)
        if courant is None:
            # rubrique sans page propre (ex. "guide")
            rub = registre.RUBRIQUES.get(parent)
            if rub:
                chaine.insert(0, {"slug": parent, "fil": rub, "virtuel": True})
            courant = registre.par_slug().get("")
    if len(chaine) < 2:
        return None
    elements = []
    for i, p in enumerate(chaine, start=1):
        item = {"@type": "ListItem", "position": i, "name": p["fil"].get(langue, p["fil"]["fr"])}
        if p.get("virtuel"):
            # Marqueur interne : ce maillon reste dans le fil affiche, mais
            # sera retire du JSON-LD par fil_structure().
            item["_sans_page"] = True
        else:
            item["item"] = registre.url(p["slug"], langue)
        elements.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}


def fil_structure(fil):
    """Version du fil destinee a Google.

    Les maillons sans page propre (rubrique "guide") n ont pas d URL. Google
    refuse un ListItem depourvu du champ "item" (« Champ item manquant »), et
    les lier a /guide/ pointerait vers une 404. On les retire donc du JSON-LD
    en renumerotant les positions, alors qu ils restent visibles a l ecran.
    """
    if not fil:
        return None
    reels = []
    for item in fil["itemListElement"]:
        if item.get("_sans_page"):
            continue
        propre = {c: v for c, v in item.items() if not c.startswith("_")}
        propre["position"] = len(reels) + 1
        reels.append(propre)
    if len(reels) < 2:
        return None
    return {**fil, "itemListElement": reels}


def donnees_structurees(page, langue, avis):
    blocs = []
    if page["jsonld"] == "logement":
        blocs.append(bloc_logement(page, langue, avis))
    elif page["jsonld"] == "article":
        blocs.append(bloc_article(page, langue))
    elif page["jsonld"] == "contact":
        blocs.append({"@context": "https://schema.org", "@type": "ContactPage",
                      "url": registre.url(page["slug"], langue), "inLanguage": langue,
                      "about": {"@id": DOMAINE + "/#logement"}})
    # Une page peut declarer ses questions : Google les affiche parfois
    # directement dans ses resultats, ce qui vaut tous les mots-cles.
    if page.get("faq"):
        blocs.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "inLanguage": langue,
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": r}}
                for q, r in page["faq"]
            ],
        })

    # La page d'agenda declare ses dates : c'est ce qui permet a Google de
    # les faire remonter dans ses resultats d'evenements.
    if page.get("evenements"):
        blocs.extend(evenements_structures())

    fil = fil_structure(bloc_fil(page, langue))
    if fil:
        blocs.append(fil)
    return "\n".join(
        '<script type="application/ld+json">\n%s\n</script>'
        % json.dumps(b, ensure_ascii=False, indent=2) for b in blocs
    )


# --------------------------------------------------------------------------
# Navigation, fil d'Ariane, pied de page
# --------------------------------------------------------------------------

def lien_menu(page, langue):
    """Une page non traduite reste en francais, quelle que soit la langue lue."""
    if langue not in registre.langues(page):
        langue = "fr"
    return registre.url(page["slug"], langue).replace(DOMAINE, "")


def navigation(page, langue):
    lib = LIBELLES[langue]
    accueil = "/" if langue == "fr" else "/%s/" % langue
    liens = []
    for p in registre.PAGES:
        if not p["menu"]:
            continue
        # Une page pas encore traduite reste au menu, en francais : un menu
        # a trois entrees sur dix donnerait l'impression d'un site vide.
        traduite = langue in registre.langues(p)
        libelle = p["menu"].get(langue) or p["menu"]["fr"]
        if not traduite:
            libelle = p["menu"]["fr"]
        classe = ' class="actif" aria-current="page"' if p["slug"] == page["slug"] else ""
        drapeau = "" if traduite else ' hreflang="fr" lang="fr"'
        liens.append('<a href="%s"%s%s>%s</a>'
                     % (lien_menu(p, langue), classe, drapeau, e(libelle)))

    contact = registre.par_slug()["contact"]
    return (
        '<nav class="nav" id="nav">\n'
        '  <a class="nav-marque" href="%s">Le Balcon d\'Aure</a>\n'
        '  <div class="nav-liens">%s</div>\n'
        '  <div class="nav-droite">\n'
        "    <!--LANGUES-->\n"
        '    <a class="pastille pastille-pleine" href="%s">%s</a>\n'
        "  </div>\n"
        "</nav>" % (accueil, "".join(liens), lien_menu(contact, langue), e(lib["reserver"]))
    )


def selecteur_langue(page, langue):
    """Absent des pages qui n'existent que dans une langue."""
    disponibles = registre.langues(page)
    if len(disponibles) < 2:
        return ""
    liens = []
    for l in disponibles:
        adresse = registre.url(page["slug"], l).replace(DOMAINE, "")
        actif = ' class="actif" aria-current="page"' if l == langue else ""
        liens.append('<a%s href="%s" hreflang="%s" lang="%s">%s</a>'
                     % (actif, adresse, l, l, l.upper()))
    return '<div class="langues">%s</div>' % "".join(liens)


def fil_ariane(page, langue):
    fil = bloc_fil(page, langue)
    if not fil:
        return ""
    morceaux = []
    for item in fil["itemListElement"]:
        nom = e(item["name"])
        if "item" in item and item is not fil["itemListElement"][-1]:
            morceaux.append('<a href="%s">%s</a>' % (item["item"].replace(DOMAINE, ""), nom))
        else:
            morceaux.append("<span>%s</span>" % nom)
    return ('<nav class="fil-ariane" aria-label="%s"><div class="enveloppe">%s</div></nav>'
            % (LIBELLES[langue]["fil"], "".join(morceaux)))


def pied_liens(langue):
    lib = LIBELLES[langue]
    slugs = registre.par_slug()

    def groupe(titre, cles):
        items = []
        for cle in cles:
            p = slugs.get(cle)
            if not p:
                continue
            libelle = p["fil"].get(langue) or p["fil"]["fr"]
            # Depuis l'anglais, une page qui n'existe qu'en francais est
            # signalee comme telle : on garde le lien, mais le visiteur sait
            # ou il va.
            if langue != "fr" and langue not in registre.langues(p):
                items.append('<li><a href="%s" hreflang="fr" lang="fr">%s</a>'
                             '<span class="pied-langue"> (en français)</span></li>'
                             % (lien_menu(p, langue), e(libelle)))
                continue
            items.append('<li><a href="%s">%s</a></li>' % (lien_menu(p, langue), e(libelle)))
        if not items:
            return ""
        return "<div><p class=\"sur-titre\">%s</p><ul>%s</ul></div>" % (e(titre), "".join(items))

    colonnes = [
        groupe(lib["pied_lieu"], ["studio", "residence-royal-milan", "tarifs-disponibilites"]),
        groupe(lib["pied_sejours"], ["hiver", "ete", "cure-thermale", "velo"]),
        groupe(lib["pied_guide"], ["guide/skier-a-saint-lary", "guide/lacs-du-neouvielle",
                                   "guide/saint-lary-quand-il-pleut", "guide/venir-a-saint-lary"]),
        groupe(lib["pied_infos"], ["livre-d-or", "contact", "mentions-legales"]),
    ]
    return '<div class="pied-liens">%s</div>' % "".join(c for c in colonnes if c)


# --------------------------------------------------------------------------
# Pre-rendu du contenu injecte en JavaScript
# --------------------------------------------------------------------------

def carte_bonplan(plan, langue):
    """Une fiche du carnet. Chaque champ retombe sur le francais a defaut :
    les sites de la vallee ne sont pas tous traduits, et mieux vaut une
    adresse juste en francais qu'une adresse absente."""
    def champ(base):
        return plan.get("%s_%s" % (base, langue)) or plan.get(base + "_fr") or plan.get(base)

    url = champ("url")
    nom = champ("nom")
    desc = champ("desc")
    mot = (plan.get("commentaire") if langue == "fr"
           else (plan.get("commentaire_" + langue) or plan.get("commentaire_en")
                 or plan.get("commentaire")))
    out = ['<a class="activite" target="_blank" rel="noopener" href="%s"><b>%s</b>' % (e(url), e(nom))]
    if desc:
        out.append("<span>%s</span>" % e(desc))
    if plan.get("reduction"):
        out.append('<span class="activite-reduc">%s</span>' % e(LIBELLES[langue]["reduction"]))
    if mot:
        out.append('<span class="activite-mot">« %s » — Karine &amp; Romuald</span>' % e(mot))
    out.append("</a>")
    return "".join(out)


def carte_avis(v):
    out = ['<div class="carte-avis">']
    if v.get("note"):
        out.append('<p class="avis-etoiles">%s</p>' % ("★" * max(1, min(5, int(v["note"])))))
    out.append("<blockquote>« %s »</blockquote>" % e(v["texte"]))
    pied = e(v.get("auteur", "")) + (" · " + e(v["date"]) if v.get("date") else "")
    out.append('<div class="avis-pied"><span class="avis-auteur">%s</span>' % pied)
    if v.get("cible"):
        out.append('<span class="avis-cible">%s</span>' % e(v["cible"]))
    out.append("</div></div>")
    return "".join(out)


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def agenda_a_venir():
    """Les evenements encore a venir, du plus proche au plus lointain.

    Un evenement reste affiche jusqu'au lendemain de sa fin : une fete du
    samedi doit encore se lire le samedi soir."""
    donnees = json.load(open(AGENDA_JSON, encoding="utf-8"))
    aujourdhui = datetime.date.today().isoformat()
    a_venir = [e for e in donnees.get("evenements", [])
               if (e.get("fin") or e["debut"]) >= aujourdhui]
    a_venir.sort(key=lambda e: e["debut"])
    return donnees.get("verifie", ""), a_venir


def date_lisible(debut, fin):
    d = datetime.date.fromisoformat(debut)
    if not fin or fin == debut:
        return "%d %s %d" % (d.day, MOIS[d.month - 1], d.year)
    f = datetime.date.fromisoformat(fin)
    if (d.month, d.year) == (f.month, f.year):
        return "%d – %d %s %d" % (d.day, f.day, MOIS[d.month - 1], d.year)
    return "%d %s – %d %s %d" % (d.day, MOIS[d.month - 1], f.day, MOIS[f.month - 1], f.year)


def carte_evenement(ev):
    d = datetime.date.fromisoformat(ev["debut"])
    sur = "À %d km" % ev["km"] if ev.get("km") else "Au village"
    lignes = ['<article class="evenement">',
              '<div class="evenement-date"><b>%d</b><span>%s</span></div>'
              % (d.day, e(MOIS[d.month - 1][:4] + ("." if len(MOIS[d.month - 1]) > 4 else ""))),
              '<div class="evenement-corps">',
              '<h3>%s</h3>' % e(ev["nom"]),
              '<p class="evenement-ou">%s · %s · %s</p>'
              % (e(date_lisible(ev["debut"], ev.get("fin"))), e(ev["lieu"]), e(sur)),
              '<p>%s</p>' % e(ev["resume"])]
    if ev.get("statut") != "confirme":
        lignes.append('<p class="evenement-reserve">Date à confirmer auprès de l\'organisateur</p>')
    if ev.get("url"):
        externe = ev["url"].startswith("http")
        lignes.append('<a class="evenement-lien" href="%s"%s>En savoir plus →</a>'
                      % (e(ev["url"]), ' target="_blank" rel="noopener"' if externe else ""))
    lignes += ["</div>", "</article>"]
    return "".join(lignes)


def bloc_agenda():
    verifie, evenements = agenda_a_venir()
    if not evenements:
        return '<p class="avis-vide">Agenda en cours de mise à jour.</p>'
    out, mois_courant = [], None
    for ev in evenements:
        d = datetime.date.fromisoformat(ev["debut"])
        if (d.year, d.month) != mois_courant:
            if mois_courant:
                out.append("</div>")
            mois_courant = (d.year, d.month)
            out.append('<p class="agenda-mois">%s %d</p><div class="agenda-mois-liste">'
                       % (e(MOIS[d.month - 1].capitalize()), d.year))
        out.append(carte_evenement(ev))
    out.append("</div>")
    if verifie:
        jour = datetime.date.fromisoformat(verifie)
        out.append('<p class="cal-note">Agenda vérifié le %d %s %d. '
                   'Une date vous semble fausse ou il en manque une ? Écrivez-nous, '
                   'nous corrigeons.</p>' % (jour.day, MOIS[jour.month - 1], jour.year))
    return "".join(out)


def evenements_structures():
    """Balisage Event des seules dates confirmees : annoncer a Google une
    date qu'on n'a pas verifiee se paie en confiance."""
    _, evenements = agenda_a_venir()
    blocs = []
    for ev in evenements:
        if ev.get("statut") != "confirme":
            continue
        bloc = {"@context": "https://schema.org", "@type": "Event",
                "name": ev["nom"], "startDate": ev["debut"],
                "eventStatus": "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "description": ev["resume"],
                "location": {"@type": "Place", "name": ev["lieu"],
                             "address": {"@type": "PostalAddress",
                                         "addressLocality": ev["lieu"],
                                         "addressRegion": "Hautes-Pyrénées",
                                         "addressCountry": "FR"}}}
        if ev.get("fin"):
            bloc["endDate"] = ev["fin"]
        if ev.get("url"):
            bloc["url"] = ev["url"] if ev["url"].startswith("http") else DOMAINE + ev["url"]
        blocs.append(bloc)
    return blocs


def prerendre(doc, langue, guide):
    plans = [p for p in guide.get("bonsplans", [])
             if p.get("visible") is not False and p.get("url_fr")]

    def remplir(m):
        saison, categorie = m.group(1), m.group(2)
        # "tout" ignore le filtre saisonnier : la page des bons plans presente
        # l ensemble du carnet, regroupe par categorie plutot que par saison.
        choisis = [p for p in plans
                   if saison == "tout" or p.get("saison") in (saison, "toute")]
        if categorie:
            choisis = [p for p in choisis if p.get("categorie") == categorie]
        if saison == "tout":
            # Certaines adresses existent en deux fiches, hiver et ete, qui ne
            # different que par le lien saisonnier de l office de tourisme.
            # Sur une page toutes saisons, on n en garde qu une par nom.
            vus, uniques = set(), []
            for p in choisis:
                nom = (p.get("nom_fr") or p.get("id") or "").strip().lower()
                if nom in vus:
                    continue
                vus.add(nom)
                uniques.append(p)
            choisis = uniques
        return ('<div class="activites surgit">'
                + "".join(carte_bonplan(p, langue) for p in choisis) + "</div>")

    doc = re.sub(
        r'<div class="activites surgit" data-bonsplans="(\w+)"(?: data-categorie="([\w-]+)")?></div>',
        remplir, doc)

    avis = [v for v in guide.get("avis", [])
            if v.get("visible") is not False and v.get("texte")]
    contenu = ("".join(carte_avis(v) for v in avis) if avis
               else '<p class="avis-vide">%s</p>' % e(LIBELLES[langue]["avis_vide"]))
    doc = doc.replace('<div class="agenda" data-agenda></div>',
                      '<div class="agenda">%s</div>' % bloc_agenda())

    doc = doc.replace('<div class="grille-avis surgit" id="grille-avis"></div>',
                      '<div class="grille-avis surgit" id="grille-avis">%s</div>' % contenu)
    return doc, avis


# --------------------------------------------------------------------------
# Assemblage
# --------------------------------------------------------------------------

def textes_alternatifs(doc, langue):
    """Applique la traduction anglaise des attributs alt.

    Meme principe que data-jalon-en : le fragment porte la version francaise
    dans alt et l anglaise dans data-alt-en, juste apres. Ces textes ne sont
    pas decoratifs — ce sont eux que lisent les lecteurs d ecran et Google.

    Le remplacement exige que les deux attributs soient adjacents. Si l un des
    deux se retrouve isole (attribut intercale, faute de frappe), la traduction
    ne s appliquerait pas et la page anglaise partirait en ligne avec un texte
    francais, sans que rien ne le signale : on compte donc les substitutions et
    on interrompt le build si le compte n y est pas.
    """
    attendus = len(re.findall(r'data-alt-en="', doc))
    if langue == "en":
        doc, faits = re.subn(r'alt="[^"]*"\s+data-alt-en="([^"]*)"',
                             lambda m: 'alt="%s"' % m.group(1), doc)
        if faits != attendus:
            raise ValueError(
                "%d data-alt-en sur %d appliques : verifiez que chaque data-alt-en "
                "suit immediatement son alt." % (faits, attendus))
    # En francais l attribut n a plus rien a faire dans la page livree.
    return re.sub(r'\s+data-alt-en="[^"]*"', "", doc)


def construire(gabarit, page, langue, guide):
    fragment = open(os.path.join(FRAGMENTS, page["fichier"]), encoding="utf-8").read()
    doc = gabarit.replace("<!--CONTENU-->", fragment, 1)

    # Le fragment porte les trois langues : on retire celles qu'on ne sert pas.
    for autre in registre.LANGUES:
        if autre != langue:
            doc = retirer(doc, "data-" + autre)

    # Libelles de l'indicateur lateral : on ne garde que celui de la langue,
    # pour qu'aucun texte de l'autre langue ne subsiste dans le document.
    if langue == "en":
        doc = re.sub(r'data-jalon="[^"]*"\s+data-jalon-en="([^"]*)"',
                     lambda m: 'data-jalon="%s"' % m.group(1), doc)
    doc = re.sub(r'\s+data-jalon-en="[^"]*"', "", doc)

    doc = textes_alternatifs(doc, langue)

    # Dans les titres, <em> passe a la ligne par le CSS mais reste colle au
    # mot precedent dans le texte extrait : « Les cols commencentau bas de la
    # rue ». On retablit l'espace, invisible a l'ecran, lisible par Google.
    def aerer_titre(m):
        interieur = re.sub(r"(\S)(<em>|<span\b)", r"\1 \2", m.group(2))
        return m.group(1) + interieur + m.group(3)

    doc = re.sub(r"(<h[12][^>]*>)(.*?)(</h[12]>)", aerer_titre, doc, flags=re.S)

    # Les pages vivent a des profondeurs differentes (/, /studio/,
    # /guide/x/, /en/studio/). Un chemin relatif casse partout sauf a la
    # racine : on force la racine absolue, une bonne fois.
    doc = re.sub(
        r'\b(src|href|poster)="(?!/|https?:|//|#|mailto:|tel:|data:)',
        lambda m: '%s="/' % m.group(1), doc)
    doc = re.sub(r'srcset="([^"]*)"',
                 lambda m: 'srcset="%s"' % srcset_absolu(m.group(1)), doc)

    doc = re.sub(r"[ \t]+\n", "\n", doc)
    doc = re.sub(r"\n{3,}", "\n\n", doc)

    doc, avis = prerendre(doc, langue, guide)

    doc = doc.replace('<html lang="fr">', '<html lang="%s">' % langue, 1)
    doc = doc.replace('<body class="lang-fr saison-hiver">',
                      '<body class="lang-%s saison-hiver">' % langue, 1)
    doc = doc.replace("<!--METAS-->", metas(page, langue), 1)
    doc = doc.replace("<!--JSONLD-->", donnees_structurees(page, langue, avis), 1)
    doc = doc.replace("<!--NAV-->", navigation(page, langue), 1)

    # Le fil d'Ariane se place sous la banniere de la page, pas au-dessus :
    # au-dessus, il coiffe une image plein cadre et passe sous le menu flottant.
    fil = fil_ariane(page, langue)
    if fil:
        marque = "</header>"
        if marque in doc:
            i = doc.index(marque) + len(marque)
            doc = doc[:i] + "\n\n" + fil + doc[i:]
        else:
            doc = doc.replace("<!--NAV-->", fil, 1)
    doc = doc.replace("<!--LANGUES-->", selecteur_langue(page, langue), 1)
    doc = doc.replace("<!--PIED-LIENS-->", pied_liens(langue), 1)

    doc = re.sub(r"<!--\s*=+\s*\n\s*SOURCE BILINGUE.*?=+\s*-->\n", "", doc, flags=re.S)
    doc = doc.replace(
        "<!DOCTYPE html>\n",
        "<!DOCTYPE html>\n"
        "<!-- FICHIER GENERE — toute modification sera perdue.\n"
        "     Modifier pages/%s ou gabarits/base.html, puis : python outils/build.py -->\n"
        % page["fichier"], 1)
    return doc


def sitemap(jour):
    blocs = []
    for p in registre.PAGES:
        if p.get("prive"):
            continue  # une page en noindex n'a rien a faire dans le sitemap
        langues = ["fr", "en"] if p["bilingue"] else ["fr"]
        for langue in langues:
            alternances = ""
            if p["bilingue"]:
                alternances = (
                    '\n    <xhtml:link rel="alternate" hreflang="fr" href="%s"/>'
                    '\n    <xhtml:link rel="alternate" hreflang="en" href="%s"/>'
                    '\n    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>'
                    % (registre.url(p["slug"], "fr"), registre.url(p["slug"], "en"),
                       registre.url(p["slug"], "fr")))
            blocs.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>%s\n  </url>"
                         % (registre.url(p["slug"], langue), jour, alternances))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(blocs) + "\n</urlset>\n")


def calendrier_ics():
    """Calendrier iCalendar des dates deja prises, a donner aux plateformes.

    Airbnb, Booking et les centrales de reservation savent importer une
    adresse .ics et bloquer automatiquement les dates qu elle contient.
    C est la seule parade serieuse au risque de double reservation quand
    le logement est propose a plusieurs endroits a la fois.

    Une seule precaution de format : DTEND est exclusif en iCalendar,
    comme le jour de depart l est chez nous. Les deux conventions
    coincident, il n y a donc rien a decaler.
    """
    donnees = json.load(open(RESERVATIONS, encoding="utf-8"))

    lignes = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Le Balcon d'Aure//Calendrier des disponibilites//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Le Balcon d'Aure — dates occupées",
    ]
    for resa in donnees.get("reservations", []):
        debut, fin = resa.get("arrivee"), resa.get("depart")
        if not debut or not fin:
            continue
        titre = "Réservé" if resa.get("statut") == "reserve" else "Option"
        lignes += [
            "BEGIN:VEVENT",
            "UID:%s-%s@lebalcondaure.fr" % (debut, fin),
            # Horodatage derive de la date d arrivee, et non de l heure
            # courante : sinon le fichier changerait a chaque execution et
            # l action GitHub republierait le site toutes les trois heures
            # pour une ligne sans interet.
            "DTSTAMP:" + debut.replace("-", "") + "T000000Z",
            "DTSTART;VALUE=DATE:" + debut.replace("-", ""),
            "DTEND;VALUE=DATE:" + fin.replace("-", ""),
            "SUMMARY:" + titre + " — Le Balcon d'Aure",
            "TRANSP:OPAQUE",
            "END:VEVENT",
        ]
    lignes.append("END:VCALENDAR")
    # iCalendar impose les fins de ligne CRLF.
    return "\r\n".join(lignes) + "\r\n"


def verifier_liens(produites):
    """Refuse un lien interne vers une page qui n'existe pas.

    Le piege classique du site bilingue asymetrique : une carte anglaise qui
    renvoie vers /en/guide/... alors que le guide n'existe qu'en francais.
    """
    connues = {"/" + c.replace("\\", "/").replace("index.html", "") for c in produites}
    connues = {c if c.endswith("/") else c + "/" for c in connues}
    manquants = []
    for chemin, doc in produites.items():
        for href in re.findall(r'href="(/[^"#?]*)"', doc):
            if not href.endswith("/"):
                continue  # fichier (css, image, manifeste) : verifie ailleurs
            if href not in connues:
                manquants.append((chemin, href))
    return manquants


def main():
    gabarit = open(GABARIT, encoding="utf-8").read()
    guide = json.load(open(GUIDE_JSON, encoding="utf-8"))

    produites = {}
    total = 0
    for page in registre.PAGES:
        for langue in registre.langues(page):
            doc = construire(gabarit, page, langue, guide)
            relatif = registre.chemin(page["slug"], langue)
            cible = os.path.join(RACINE, relatif)
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            with open(cible, "w", encoding="utf-8", newline="\n") as f:
                f.write(doc)
            produites[relatif] = doc
            total += 1
            print("  %-2s  %-42s %6d o   titre %3d" % (
                langue, registre.chemin(page["slug"], langue),
                len(doc.encode("utf-8")), len(page[langue]["titre"])))

    manquants = verifier_liens(produites)
    if manquants:
        print("\n*** %d lien(s) interne(s) vers une page inexistante :" % len(manquants))
        for chemin, href in manquants:
            print("      %-42s -> %s" % (chemin, href))
        sys.exit("Build interrompu : corrigez les liens ci-dessus.")

    jour = datetime.date.today().isoformat()
    with open(os.path.join(RACINE, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sitemap(jour))

    ics = calendrier_ics()
    with open(os.path.join(RACINE, "calendrier.ics"), "w", encoding="utf-8", newline="") as f:
        f.write(ics)
    print("  calendrier.ics : %d date(s) occupee(s) publiee(s)" % ics.count("BEGIN:VEVENT"))
    print("\n%d pages generees, %d liens internes verifies, sitemap a jour (%s)"
          % (total, sum(len(re.findall(r'href="(/[^"#?]*/)"', d)) for d in produites.values()), jour))


if __name__ == "__main__":
    main()
