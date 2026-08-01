#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere le site publie a partir de source.html.

    python outils/build.py

Produit :
  index.html      version francaise, canonique https://lebalcondaure.fr/
  en/index.html   version anglaise, canonique https://lebalcondaure.fr/en/
  sitemap.xml     les deux URL, avec lastmod et alternances hreflang

Pourquoi deux fichiers plutot qu'une page bilingue : tant que les deux
langues cohabitent sur la meme URL, Google n'indexe qu'une seule version et
ignore les annotations hreflang. Une URL par langue est la seule facon
d'etre reference sur les requetes anglaises.

Le contenu se modifie dans source.html (marque data-fr / data-en), jamais
dans les fichiers generes : ils sont ecrases a chaque build.
"""

import datetime
import html
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(RACINE, "source.html")
GUIDE = os.path.join(RACINE, "guide.json")

DOMAINE = "https://lebalcondaure.fr"

VIDES = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

# --------------------------------------------------------------------------
# Textes propres a chaque langue
# --------------------------------------------------------------------------

LANGUES = {
    "fr": {
        "code": "fr",
        "locale": "fr_FR",
        "locale_alt": "en_GB",
        "url": DOMAINE + "/",
        "dossier": "",
        "titre": "Studio à louer à Saint-Lary-Soulan, 200 m des pistes | Le Balcon d'Aure",
        "description": (
            "Studio 27 m² avec balcon vue montagne à Saint-Lary-Soulan, à 200 m des "
            "remontées. Sauna, jacuzzi, thermes à 150 m. Location en direct, sans commission."
        ),
        "og_titre": "Le Balcon d'Aure — studio à Saint-Lary-Soulan, 200 m des pistes",
        "og_description": (
            "27 m² et un balcon face aux sommets, résidence Royal Milan : sauna, jacuzzi, "
            "thermes à 150 m. Location en direct auprès des propriétaires."
        ),
        "image_alt": "Le studio Le Balcon d'Aure et la vallée d'Aure vus depuis le balcon",
        "ld_description": (
            "Studio de 27 m² avec balcon de 9 m² vue montagne, au premier étage de la "
            "résidence Royal Milan à Saint-Lary-Soulan. 200 m des remontées mécaniques, "
            "thermes Sensoria à 150 m, sauna et jacuzzi en accès libre, piscine chauffée "
            "l'été. Location en direct auprès des propriétaires, sans commission."
        ),
        "ld_animaux": "Chiens acceptés l'été uniquement, sous conditions ; pas d'animaux en hiver",
        "ld_logement": "Studio avec balcon, couchages dans la pièce de vie",
        "equipements": [
            "Balcon de 9 m² vue montagne",
            "Sauna et jacuzzi (résidence)",
            "Piscine extérieure chauffée l'été",
            "Salle de sport",
            "Lave-vaisselle",
            "Casier à skis",
            "Parking",
            "Wifi (espaces communs)",
        ],
        "avis_vide": "Votre avis inaugurera ce livre d’or : un message suffit.",
        "reduction": "Réduction avec notre code",
    },
    "en": {
        "code": "en",
        "locale": "en_GB",
        "locale_alt": "fr_FR",
        "url": DOMAINE + "/en/",
        "dossier": "en",
        "titre": "Ski studio to rent in Saint-Lary-Soulan, French Pyrenees | Le Balcon d'Aure",
        "description": (
            "27 m² studio flat with mountain-view balcony in Saint-Lary-Soulan, 200 m from "
            "the ski lifts. Sauna, jacuzzi, thermal baths 150 m away. Book direct, no fees."
        ),
        "og_titre": "Le Balcon d'Aure — studio flat in Saint-Lary-Soulan, 200 m from the lifts",
        "og_description": (
            "27 m² and a balcony facing the peaks, Royal Milan residence: sauna, jacuzzi, "
            "thermal baths 150 m away. Booked directly with the owners."
        ),
        "image_alt": "Le Balcon d'Aure studio and the Aure valley seen from the balcony",
        "ld_description": (
            "27 m² studio flat with a 9 m² mountain-view balcony, on the first floor of the "
            "Royal Milan residence in Saint-Lary-Soulan, French Pyrenees. 200 m from the ski "
            "lifts, Sensoria thermal baths 150 m away, free access to sauna and jacuzzi, "
            "heated outdoor pool in summer. Booked directly with the owners, no agency fees."
        ),
        "ld_animaux": "Dogs welcome in summer only, under conditions; no pets in winter",
        "ld_logement": "Studio flat with balcony, beds in the living area",
        "equipements": [
            "9 m² mountain-view balcony",
            "Sauna and jacuzzi (residence)",
            "Heated outdoor pool in summer",
            "Fitness room",
            "Dishwasher",
            "Ski locker",
            "Car park",
            "Wi-Fi (common areas)",
        ],
        "avis_vide": "Your review will open this guest book: just send us a message.",
        "reduction": "Discount with our code",
    },
}


# --------------------------------------------------------------------------
# Retrait des elements d'une langue
# --------------------------------------------------------------------------

def _masquer_scripts(doc):
    """Remplace le contenu des <script> par des jetons, pour que le decoupage
    des balises ne trebuche pas sur du HTML ecrit dans des chaines JS."""
    gardes = []

    def prendre(m):
        gardes.append(m.group(2))
        return "%s\x00%d\x00%s" % (m.group(1), len(gardes) - 1, m.group(3))

    doc = re.sub(
        r"(<script\b[^>]*>)(.*?)(</script>)", prendre, doc, flags=re.S | re.I
    )
    return doc, gardes


def _rendre_scripts(doc, gardes):
    return re.sub(r"\x00(\d+)\x00", lambda m: gardes[int(m.group(1))], doc)


BALISE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>")


def retirer(doc, attribut):
    """Supprime tout element portant `attribut` (et son sous-arbre)."""
    doc, gardes = _masquer_scripts(doc)
    presence = re.compile(r"(?:^|\s)%s(?=[\s=>/]|$)" % re.escape(attribut))

    sortie = []
    position = 0
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

        # Element a retirer : on saute jusqu'a sa balise fermante.
        sortie.append(doc[position:m.start()])
        if nom in VIDES or attrs.rstrip().endswith("/"):
            position = m.end()
            continue

        profondeur = 1
        curseur = m.end()
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


def dedoubler_espaces(doc):
    """Nettoie les lignes devenues vides apres le retrait d'une langue."""
    doc = re.sub(r"[ \t]+\n", "\n", doc)
    return re.sub(r"\n{3,}", "\n\n", doc)


# --------------------------------------------------------------------------
# En-tete : metadonnees et donnees structurees
# --------------------------------------------------------------------------

def att(texte):
    """Echappe pour un attribut HTML. Contrairement a html.escape(quote=True),
    laisse l'apostrophe intacte : les titres en contiennent, et &#x27; dans une
    balise <title> se retrouve tel quel dans certains apercus."""
    return (
        str(texte)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def metas(conf):
    autre = LANGUES["en" if conf["code"] == "fr" else "fr"]
    image = DOMAINE + "/images/opt/og-image.jpg"
    lignes = [
        "<title>%s</title>" % att(conf["titre"]),
        '<meta name="description" content="%s">' % att(conf["description"]),
        '<link rel="canonical" href="%s">' % conf["url"],
        '<link rel="alternate" hreflang="fr" href="%s">' % LANGUES["fr"]["url"],
        '<link rel="alternate" hreflang="en" href="%s">' % LANGUES["en"]["url"],
        '<link rel="alternate" hreflang="x-default" href="%s">' % LANGUES["fr"]["url"],
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Le Balcon d\'Aure">',
        '<meta property="og:title" content="%s">' % att(conf["og_titre"]),
        '<meta property="og:description" content="%s">' % att(conf["og_description"]),
        '<meta property="og:url" content="%s">' % conf["url"],
        '<meta property="og:image" content="%s">' % image,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="%s">' % att(conf["image_alt"]),
        '<meta property="og:locale" content="%s">' % conf["locale"],
        '<meta property="og:locale:alternate" content="%s">' % autre["locale"],
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="%s">' % image,
    ]
    return "\n".join(lignes)


def donnees_structurees(conf, avis):
    photos = ["vue-montagne", "sejour-baie", "sejour-large", "cuisine", "balcon-vue"]
    ld = {
        "@context": "https://schema.org",
        "@type": "VacationRental",
        "@id": DOMAINE + "/#logement",
        "name": "Le Balcon d'Aure",
        "url": conf["url"],
        "inLanguage": conf["code"],
        "description": conf["ld_description"],
        "image": [DOMAINE + "/images/opt/%s-1200.webp" % p for p in photos],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Résidence Royal Milan, chemin de Vielle-Aure",
            "addressLocality": "Saint-Lary-Soulan",
            "postalCode": "65170",
            "addressRegion": "Hautes-Pyrénées",
            "addressCountry": "FR",
        },
        "hasMap": (
            "https://www.google.com/maps/search/?api=1&query="
            "R%C3%A9sidence+Royal+Milan%2C+chemin+de+Vielle-Aure%2C+65170+Saint-Lary-Soulan"
        ),
        "telephone": ["+33642845542", "+33627352328"],
        "numberOfRooms": 1,
        "petsAllowed": conf["ld_animaux"],
        "priceRange": "300 € – 700 €",
        "currenciesAccepted": "EUR",
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": nom, "value": True}
            for nom in conf["equipements"]
        ],
        "containsPlace": {
            "@type": "Accommodation",
            "name": conf["ld_logement"],
            "floorSize": {"@type": "QuantitativeValue", "value": 27, "unitCode": "MTK"},
            "occupancy": {"@type": "QuantitativeValue", "maxValue": 3},
            "numberOfBedrooms": 0,
            "numberOfBathroomsTotal": 1,
        },
        "makesOffer": {
            "@type": "Offer",
            "priceCurrency": "EUR",
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "priceCurrency": "EUR",
                "minPrice": 300,
                "maxPrice": 700,
                "unitCode": "WEE",
            },
        },
    }

    # Les etoiles dans Google exigent des avis reellement affiches sur la page :
    # on ne balise que ceux qui sont publies dans guide.json.
    notes = [v["note"] for v in avis if v.get("note")]
    if notes:
        ld["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(notes) / len(notes), 1),
            "reviewCount": len(notes),
            "bestRating": 5,
            "worstRating": 1,
        }
    if avis:
        ld["review"] = [
            {
                "@type": "Review",
                "reviewBody": v["texte"],
                "author": {"@type": "Person", "name": v.get("auteur") or "Voyageur"},
                **(
                    {"datePublished": v["date"]}
                    if re.match(r"^\d{4}-\d{2}(-\d{2})?$", str(v.get("date", "")))
                    else {}
                ),
                **(
                    {
                        "reviewRating": {
                            "@type": "Rating",
                            "ratingValue": v["note"],
                            "bestRating": 5,
                            "worstRating": 1,
                        }
                    }
                    if v.get("note")
                    else {}
                ),
            }
            for v in avis
        ]

    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(
        ld, ensure_ascii=False, indent=2
    )


# --------------------------------------------------------------------------
# Pre-rendu du contenu aujourd'hui injecte en JavaScript
# --------------------------------------------------------------------------

def e(texte):
    return html.escape(str(texte), quote=True)


def carte_bonplan(plan, conf):
    fr = conf["code"] == "fr"
    url = plan["url_fr"] if fr else (plan.get("url_en") or plan["url_fr"])
    nom = plan["nom_fr"] if fr else (plan.get("nom_en") or plan["nom_fr"])
    desc = plan.get("desc_fr") if fr else (plan.get("desc_en") or plan.get("desc_fr"))
    mot = plan.get("commentaire") if fr else (plan.get("commentaire_en") or plan.get("commentaire"))

    morceaux = ['<a class="activite" target="_blank" rel="noopener" href="%s">' % e(url)]
    morceaux.append("<b>%s</b>" % e(nom))
    if desc:
        morceaux.append("<span>%s</span>" % e(desc))
    if plan.get("reduction"):
        morceaux.append('<span class="activite-reduc">%s</span>' % e(conf["reduction"]))
    if mot:
        morceaux.append('<span class="activite-mot">« %s » — Karine &amp; Romuald</span>' % e(mot))
    morceaux.append("</a>")
    return "".join(morceaux)


def carte_avis(v):
    morceaux = ['<div class="carte-avis">']
    if v.get("note"):
        etoiles = "★" * max(1, min(5, int(v["note"])))
        morceaux.append('<p class="avis-etoiles">%s</p>' % etoiles)
    morceaux.append("<blockquote>« %s »</blockquote>" % e(v["texte"]))
    pied = e(v.get("auteur", ""))
    if v.get("date"):
        pied += " · " + e(v["date"])
    morceaux.append('<div class="avis-pied"><span class="avis-auteur">%s</span>' % pied)
    if v.get("cible"):
        morceaux.append('<span class="avis-cible">%s</span>' % e(v["cible"]))
    morceaux.append("</div></div>")
    return "".join(morceaux)


def prerendre(doc, conf, guide):
    """Ecrit dans le HTML ce que le JavaScript reconstruira ensuite : un moteur
    qui n'execute pas le script voit quand meme les bons plans et les avis."""
    plans = [p for p in guide.get("bonsplans", []) if p.get("visible") is not False and p.get("url_fr")]

    def remplir_zone(m):
        saison = m.group(1)
        choisis = [p for p in plans if p.get("saison") in (saison, "toute")]
        return m.group(0)[:-len("</div>")] + "".join(
            carte_bonplan(p, conf) for p in choisis
        ) + "</div>"

    doc = re.sub(
        r'<div class="activites surgit" data-bonsplans="(\w+)"></div>',
        remplir_zone,
        doc,
    )

    avis = [v for v in guide.get("avis", []) if v.get("visible") is not False and v.get("texte")]
    contenu = (
        "".join(carte_avis(v) for v in avis)
        if avis
        else '<p class="avis-vide">%s</p>' % e(conf["avis_vide"])
    )
    doc = doc.replace(
        '<div class="grille-avis surgit" id="grille-avis"></div>',
        '<div class="grille-avis surgit" id="grille-avis">%s</div>' % contenu,
    )
    return doc, avis


# --------------------------------------------------------------------------
# Assemblage
# --------------------------------------------------------------------------

RELATIF = re.compile(r'\b(src|href|srcset|poster)="(?!https?:|//|/|#|mailto:|tel:|data:)')


def vers_sous_dossier(doc):
    """Sur /en/, les chemins relatifs remontent d'un cran."""
    doc = RELATIF.sub(lambda m: '%s="../' % m.group(1), doc)
    # srcset contient plusieurs chemins separes par des virgules
    doc = re.sub(
        r'srcset="([^"]*)"',
        lambda m: 'srcset="%s"'
        % re.sub(r"(^|,\s*)(?!\.\./|https?:|/)", r"\1../", m.group(1)),
        doc,
    )
    doc = doc.replace("fetch('reservations.json", "fetch('../reservations.json")
    doc = doc.replace("fetch('guide.json", "fetch('../guide.json")
    return doc


def selecteur_langue(conf):
    if conf["code"] == "fr":
        liens = (
            '<a class="actif" href="./" hreflang="fr" lang="fr" aria-current="page">FR</a>'
            '<a href="en/" hreflang="en" lang="en">EN</a>'
        )
    else:
        liens = (
            '<a href="../" hreflang="fr" lang="fr">FR</a>'
            '<a class="actif" href="./" hreflang="en" lang="en" aria-current="page">EN</a>'
        )
    return '<div class="langues">%s</div>' % liens


def construire(source, conf, guide):
    doc = retirer(source, "data-en" if conf["code"] == "fr" else "data-fr")
    doc = dedoubler_espaces(doc)
    doc, avis = prerendre(doc, conf, guide)

    doc = doc.replace('<html lang="fr">', '<html lang="%s">' % conf["code"], 1)
    doc = doc.replace(
        '<body class="lang-fr saison-hiver">',
        '<body class="lang-%s saison-hiver">' % conf["code"],
        1,
    )
    doc = doc.replace("<!--METAS-->", metas(conf), 1)
    doc = doc.replace("<!--JSONLD-->", donnees_structurees(conf, avis), 1)

    # Le commentaire de la source cede la place a celui du fichier genere.
    doc = re.sub(r"<!--\s*=+\s*\n\s*SOURCE BILINGUE.*?=+\s*-->\n", "", doc, flags=re.S)
    doc = doc.replace(
        "<!DOCTYPE html>\n",
        "<!DOCTYPE html>\n"
        "<!-- FICHIER GENERE — toute modification sera perdue.\n"
        "     Modifier source.html, puis : python outils/build.py -->\n",
        1,
    )

    if conf["dossier"]:
        doc = vers_sous_dossier(doc)

    # Insere apres la reecriture des chemins : ces liens sont deja corrects.
    doc = doc.replace("<!--LANGUES-->", selecteur_langue(conf), 1)
    return doc


def sitemap(jour):
    urls = []
    for conf in (LANGUES["fr"], LANGUES["en"]):
        urls.append(
            "  <url>\n"
            "    <loc>%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            '    <xhtml:link rel="alternate" hreflang="fr" href="%s"/>\n'
            '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n'
            '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>\n'
            "  </url>"
            % (conf["url"], jour, LANGUES["fr"]["url"], LANGUES["en"]["url"], LANGUES["fr"]["url"])
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def main():
    if not os.path.isfile(SOURCE):
        sys.exit("source.html introuvable")

    with open(SOURCE, encoding="utf-8") as f:
        source = f.read()
    with open(GUIDE, encoding="utf-8") as f:
        guide = json.load(f)

    for code, conf in LANGUES.items():
        doc = construire(source, conf, guide)
        dossier = os.path.join(RACINE, conf["dossier"]) if conf["dossier"] else RACINE
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, "index.html")
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
        print(
            "%-16s %6d octets   titre %d car.   description %d car."
            % (
                os.path.relpath(chemin, RACINE),
                len(doc.encode("utf-8")),
                len(conf["titre"]),
                len(conf["description"]),
            )
        )

    jour = datetime.date.today().isoformat()
    with open(os.path.join(RACINE, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sitemap(jour))
    print("sitemap.xml      2 URL, lastmod %s" % jour)


if __name__ == "__main__":
    main()
