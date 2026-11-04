# Contenu éditorial (contributions)

Ce dossier est la porte d'entrée des contributions acceptées par les administrateurs/éditeurs de l'organisation **Souss-massa**.

Flux : **fork → branche → pull request → revue (1 approbation) → merge sur `main` → déploiement automatique (GitHub Pages)**. Une fois le PR mergé, le contenu apparaît sur le site.

## `personnalites.json`

Tableau JSON de personnalités ajoutées par la communauté. Elles sont rendues en cartes à la fin de la page `personnalites.html` (badge « Contribution »), et participent aux filtres par catégorie.

Schéma d'un élément :

```json
{
  "id": "nom-slug-unique",
  "name": "Nom complet",
  "tag": "Rôle (ex : Poète, Historien, Musicien…)",
  "meta": "1900 – 1980 · Ville, région",
  "bio": "Texte biographique (HTML simple autorisé : <em>, <strong>, <a href>).",
  "works": "Œuvres marquantes (optionnel)",
  "cats": ["lettres"],
  "initials": "ⵎⵙ",
  "image": {
    "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/…/1280px-….jpg",
    "alt": "Description de l'image",
    "credit": "Légende affichée sur la photo"
  }
}
```

- `cats` : sous-ensemble de `lettres`, `musique`, `spirituel`, `resistance`, `sport`.
- `image` est optionnel : sans image, les initiales s'affichent sur fond dégradé.
- `id` doit être unique dans le fichier.
- Les images doivent être des URLs Wikimedia Commons stables (hôte `upload.wikimedia.org`, largeur 1280px) ou tout média sous licence libre.

Le fichier est validé automatiquement à chaque pull request (`tools/validate.py`) : JSON valide, champs requis présents, `cats` autorisés, `id` uniques, URLs d'images joignables.

## `figures.json` — fiches détaillées des personnalités

`content/figures.json` est la source de vérité des 14 fiches détaillées :
biographie complète, repères chronologiques, œuvres, faits et sources.
Il est compilé par `tools/build_figures.py` qui génère :

- `personnalites/<id>.html` — une page par personnalité ;
- les cartes de `personnalites.html` (entre les marqueurs
  `<!-- figures:start -->` et `<!-- figures:end -->`).

Après toute modification de `figures.json`, régénérez et vérifiez :

```bash
python3 tools/build_figures.py
python3 tools/validate.py   # refuse les pages générées périmées
```
