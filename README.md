# Le Balcon d'Aure — lebalcondaure.fr

Site du studio à louer à Saint-Lary-Soulan, hébergé sur GitHub Pages.
Pas de framework, pas de dépendance à installer : du HTML, du CSS et un peu
de JavaScript. Trois petits scripts Python servent à préparer les fichiers
publiés.

## Ce qu'il faut savoir avant de modifier quoi que ce soit

`index.html` et `en/index.html` sont **générés**. Les modifier directement
ne sert à rien : le prochain build les écrase. Le contenu se modifie dans
**`source.html`**, qui contient les deux langues.

```
source.html   ──▶  outils/build.py  ──▶  index.html      (français)
                                    ──▶  en/index.html   (anglais)
                                    ──▶  sitemap.xml
```

Dans `source.html`, chaque élément propre à une langue porte `data-fr` ou
`data-en` :

```html
<h3 data-fr>Forfaits</h3><h3 data-en>Ski passes</h3>
```

Le build garde `data-fr` pour la page française, `data-en` pour l'anglaise,
et retire l'autre. Une page publiée ne contient donc qu'une seule langue —
c'est ce qui permet à Google d'indexer les deux versions séparément.

## Modifier le contenu

```bash
python outils/build.py
```

Puis commiter `source.html`, `index.html`, `en/index.html` et `sitemap.xml`
ensemble.

Les textes qui ne sont pas dans `source.html` (titre de la page, description,
données structurées) sont en haut de `outils/build.py`, dans le dictionnaire
`LANGUES`.

## Ajouter ou remplacer une photo

1. Déposer le fichier dans `images/` (JPEG, la plus grande taille disponible).
2. `python outils/images.py` — génère les versions WebP dans `images/opt/`
   aux largeurs 500, 800, 1200 et 1600 px, plus `og-image.jpg` (l'aperçu des
   liens partagés sur WhatsApp et Facebook).
3. Référencer les WebP dans `source.html` avec `srcset`, `sizes`, `width`,
   `height` et un `alt` descriptif, en recopiant un bloc existant.
4. `python outils/build.py`

Les JPEG d'origine restent dans `images/` : ils servent de source aux
regénérations et aux flyers imprimables.

## Refaire les favicons

```bash
python outils/favicons.py
```

Le motif est défini deux fois : en vectoriel dans `favicon.svg`, et en
Python dans `outils/favicons.py` pour les versions PNG. Modifier les deux.

## Réservations, tarifs et bons plans

`reservations.json` et `guide.json` se modifient depuis `admin.html`
(page volontairement non indexée). Ces deux fichiers sont lus par le
JavaScript à chaque visite : une modification est visible immédiatement,
sans rebuild.

Le build recopie tout de même les bons plans et le livre d'or directement
dans le HTML, pour qu'un robot qui n'exécute pas le JavaScript les voie
quand même. Relancer `build.py` de temps en temps garde ce pré-rendu à jour ;
oublier de le faire n'a aucune conséquence visible pour les visiteurs.

## Vérifier avant de publier

```bash
python -m http.server 4291
```

Puis ouvrir <http://localhost:4291/> et <http://localhost:4291/en/>.

## Fichiers

| Fichier | Rôle |
|---|---|
| `source.html` | **la source bilingue — c'est ici qu'on écrit** |
| `index.html`, `en/index.html` | générés, ne pas éditer |
| `style.css` | feuille de style unique, commune aux deux langues |
| `admin.html` | gestion des réservations et du guide (non indexée) |
| `guide.json`, `reservations.json` | données lues à chaud par le site |
| `flyer.html`, `flyer-a6.html`, `affiche-a4.html` | supports imprimables (non indexés) |
| `outils/build.py` | génère les pages et le sitemap |
| `outils/images.py` | génère les WebP et l'image de partage |
| `outils/favicons.py` | génère les icônes PNG |
