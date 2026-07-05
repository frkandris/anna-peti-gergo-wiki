---
type: "Runbook"
title: "Deploy — GitHub Actions → Pages"
description: "Hogyan épül és publikálódik az oldal."
tags: ["deploy", "github-actions", "pages"]
timestamp: "2026-07-05"
---

# Deploy

- **Trigger:** push a `main`-re (`.github/workflows/deploy.yml`), vagy manuális
  `workflow_dispatch`.
- **Lépések:** Node telepítés → `npm ci` a `site/`-ban → `npm run build` →
  a `site/dist` feltöltése GitHub Pages-artifactként → deploy.
- **URL:** https://frkandris.github.io/anna-peti-gergo-wiki/ (project pages, base = a repó neve).
- **Ellenőrzés:** a build lógó hivatkozáson elbukik → a hibás content nem megy ki.
- **Analytics:** Cloudflare Web Analytics beacon (süti nélkül).

Kézi build lokálisan: `cd site && npm install && npm run build && npm run preview`.
