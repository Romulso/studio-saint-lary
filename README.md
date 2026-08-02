# Le Balcon d'Aure — lebalcondaure.fr

Site du studio à louer à Saint-Lary-Soulan, hébergé sur GitHub Pages.
Pas de framework, pas de dépendance à installer : du HTML, du CSS et un peu
de JavaScript. Trois scripts Python préparent les fichiers publiés.

## Ce qu'il faut savoir avant de modifier quoi que ce soit

Les fichiers `index.html` répartis à la racine et dans les sous-dossiers
sont **générés**. Les modifier ne sert à rien : le prochain build les
écrase. Le contenu se modifie dans **`pages/`**.

```
pages/<fragment>.html  ─┐
                        ├─▶  outils/build.py  ──▶  <slug>/index.html
gabarits/base.html     ─┤                     ──▶  en/<slug>/index.html
outils/pages.py        ─┘                     ──▶  sitemap.xml
```

- **`pages/*.html`** — le contenu de chaque page, sans en-tête ni pied de page.
- **`gabarits/base.html`** — le squelette commun : `<head>`, menu, pied de page,
  panorama et tout le JavaScript. Modifié une fois, il s'applique partout.
- **`outils/pages.py`** — le registre : arborescence, titres, descriptions,
  place dans le menu, type de données structurées. **C'est ici qu'on ajoute
  une page.**

## Le bilinguisme

Dans `pages/`, chaque élément propre à une langue porte `data-fr` ou `data-en` :

```html
<h3 data-fr>Forfaits</h3><h3 data-en>Ski passes</h3>
```

Le build garde l'un et retire l'autre. Une page publiée ne contient donc
qu'une seule langue — c'est ce qui permet à Google d'indexer les deux
versions séparément.

Toutes les pages ne sont pas traduites : le champ `bilingue` de
`outils/pages.py` décide. Une page en français seulement **ne déclare aucun
hreflang alterne** — annoncer une traduction qui n'existe pas fait ignorer
tout le groupe de langues par Google. Le build refuse de produire un site
qui contiendrait un lien interne vers une page inexistante.

## Modifier le contenu

```bash
python outils/build.py
```

Puis commiter `pages/`, les `index.html` générés et `sitemap.xml` ensemble.

## Ajouter une page

1. Créer le fragment dans `pages/` (partir d'un fragment existant).
2. Ajouter l'entrée correspondante dans `PAGES`, au bon endroit, dans
   `outils/pages.py` : `slug`, `fichier`, `bilingue`, `menu`, `fil`,
   `parent`, `jsonld`, puis les titres et descriptions par langue.
3. `python outils/build.py`

Le menu, le fil d'Ariane, le pied de page et le sitemap se mettent à jour
tout seuls.

## Ajouter ou remplacer une photo

1. Déposer le fichier dans `images/` (JPEG, la plus grande taille disponible).
2. `python outils/images.py` — génère les WebP dans `images/opt/` aux largeurs
   500, 800, 1200 et 1600 px, plus `og-image.jpg` (l'aperçu des liens partagés).
3. Référencer les WebP dans le fragment avec `srcset`, `sizes`, `width`,
   `height` et un `alt` descriptif, en recopiant un bloc existant.
4. `python outils/build.py`

Les JPEG d'origine restent dans `images/` : ils servent de source aux
regénérations et aux flyers imprimables.

## Refaire les favicons

```bash
python outils/favicons.py
```

Le motif est défini deux fois : en vectoriel dans `favicon.svg`, et en
Python dans `outils/favicons.py` pour les PNG. Modifier les deux.

## Réservations, tarifs et bons plans

`reservations.json` et `guide.json` se modifient depuis `admin.html`
(page volontairement non indexée). Ces fichiers sont lus par le JavaScript
à chaque visite : une modification est visible immédiatement, sans rebuild.

Le build en recopie tout de même le contenu directement dans le HTML, pour
qu'un robot qui n'exécute pas le JavaScript le voie. Relancer `build.py` de
temps en temps garde ce pré-rendu à jour ; l'oublier n'a aucune conséquence
visible pour les visiteurs.

## Vérifier avant de publier

```bash
python -m http.server 4291
```

Puis ouvrir <http://localhost:4291/>.

## Arborescence publiée

| URL | Rôle |
|---|---|
| `/` · `/en/` | accueil |
| `/studio/` · `/en/studio/` | le logement en détail |
| `/residence-royal-milan/` · `/en/…` | la résidence et ses espaces communs |
| `/tarifs-disponibilites/` · `/en/…` | grille tarifaire, calendrier, conditions |
| `/hiver/` · `/en/hiver/` | séjour au ski |
| `/ete/` · `/en/ete/` | séjour randonnée et lacs |
| `/cure-thermale/` | séjour curiste (français seulement) |
| `/velo/` | séjour cycliste (français seulement) |
| `/guide/skier-a-saint-lary/` | guide des trois secteurs |
| `/guide/lacs-du-neouvielle/` | guide de la randonnée emblématique |
| `/guide/saint-lary-quand-il-pleut/` | guide des jours de mauvais temps |
| `/guide/venir-a-saint-lary/` | accès, train, navette, vie sans voiture |
| `/livre-d-or/` | avis des locataires |
| `/contact/` · `/en/contact/` | formulaire et coordonnées |
| `/mentions-legales/` | mentions légales et confidentialité |

## Fichiers

| Fichier | Rôle |
|---|---|
| `pages/` | **le contenu — c'est ici qu'on écrit** |
| `gabarits/base.html` | squelette commun à toutes les pages |
| `outils/pages.py` | registre des pages et des métadonnées |
| `outils/build.py` | génère les pages, le sitemap, vérifie les liens |
| `outils/images.py` | génère les WebP et l'image de partage |
| `outils/favicons.py` | génère les icônes PNG |
| `style.css` | feuille de style unique |
| `admin.html` | gestion des réservations et du guide (non indexée) |
| `guide.json`, `reservations.json` | données lues à chaud par le site |
| `flyer.html`, `flyer-a6.html`, `affiche-a4.html` | supports imprimables (non indexés) |
