---
type: "Architecture"
title: "Architektúra — adathalmaz, nem dokumentumok"
description: "Astro content collections + Zod séma; minden oldal generált, a kereszthivatkozások levezetettek."
tags: ["astro", "zod", "content-collections"]
timestamp: "2026-07-05"
---

# Architektúra — „adathalmaz, nem dokumentumok"

A rendszer szíve egy kis **relációs adathalmaz**, nem dokumentumhalmaz.

- **Forrás-igazság:** `site/src/content/` — Zod-sémával (`content.config.ts`)
  validált YAML fájlok, kollekciónként (kötet, mese, szereplő, …).
- **Kapcsolatok:** a mese `volume: reference('volumes')` mezője és a
  `characters/locations/objects/themes/seasons/holidays` slug-listák. Az Astro
  `reference()` **build-időben ellenőrzi** a hivatkozásokat — lógó hivatkozás =
  bukott build (ingyen integritás-ellenőrzés).
- **Levezetett kereszthivatkozások:** „X szereplő mely mesékben szerepel" nem
  kézzel karbantartott — a `site/src/lib/queries.ts` számolja a mesékből. Soha
  nem drift-el.
- **Minden oldal generált:** a `src/pages/**/[id].astro` `getStaticPaths`-szal
  gyárt kötet-, mese-, szereplő-, helyszín-, tárgy-, téma-, évszak- és
  ünnepoldalt.

Következmény: új mese felvételéhez csak **adatot** írsz; az összes visszahivatkozó
oldal és index automatikusan frissül. Lásd [data-model](data-model.md) és
[site-astro](site-astro.md).
