---
type: "Guide"
title: "Anna, Peti, Gergő wiki — a tudáskatalógusról (LLM wiki)"
description: "Mi ez a wiki/ mappa, mire való, és hogyan tartsd karban."
tags: ["meta", "okf", "karbantartas"]
timestamp: "2026-07-05"
---

# Anna, Peti, Gergő wiki — a tudáskatalógusról (LLM wiki)

Ez a `wiki/` mappa a **projekt és a technikai működés** LLM-barát tudásbázisa —
annak, aki (ember vagy ügynök) a repón dolgozik. **Nem** a mesetartalmat
katalogizálja; azt maga a weboldal teszi (`site/`).

Formátum: **OKF (Open Knowledge Format)** — markdown + YAML frontmatter, minden
koncepció külön fájl. Minta: Andrej Karpathy LLM-wiki gondolata, három réteggel:

1. **Nyers réteg** — a forráskód és a jogvédett szkennek (`pdfs/`, gitignore).
2. **Forrás-igazság** — `site/src/content/` (Zod-sémával validált YAML), lásd
   [data-model](data-model.md).
3. **Ez a wiki** — a *hogyan-működik* réteg, ami az idővel bővül.

## Tartalom
- [Áttekintés](overview.md) — mi ez a projekt, célok, jog
- [Architektúra](architecture.md) — „adathalmaz, nem dokumentumok"
- [Repo-felépítés](repo-structure.md)
- [Adatmodell](data-model.md) — entitások, szótár, slug/címke konvenció
- [Extrakciós pipeline](pipeline-extraction.md) — PDF → oldalkép → ügynök → JSON
- [Merge script](merge-script.md) — `merge_extract.py` kanonikus szabályai
- [Astro oldal](site-astro.md) — oldalak, kereső, szűrők
- [Deploy](deploy.md) — GitHub Actions → Pages
- [Konvenciók](conventions.md) — ékezetek, slugok, csak-metaadat
- [Runbook: új kötet hozzáadása](runbook-add-volume.md)

## Karbantartás
Ha a projekt működése változik (script, séma, pipeline), **frissítsd az érintett
koncepció-fájlt** ebben a mappában. A repo-specifikus számokat és a vázat a
`scripts/gen_project_wiki.py` generálja — a prózát abban a scriptben szerkeszd,
majd futtasd: `python3 scripts/gen_project_wiki.py`.

Testvér-repó: [Bogyó és Babóca wiki](https://github.com/frkandris/bogyo-es-baboca-wiki) — ugyanez a tech, közös pipeline.
