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

DOMAINE = registre.DOMAINE

VIDES = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

LOCALES = {"fr": "fr_FR", "en": "en_GB"}

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

    # hreflang uniquement si la traduction existe reellement
    if page["bilingue"]:
        lignes += [
            '<link rel="alternate" hreflang="fr" href="%s">' % registre.url(page["slug"], "fr"),
            '<link rel="alternate" hreflang="en" href="%s">' % registre.url(page["slug"], "en"),
            '<link rel="alternate" hreflang="x-default" href="%s">' % registre.url(page["slug"], "fr"),
        ]

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
    if page["bilingue"]:
        lignes.append('<meta property="og:locale:alternate" content="%s">'
                      % LOCALES["en" if langue == "fr" else "fr"])
    lignes += [
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="%s">' % image,
    ]
    return "\n".join(lignes)


def bloc_logement(page, langue, avis):
    photos = ["vue-montagne", "sejour-baie", "sejour-large", "cuisine", "balcon-vue"]
    if langue == "fr":
        description = ("Studio de 27 m² avec balcon de 9 m² vue montagne, au premier étage de la "
                       "résidence Royal Milan à Saint-Lary-Soulan. 200 m des remontées mécaniques, "
                       "thermes Sensoria à 150 m, sauna et jacuzzi en accès libre, piscine chauffée "
                       "l'été. Location en direct auprès des propriétaires, sans commission.")
        animaux = "Chiens acceptés l'été uniquement, sous conditions ; pas d'animaux en hiver"
        logement = "Studio avec balcon, couchages dans la pièce de vie"
        equipements = ["Balcon de 9 m² vue montagne", "Sauna et jacuzzi (résidence)",
                       "Piscine extérieure chauffée l'été", "Salle de sport", "Lave-vaisselle",
                       "Casier à skis", "Parking", "Wifi (espaces communs)"]
    else:
        description = ("27 m² studio flat with a 9 m² mountain-view balcony, on the first floor of the "
                       "Royal Milan residence in Saint-Lary-Soulan, French Pyrenees. 200 m from the ski "
                       "lifts, Sensoria thermal baths 150 m away, free access to sauna and jacuzzi, "
                       "heated outdoor pool in summer. Booked directly with the owners, no agency fees.")
        animaux = "Dogs welcome in summer only, under conditions; no pets in winter"
        logement = "Studio flat with balcony, beds in the living area"
        equipements = ["9 m² mountain-view balcony", "Sauna and jacuzzi (residence)",
                       "Heated outdoor pool in summer", "Fitness room", "Dishwasher",
                       "Ski locker", "Car park", "Wi-Fi (common areas)"]

    ld = {
        "@context": "https://schema.org",
        "@type": "VacationRental",
        "@id": DOMAINE + "/#logement",
        "name": "Le Balcon d'Aure",
        "url": registre.url(page["slug"], langue),
        "inLanguage": langue,
        "description": description,
        "image": [DOMAINE + "/images/opt/%s-1200.webp" % p for p in photos],
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
        "priceRange": "300 € – 700 €",
        "currenciesAccepted": "EUR",
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in equipements
        ],
        "containsPlace": {
            "@type": "Accommodation",
            "name": logement,
            "floorSize": {"@type": "QuantitativeValue", "value": 27, "unitCode": "MTK"},
            "occupancy": {"@type": "QuantitativeValue", "maxValue": 3},
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
        if not p.get("virtuel"):
            item["item"] = registre.url(p["slug"], langue)
        elements.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}


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
    fil = bloc_fil(page, langue)
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
    """Une page monolingue reste en francais meme depuis la version anglaise."""
    if langue == "en" and not page["bilingue"]:
        return registre.url(page["slug"], "fr").replace(DOMAINE, "")
    return registre.url(page["slug"], langue).replace(DOMAINE, "")


def navigation(page, langue):
    lib = LIBELLES[langue]
    accueil = "/" if langue == "fr" else "/en/"
    liens = []
    for p in registre.PAGES:
        if not p["menu"]:
            continue
        if langue == "en" and not p["bilingue"]:
            continue  # pas de page anglaise, on n'encombre pas le menu anglais
        libelle = p["menu"].get(langue) or p["menu"]["fr"]
        classe = ' class="actif" aria-current="page"' if p["slug"] == page["slug"] else ""
        liens.append('<a href="%s"%s>%s</a>' % (lien_menu(p, langue), classe, e(libelle)))

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
    if not page["bilingue"]:
        return ""
    fr = registre.url(page["slug"], "fr").replace(DOMAINE, "")
    en = registre.url(page["slug"], "en").replace(DOMAINE, "")
    a = ('<a class="actif" href="%s" hreflang="fr" lang="fr" aria-current="page">FR</a>'
         if langue == "fr" else '<a href="%s" hreflang="fr" lang="fr">FR</a>') % fr
    b = ('<a class="actif" href="%s" hreflang="en" lang="en" aria-current="page">EN</a>'
         if langue == "en" else '<a href="%s" hreflang="en" lang="en">EN</a>') % en
    return '<div class="langues">%s%s</div>' % (a, b)


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
            if langue == "en" and not p["bilingue"]:
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
    fr = langue == "fr"
    url = plan["url_fr"] if fr else (plan.get("url_en") or plan["url_fr"])
    nom = plan["nom_fr"] if fr else (plan.get("nom_en") or plan["nom_fr"])
    desc = plan.get("desc_fr") if fr else (plan.get("desc_en") or plan.get("desc_fr"))
    mot = plan.get("commentaire") if fr else (plan.get("commentaire_en") or plan.get("commentaire"))
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


def prerendre(doc, langue, guide):
    plans = [p for p in guide.get("bonsplans", [])
             if p.get("visible") is not False and p.get("url_fr")]

    def remplir(m):
        saison = m.group(1)
        choisis = [p for p in plans if p.get("saison") in (saison, "toute")]
        return (m.group(0)[:-len("</div>")]
                + "".join(carte_bonplan(p, langue) for p in choisis) + "</div>")

    doc = re.sub(r'<div class="activites surgit" data-bonsplans="(\w+)"></div>', remplir, doc)

    avis = [v for v in guide.get("avis", [])
            if v.get("visible") is not False and v.get("texte")]
    contenu = ("".join(carte_avis(v) for v in avis) if avis
               else '<p class="avis-vide">%s</p>' % e(LIBELLES[langue]["avis_vide"]))
    doc = doc.replace('<div class="grille-avis surgit" id="grille-avis"></div>',
                      '<div class="grille-avis surgit" id="grille-avis">%s</div>' % contenu)
    return doc, avis


# --------------------------------------------------------------------------
# Assemblage
# --------------------------------------------------------------------------

def construire(gabarit, page, langue, guide):
    fragment = open(os.path.join(FRAGMENTS, page["fichier"]), encoding="utf-8").read()
    doc = gabarit.replace("<!--CONTENU-->", fragment, 1)

    doc = retirer(doc, "data-en" if langue == "fr" else "data-fr")

    # Libelles de l'indicateur lateral : on ne garde que celui de la langue,
    # pour qu'aucun texte de l'autre langue ne subsiste dans le document.
    if langue == "en":
        doc = re.sub(r'data-jalon="[^"]*"\s+data-jalon-en="([^"]*)"',
                     lambda m: 'data-jalon="%s"' % m.group(1), doc)
    doc = re.sub(r'\s+data-jalon-en="[^"]*"', "", doc)

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
        r'\b(src|href|srcset|poster)="(?!/|https?:|//|#|mailto:|tel:|data:)',
        lambda m: '%s="/' % m.group(1), doc)
    doc = re.sub(
        r'srcset="([^"]*)"',
        lambda m: 'srcset="%s"' % re.sub(r"(^|,\s*)(?!/|https?:)", r"\g<1>/", m.group(1)),
        doc)

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
        for langue in (["fr", "en"] if page["bilingue"] else ["fr"]):
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
    print("\n%d pages generees, %d liens internes verifies, sitemap a jour (%s)"
          % (total, sum(len(re.findall(r'href="(/[^"#?]*/)"', d)) for d in produites.values()), jour))


if __name__ == "__main__":
    main()
