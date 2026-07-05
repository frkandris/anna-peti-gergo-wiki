---
type: "Reference"
title: "Repo-felépítés"
description: "A repó könyvtárszerkezete és mi hol található."
tags: ["struktura"]
timestamp: "2026-07-05"
---

# Repo-felépítés

```
pdfs/                      # forrás szkennek — GITIGNORE, jogvédett, sosem commitolt
scripts/
  render_sources.sh        # források → PNG oldalképek (scratch/pages/<slug>/)
  merge_extract.py         # scratch/extract/*.json → site/src/content/*.yaml
  gen_project_wiki.py      # EZT a wiki/ mappát generálja
scratch/                   # GITIGNORE — extrakciós munkakönyvtár
  pages/<slug>/            # renderelt oldalképek
  extract/<slug>.json      # ügynökönkénti/kötetenkénti nyers kivonat
  EXTRACTION_GUIDE.md      # az ügynököknek szóló séma + szótár
site/                      # Astro projekt
  src/content/             # ← FORRÁS-IGAZSÁG (Zod-validált YAML)
    volumes/ stories/ characters/ locations/ objects/ themes/ seasons/ holidays/
  src/content.config.ts    # Zod sémák + reference() integritás
  src/pages/               # generált oldalak (getStaticPaths)
  src/lib/queries.ts       # visszahivatkozás-számítás
  src/lib/site.ts          # base-path-tudatos URL-ek, címkék
  src/components/  src/layouts/  src/styles/
.github/workflows/deploy.yml  # Actions → GitHub Pages
wiki/                      # EZ a projekt/tech LLM-wiki (OKF)
```

Forrás-formátumok ennél a repónál: beszkennelt PDF oldalpárok (spread-enként egy kép), vízió/OCR-rel olvasva.
