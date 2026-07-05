---
type: "Pipeline"
title: "Extrakciós pipeline"
description: "PDF/DJVU/JPG → PNG oldalkép → vízió-ügynök → JSON → merge → content YAML."
tags: ["extrakcio", "agents", "render"]
timestamp: "2026-07-05"
---

# Extrakciós pipeline

A szkennekben **nincs szövegréteg**, ezért vízió (kép-olvasás) kell. A folyamat:

1. **Render** — `scripts/render_sources.sh` minden forrást PNG oldalképpé alakít
   (`pdftoppm`; DJVU `ddjvu -format=pdf`-en át; JPG `sips` resample) ide:
   `scratch/pages/<slug>/p-*.png`. Így az ügynökök csak képeket olvasnak — nincs
   per-ügynök tooling, és egy megszakadt render nem visz magával adatot.
2. **Kivonatolás** — kötetenként egy **vízió-ügynök** (párhuzamosan, háttérben):
   elolvassa az oldalképeket, felismeri a mesehatárokat (címoldalak), és kiírja a
   strukturált metaadatot + **saját szavas magyar** összefoglalót ide:
   `scratch/extract/<slug>.json`. Az ügynökök a `scratch/EXTRACTION_GUIDE.md`
   sémáját és a meglévő szótárt (slugok újrahasznosítása) követik.
3. **Merge** — `scripts/merge_extract.py` az összes JSON-t egyesíti, deduplikál,
   javítja a címkéket, integritást ellenőriz, és kiírja a
   `site/src/content/**`-t. Lásd [merge-script](merge-script.md).
4. **Build** — `npm run build` (`site/`); lógó hivatkozásnál elbukik.

## Buktatók / tanulságok
- **Duplikátumok:** ugyanaz a mese két forrásmappában is lehet (pl. „Boszorkányok"
  külön szkennben és egy másik kötet végén). Merge/kézi dedup kell.
- **Nem oda tartozó forrás:** figyelj, hogy tényleg a sorozat kötete-e (volt
  tévesen bekevert könyv).
- **Csak-magyar összefoglaló:** korábban becsúszott angol summary — a promptban
  nyomatékosítva, merge után grep-pel ellenőrizve.
