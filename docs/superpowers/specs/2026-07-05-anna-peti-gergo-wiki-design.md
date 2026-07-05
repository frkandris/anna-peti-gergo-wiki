# Anna, Peti és Gergő Wiki — Design

Date: 2026-07-05

## Goal

A publicly hosted (GitHub Pages) wiki-style catalog of the Bartos Erika "Anna, Peti
és Gergő" book universe. Its purpose: **help parents find which story is in which
volume**, and browse by character, location, object, theme, season, and holiday.
Bartos Erika is prominently credited as author and copyright holder.

## Source material

- 9 scanned PDF books (~2,000 pages total) in `pdfs/` (NOT committed to the repo).
- No text layer (Konica Minolta scans) → vision/OCR required for extraction.
- Each scanned image is a two-page spread; text is clean and legible.
- Two kinds of books:
  - **Collections** (Annakönyv, Petikönyv, Gergőkönyv, Megmondalak, Süss fel Nap!,
    Irány az óvoda/iskola): many short stories per volume.
  - **Single-story books** (Kistestvér érkezik, Nagycsalád lettünk): the whole book
    is one continuous story.

## Key decisions

1. **Content scope (legal): metadata + own-words summaries ONLY.** No verbatim story
   text, no scanned illustrations. This keeps the site a legitimate catalog/index,
   which is both the safest legal footing and exactly what the stated purpose needs.
2. **It's a dataset, not documents.** Source of truth = structured, schema-validated
   data. Every page is *generated* from it, so cross-references ("this character
   appears in these stories") are derived and never drift.
3. **SSG: Astro.** Content collections + Zod schema validation + programmatic page
   generation fit a web of interlinked entity pages far better than a prose-doc tool.
4. **Extraction done by Claude Code / subagents directly** — no separate Python +
   Claude-API pipeline. `pdftoppm` renders pages; agents read them and write YAML.
5. **Sequencing: pilot one volume first** (*Kistestvér érkezik*), stand up the full
   site + deploy, validate schema and look, then process the remaining 8 volumes.

## Data model

Entities (each an Astro content collection, Zod-validated):

- **volume** (`kötet`): id, title, series, publisher, year, description, cover note.
- **story** (`mese`): id, title, volume ref(s), page range, own-words `summary`, and
  reference lists → `characters[]`, `locations[]`, `objects[]`, `vehicles[]`,
  `themes[]`, `seasons[]`, `holidays[]`.
- **character** (`szereplő`): id, name, kind (person/animal/toy), description.
- **location** (`helyszín`): id, name, real-or-fictional, description.
- **object** (`tárgy`): id, name, category (object/vehicle).
- **taxonomy** (`taxonomy.yaml`): controlled vocabulary for themes, seasons, holidays
  — extractors map to canonical terms to avoid synonym explosion (e.g. orvos vs
  doktor néni); a normalization pass dedupes.

Modeling rule: in **collections**, each short story is one `story`; in
**single-story books**, the book itself is one `story`.

Back-references (character→stories, location→stories, theme→stories, etc.) are
**generated** from the story reference lists, never hand-maintained.

## Repository layout

```
pdfs/                      # source PDFs — .gitignored, never committed
site/                      # Astro project
  src/content/             # SOURCE OF TRUTH, Zod-validated
    volumes/  stories/  characters/  locations/  objects/
    taxonomy.yaml
  src/pages/               # generated pages
scripts/render-pages.sh    # pdftoppm helper for extraction
.github/workflows/deploy.yml
docs/superpowers/specs/    # this design
```

## Site pages

- Home: browse by volume + featured filters (themes, life-situations).
- Volume detail: metadata + its stories.
- Story detail: summary + all facet chips linking to entity/filter pages.
- Character / location / object index + detail pages (detail lists referencing stories).
- Filter pages per theme / season / holiday.
- Search: Pagefind (static, works on GitHub Pages).
- Faceted browse: client-side JS filtering over a generated JSON index (combine
  theme + character + season, etc.).
- Language: Hungarian UI.

## Legal / attribution

Every page shows: Bartos Erika as author and copyright holder, publisher credited,
and a "nem hivatalos, referencia/katalógus célú oldal" (unofficial, reference-only)
disclaimer. No verbatim text, no scanned images.

## Deploy

GitHub Actions builds Astro → GitHub Pages. Project-pages URL
(`<username>.github.io/anna-peti-gergo-wiki`); exact `site`/`base` config filled at
deploy time.

## Pilot scope (this iteration)

*Kistestvér érkezik* fully extracted → full Astro site scaffolded with all page types
→ GitHub Actions deploy → verified build. On approval, remaining 8 volumes are
processed in parallel.
