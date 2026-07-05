---
type: "Reference"
title: "Astro oldal — oldalak, kereső, szűrők"
description: "Az oldalgeneráló Astro projekt felépítése és a kliensoldali kereső/szűrő."
tags: ["astro", "kereso", "szuro"]
timestamp: "2026-07-05"
---

# Astro oldal

- **Oldaltípusok** (`site/src/pages/`): főoldal, kötet-, mese-, szereplő-,
  helyszín-, tárgy-, téma-, évszak-, ünnepoldalak + indexek. Mind statikus,
  `getStaticPaths`-szal.
- **URL-szegmensek** magyarul (`site/src/lib/site.ts`): `kotet`, `mese`,
  `szereplo`, `helyszin`, `targy`, `tema`, `evszak`, `unnep`.
- **Base path:** a projekt GitHub Pages-alkönyvtáron él (`base` az
  `astro.config.mjs`-ben). MINDEN belső linket a `href()` helper adjon, hogy a
  base ne törjön el.
- **Kereső + szűrő** (`mese/index.astro`): kliensoldali JS egy build-időben
  beágyazott JSON-index felett — szövegkeresés + több-választós címkeszűrés.
  Nincs külső kereső-szolgáltatás (alkönyvtáron is működik).
- **Visszahivatkozások** (`site/src/lib/queries.ts`): `storiesReferencing`,
  `usageCounts`, `labelMap` — a mesékből számolt „mely mesékben szerepel".
- **Lábléc:** Bartos Erika mint szerző/jogtulajdonos + testvéroldal-link +
  „nem hivatalos" nyilatkozat. Cloudflare Web Analytics (süti nélküli mérés).
