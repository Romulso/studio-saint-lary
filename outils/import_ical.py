#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importe les reservations des plateformes dans reservations.json.

    ICAL_AIRBNB="https://…" python3 outils/import_ical.py

Chaque plateforme publie une adresse .ics qui liste ses dates occupees.
On n en retient QUE les vraies reservations : Airbnb y melange aussi les
dates que le proprietaire a bloquees lui-meme (« Airbnb (Not available) »),
et les importer fermerait sur le site des dates que Karine et Romuald
veulent au contraire continuer a louer en direct — la semaine du Tour de
France en est l exemple meme.

Les reservations saisies a la main dans admin.html ne portent pas de
champ "source" : elles sont conservees telles quelles. Seules les lignes
venues d une plateforme sont remplacees a chaque passage.

L adresse .ics contient un jeton d acces au calendrier : elle se passe par
variable d environnement, jamais dans le depot, qui est public.
"""

import json
import os
import re
import ssl
import sys
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESERVATIONS = os.path.join(RACINE, "reservations.json")

# Nom de la variable d'environnement -> nom de la source dans le JSON
PLATEFORMES = {
    "ICAL_AIRBNB": "airbnb",
    "ICAL_BOOKING": "booking",
    "ICAL_OFFICE": "office-de-tourisme",
}

# Un evenement est une vraie reservation si son libelle en porte la marque.
# Airbnb ecrit « Reserved », Booking « CLOSED - Not available » pour ses
# blocages et le nom du client pour ses reservations : dans le doute, on
# ecarte tout ce qui ressemble a une indisponibilite.
BLOCAGE = re.compile(r"not available|unavailable|blocked|bloqu|ferm|closed", re.I)


def evenements(ics):
    """Rend les (debut, fin, libelle) de chaque VEVENT."""
    texte = ics.replace("\r\n", "\n").replace("\n ", "")  # deplie les lignes
    for bloc in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", texte, re.S):
        debut = re.search(r"DTSTART[^:]*:(\d{8})", bloc)
        fin = re.search(r"DTEND[^:]*:(\d{8})", bloc)
        libelle = re.search(r"SUMMARY:(.*)", bloc)
        if not (debut and fin):
            continue
        iso = lambda j: "%s-%s-%s" % (j[:4], j[4:6], j[6:])
        yield iso(debut.group(1)), iso(fin.group(1)), (libelle.group(1).strip() if libelle else "")


def contexte_ssl():
    """Le Python livre avec macOS n a pas de magasin de certificats : sans
    certifi, la verification echoue alors qu elle passe sur le serveur."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def lire(url):
    requete = urllib.request.Request(url, headers={"User-Agent": "lebalcondaure.fr"})
    with urllib.request.urlopen(requete, timeout=30, context=contexte_ssl()) as reponse:
        return reponse.read().decode("utf-8", "replace")


def main():
    donnees = json.load(open(RESERVATIONS, encoding="utf-8"))
    manuelles = [r for r in donnees.get("reservations", []) if not r.get("source")]
    deja = {(r["arrivee"], r["depart"]) for r in manuelles}

    importees, resume = [], []
    for variable, source in PLATEFORMES.items():
        url = os.environ.get(variable, "").strip()
        if not url:
            continue
        try:
            ics = lire(url)
        except Exception as erreur:          # noqa: BLE001
            print("  %-18s ECHEC : %s" % (source, erreur), file=sys.stderr)
            resume.append("%s: echec" % source)
            continue

        gardees = ignorees = 0
        for debut, fin, libelle in evenements(ics):
            if BLOCAGE.search(libelle):
                ignorees += 1
                continue
            if (debut, fin) in deja:
                continue
            deja.add((debut, fin))
            importees.append({"arrivee": debut, "depart": fin, "statut": "reserve",
                              "source": source, "note": libelle or source})
            gardees += 1
        print("  %-18s %d reservation(s), %d blocage(s) ignore(s)" % (source, gardees, ignorees))
        resume.append("%s: %d" % (source, gardees))

    fusion = manuelles + importees
    fusion.sort(key=lambda r: r["arrivee"])
    if fusion == donnees.get("reservations"):
        print("Aucun changement.")
        return 0

    donnees["reservations"] = fusion
    with open(RESERVATIONS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("reservations.json mis a jour : %d manuelle(s) + %d importee(s)"
          % (len(manuelles), len(importees)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
