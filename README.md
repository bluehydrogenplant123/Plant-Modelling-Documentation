# Plant-Modelling-Documentation

This repository hosts the Chemware Docusaurus documentation site configured for GitHub Pages.

## Local development

```bash
npm ci
npm start
```

## Production build

```bash
npm run build
```

## GitHub Pages

Pushes to `main` trigger the workflow in `.github/workflows/deploy.yml`, which builds the site and deploys it to GitHub Pages.

Expected site URL:

```text
https://bluehydrogenplant123.github.io/Plant-Modelling-Documentation/
```
