# Contribuer au site Souss

Merci de votre intérêt ! Ce site est maintenu par l'organisation **Souss-massa**.

## Le flux « contribution = publication »

1. **Fork** ce dépôt (`Souss-massa/souss-site`) ou créez une branche si vous êtes membre.
2. Modifiez le contenu (voir `content/README.md` pour ajouter une personnalité, ou éditez directement les pages HTML/CSS).
3. Ouvrez une **pull request** vers `main`.
4. La CI valide automatiquement le contenu (`validate` : HTML, liens internes, schéma JSON, images joignables).
5. Un **admin ou éditeur** de l'organisation relit et approuve (1 approbation requise).
6. Au **merge** sur `main`, le workflow `deploy-pages` publie automatiquement le site sur **GitHub Pages**.

## Règles de revue (admins/éditeurs)

- Le JSON de `content/` doit respecter le schéma documenté dans `content/README.md`.
- Les images doivent être sous licence libre (Wikimedia Commons ou équivalent) avec URL stable.
- Pas de secrets ni de données personnelles dans le contenu.
- Les PR passent d'abord par la CI `validate` (doit être verte).

## Tester en local

```bash
python3 -m http.server 8123
# ouvrir http://127.0.0.1:8123/
python3 tools/validate.py   # même validation que la CI
```

## Rôles

Configurez dans **Settings → Members** de l'organisation : `Admin` pour les propriétaires, `Member` (write) pour les éditeurs qui peuvent approuver et merger.
