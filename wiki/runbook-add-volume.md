---
type: "Runbook"
title: "Új kötet hozzáadása"
description: "Lépésről lépésre: egy új kötet feldolgozása és publikálása."
tags: ["runbook", "kotet"]
timestamp: "2026-07-05"
---

# Runbook — új kötet hozzáadása

1. **Forrás** a `pdfs/`-be (bármilyen: PDF/DJVU/JPG-mappa). Ellenőrizd, hogy
   tényleg *Anna, Peti, Gergő* kötet-e.
2. **Render:** vedd fel a forrást a `scripts/render_sources.sh`-be (megfelelő
   `render_pdf` / `render_djvu` / `render_jpgdir` hívással), majd futtasd. Ellenőrizd
   a `scratch/pages/<slug>/` oldalszámát.
3. **Kötet-metaadat:** hozz létre `site/src/content/volumes/<slug>.yaml`-t
   (`id, title, series, publisher, description, types`).
4. **Kivonatolás:** indíts egy vízió-ügynököt, amely elolvassa
   `scratch/pages/<slug>/`-t és kiírja `scratch/extract/<slug>.json`-t a
   `scratch/EXTRACTION_GUIDE.md` sémája szerint (meglévő slugok újrahasznosítása,
   magyar összefoglaló, csak metaadat).
5. **Merge:** `python3 scripts/merge_extract.py` → nézd a „No dangling references"-t.
   Ha új hangszer/zöldség/szinonima jött, frissítsd a merge szabálytábláit.
6. **Build:** `cd site && npm run build` (zöldnek kell lennie).
7. **Wiki:** ha a *működés* változott, `python3 scripts/gen_project_wiki.py`.
8. **Release:** commit + push `main` → GitHub Actions deploy.
