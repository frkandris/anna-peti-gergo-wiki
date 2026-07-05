---
type: "Script"
title: "merge_extract.py — kanonikus szabályok"
description: "Dedup, kanonikus címkék, aliasok, species, tárgy-csoportok, integritás."
tags: ["merge", "python", "normalizalas"]
timestamp: "2026-07-05"
---

# `scripts/merge_extract.py`

Beolvassa az összes `scratch/extract/*.json`-t, és **nulláról újragenerálja** a
`site/src/content/{stories,characters,locations,objects,themes,seasons,holidays}`
kollekciókat (a `volumes` kézzel írt, kimarad). Fő szabálytáblák a script tetején:

- **`CANONICAL_THEME_LABELS` / `CANONICAL_SEASON_LABELS` / `CANONICAL_HOLIDAY_LABELS`**
  — ékezetes címkék, amelyek mindig felülírják az ügynök ékezet nélküli címkéjét
  (ez javította a „Baratsag→Barátság", „Osz→Ősz" hibát).
- **`THEME_ALIASES`** — szinonim témák összevonása kanonikus slugra.
- **`CHARACTER_ALIASES`** — ugyanaz a szereplő több slug alatt → kanonikus id
  (pl. `zold-kukac → kukac`); a story-hivatkozásokat is átírja.
- **`SPECIES`** — szereplő faj/szerep (a név alatt jelenik meg).
- **`CHAR_DESC`** — a főszereplők egységes leírása.
- **`OBJECT_GROUPS`** — tárgy-alcsoportok (Hangszerek, Zöldségek és gyümölcsök,
  Ételek, Ruházat, Természet) id-halmazok szerint. Új hangszert/zöldséget itt kell
  a megfelelő halmazhoz adni.
- **`CATEGORY_OVERRIDES`** — kézi object-kategória (pl. `babakocsi → vehicle`).

Robusztus a JSON-formára: az ügynökök `id`/`slug`, `kind`/`category` és
string- vagy objektum-alakú taxonómia-elemeket is adhatnak.

Végén **referenciaintegritás-ellenőrzés**: minden story-hivatkozásnak fel kell
oldódnia; lógónál figyelmeztet és stubot készít. „No dangling references." a jó kimenet.
