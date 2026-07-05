---
type: "Guide"
title: "Anna, Peti, Gergő wiki — a tudáskatalógusról"
description: "Mi ez az OKF-csomag és hogyan tartsd karban."
timestamp: "2026-07-05"
---

# Anna, Peti, Gergő wiki — a tudáskatalógusról

Bartos Erika Anna, Peti, Gergő meséinek nem hivatalos, rajongói referencia-katalógusa — melyik mese melyik kötetben, kik szerepelnek, hol játszódik, miről szól.

Ez a mappa (`wiki/`) egy **OKF (Open Knowledge Format)** tudáscsomag: emberi és
gépi (LLM/ügynök) olvasásra egyaránt alkalmas, verziókövetésben diffelhető
markdown-fájlok YAML frontmatterrel. Minden koncepció (kötet, mese, szereplő,
helyszín, tárgy, téma, évszak, ünnep) külön fájl, kereszthivatkozásokkal.

## Három réteg (Karpathy LLM-wiki mintája)
1. **Nyers források** — a beszkennelt könyvek (`pdfs/`, a repóból kihagyva, jogvédett).
2. **Forrás-igazság** — `site/src/content/` (Zod-sémával validált YAML).
3. **Ez a wiki** — a 2. rétegből *generált*, LLM-barát tudáscsomag.

## Karbantartás
- **Ne szerkeszd kézzel** a `wiki/` fájljait — generált. Módosíts a
  `site/src/content/`-ben, majd futtasd: `python3 scripts/gen_okf_wiki.py`.
- **Ingest** (új kötet): `scratch/extract/*.json` → `scripts/merge_extract.py` →
  `scripts/gen_okf_wiki.py`.
- **Lint**: a build (`npm run build`) elbukik lógó hivatkozáson; a merge
  jelzi a dangling refeket.

## Jogi
Nem hivatalos, rajongói referencia. Szerző és jogtulajdonos: **Bartos Erika**.
Csak metaadat és saját szavas összefoglalók — a mesék szövege/képei nem szerepelnek.

Testvéroldal: [Bogyó és Babóca wiki](https://frkandris.github.io/bogyo-es-baboca-wiki/).
