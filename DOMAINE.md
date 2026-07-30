# Passer le site sur un vrai nom de domaine

Guide pour brancher un domaine (ex. `lebalcondaure.fr`) sur ce site GitHub Pages.
Coût : ~10 €/an. Durée : ~1 h, puis quelques heures de propagation DNS.

## 1 · Acheter le domaine

Chez n'importe quel registrar sérieux : OVH, Gandi, Ionos… Prendre le `.fr`
(et éventuellement le `.com` en redirection). Rien d'autre à acheter :
pas d'hébergement, GitHub Pages reste l'hébergeur gratuit.

## 2 · Configurer le DNS chez le registrar

Dans la zone DNS du domaine, créer :

| Type  | Nom  | Valeur |
|-------|------|--------|
| A     | @    | 185.199.108.153 |
| A     | @    | 185.199.109.153 |
| A     | @    | 185.199.110.153 |
| A     | @    | 185.199.111.153 |
| CNAME | www  | romulso.github.io. |

## 3 · Déclarer le domaine côté GitHub

Sur https://github.com/Romulso/studio-saint-lary → Settings → Pages :
- « Custom domain » : saisir `lebalcondaure.fr` → Save
  (GitHub crée un fichier `CNAME` à la racine du repo, c'est normal)
- Attendre la vérification DNS (peut prendre quelques heures)
- Cocher « Enforce HTTPS » dès que la case devient disponible

Conseillé : Settings (du compte) → Pages → « Verified domains » pour
protéger le domaine.

## 4 · Mettre à jour les URL dans le code (à demander à Mathieu/Claude)

Remplacer `https://lebalcondaure.fr/` par
`https://lebalcondaure.fr/` dans :
- `index.html` : balise `canonical`, les 3 `hreflang`, `og:url`, `og:image`,
  le JSON-LD (`url` + `image`), et le texte du bouton de partage
- `sitemap.xml` : toutes les URL
- `robots.txt` : la ligne Sitemap

Attention : une fois le domaine actif, les chemins ne contiennent plus
`/studio-saint-lary/` — les chemins relatifs du site (images, CSS, JSON)
fonctionnent tels quels, seules les URL absolues ci-dessus changent.

## 5 · Ensuite (visibilité)

1. **Google Search Console** (https://search.google.com/search-console) :
   ajouter la propriété « Domaine », vérification par enregistrement DNS TXT
   (le registrar l'affiche), puis soumettre `sitemap.xml`.
2. **Google Business Profile** (https://business.google.com) : créer la fiche
   « Le Balcon d'Aure — location de vacances », catégorie « Location de
   vacances », adresse Résidence Royal Milan, chemin de Vielle-Aure,
   65170 Saint-Lary-Soulan, lien vers le site, photos du studio.
3. **Office de tourisme** : demander le référencement du meublé sur
   saintlary.com (et engager le classement « meublé de tourisme » en mairie).
4. L'ancienne adresse `lebalcondaure.fr` redirigera
   automatiquement vers le domaine : les liens déjà partagés continuent
   de fonctionner.
