#!/usr/bin/env python3
"""Generate the project/tech LLM wiki (OKF bundle) for a Bartos-Erika wiki repo.

This is a knowledge base ABOUT THE PROJECT AND HOW THE TECH WORKS — for an
LLM/agent (or human) that needs to work on the repo. It does NOT catalog the
fairy-tale content (that is the website itself).

Format: OKF (Open Knowledge Format) — markdown concept files with YAML
frontmatter, index.md, log.md. Pattern: Andrej Karpathy's LLM-wiki (raw layer
= the code/PDFs, source-of-truth = site/src/content, this wiki = the how-it-works
layer that compounds over time).

The prose is identical across both repos (shared tech); only the title, series,
base URL, sibling link and a few live counts differ, filled from CONFIG + content.

Usage: python3 scripts/gen_project_wiki.py [<repo_root>]
"""
import sys, pathlib, datetime, re

TODAY = datetime.date.today().isoformat()

CONFIG = {
    "bogyo-es-baboca-wiki": {
        "title": "Bogyó és Babóca wiki",
        "series": "Bogyó és Babóca",
        "base": "https://frkandris.github.io/bogyo-es-baboca-wiki",
        "sibling": ("Anna, Peti, Gergő wiki", "https://github.com/frkandris/anna-peti-gergo-wiki"),
        "sources": "PDF, DJVU és JPG-szkennek (`scripts/render_sources.sh` mindet PNG-vé renderel)",
    },
    "anna-peti-gergo-wiki": {
        "title": "Anna, Peti, Gergő wiki",
        "series": "Anna, Peti, Gergő",
        "base": "https://frkandris.github.io/anna-peti-gergo-wiki",
        "sibling": ("Bogyó és Babóca wiki", "https://github.com/frkandris/bogyo-es-baboca-wiki"),
        "sources": "beszkennelt PDF oldalpárok (spread-enként egy kép), vízió/OCR-rel olvasva",
    },
}

COLLS = ["volumes", "stories", "characters", "locations", "objects", "themes", "seasons", "holidays"]


def counts(repo):
    c = {}
    base = repo / "site" / "src" / "content"
    for name in COLLS:
        d = base / name
        c[name] = len(list(d.glob("*.yaml"))) if d.exists() else 0
    return c


def fm(type_, title, description, tags):
    lines = ["---", f'type: "{type_}"', f'title: "{title}"',
             f'description: "{description}"']
    if tags:
        lines.append("tags: [" + ", ".join(f'"{t}"' for t in tags) + "]")
    lines.append(f'timestamp: "{TODAY}"')
    lines.append("---")
    return "\n".join(lines)


def doc(type_, title, desc, tags, body):
    return fm(type_, title, desc, tags) + "\n\n" + body.strip() + "\n"


def build(repo):
    cfg = CONFIG.get(repo.name)
    if not cfg:
        sys.exit(f"No CONFIG for repo '{repo.name}'")
    c = counts(repo)
    T, S = cfg["title"], cfg["series"]
    sib_name, sib_url = cfg["sibling"]
    wiki = repo / "wiki"
    if wiki.exists():
        for f in wiki.glob("*.md"):
            f.unlink()
    wiki.mkdir(parents=True, exist_ok=True)

    def w(name, text):
        (wiki / name).write_text(text.rstrip() + "\n", encoding="utf-8")

    # ---------------- about.md (Karpathy "schema" / how-to-maintain layer) ----
    w("about.md", doc(
        "Guide", f"{T} — a tudáskatalógusról (LLM wiki)",
        "Mi ez a wiki/ mappa, mire való, és hogyan tartsd karban.",
        ["meta", "okf", "karbantartas"],
        f"""# {T} — a tudáskatalógusról (LLM wiki)

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

Testvér-repó: [{sib_name}]({sib_url}) — ugyanez a tech, közös pipeline.
"""))

    # ---------------- overview.md --------------------------------------------
    w("overview.md", doc(
        "Overview", f"{T} — áttekintés",
        f"Statikus, kereshető katalógus Bartos Erika {S} meséiről.",
        ["projekt", "cel", "jog"],
        f"""# {T} — áttekintés

Statikus, kereshető **rajongói referencia-katalógus** Bartos Erika *{S}*
könyveiről. Fő cél: a szülők gyorsan megtalálják, **melyik mese melyik kötetben**
van, és böngészhessenek szereplő, helyszín, tárgy, téma, évszak és ünnep szerint.

Jelenlegi méret: **{c['volumes']} kötet · {c['stories']} mese · {c['characters']}
szereplő · {c['locations']} helyszín · {c['objects']} tárgy · {c['themes']} téma**.

## Alapelvek
- **Csak metaadat + saját szavas összefoglaló.** Bartos Erika a szerző és a
  jogtulajdonos; a mesék szövege és képei **nem** kerülnek a repóba vagy a
  weboldalra. A forrás-PDF-ek gitignore-oltak. Lásd [conventions](conventions.md).
- **Statikus.** Nincs backend, nincs adatbázis — Astro build → GitHub Pages.
- **Adathalmaz, nem dokumentumok.** A forrás-igazság strukturált YAML; minden
  oldal generált. Lásd [architecture](architecture.md).

Élő oldal: {cfg['base']}/
"""))

    # ---------------- architecture.md ----------------------------------------
    w("architecture.md", doc(
        "Architecture", "Architektúra — adathalmaz, nem dokumentumok",
        "Astro content collections + Zod séma; minden oldal generált, a kereszthivatkozások levezetettek.",
        ["astro", "zod", "content-collections"],
        f"""# Architektúra — „adathalmaz, nem dokumentumok"

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
"""))

    # ---------------- repo-structure.md --------------------------------------
    w("repo-structure.md", doc(
        "Reference", "Repo-felépítés",
        "A repó könyvtárszerkezete és mi hol található.",
        ["struktura"],
        f"""# Repo-felépítés

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

Forrás-formátumok ennél a repónál: {cfg['sources']}.
"""))

    # ---------------- data-model.md ------------------------------------------
    w("data-model.md", doc(
        "Reference", "Adatmodell és kontrollált szótár",
        "Entitások, mezők, slug/címke konvenció, kontrollált szótár.",
        ["schema", "szotar", "slug"],
        f"""# Adatmodell és kontrollált szótár

## Entitások (kollekciók)
- **volumes** (kötet): `id, title, series, publisher, description, types[]`.
  Kézzel írt (nem generált a merge által).
- **stories** (mese): `id, title, volume(ref), order, pageStart, pageEnd,
  summary, characters[], locations[], objects[], themes[], seasons[], holidays[]`.
- **characters**: `id, name, kind (person|animal|toy|other), description?,
  species?` — a `species` a név alatt jelenik meg (pl. Bogyó → *Csigafiú*).
- **locations**: `id, name, description?`.
- **objects**: `id, name, description?, category (object|vehicle), group?` — a
  `group` tárgy-alcsoport (Hangszerek, Zöldségek…), a merge tölti ki.
- **themes / seasons / holidays**: `id, label` — kontrollált szótár.

## Slug ⇄ címke konvenció (FONTOS)
- **slug/id: ékezet nélküli, kisbetűs, kötőjeles ASCII** (`sutes-fozes`).
- **megjelenő címke (title/name/label): ékezetes magyar** (`Sütés-főzés`).
- Az ügynökök néha ékezet nélküli slugból gyártanak címkét → ezt a
  [merge-script](merge-script.md) `CANONICAL_*_LABELS` térképe javítja.

## Modellezési döntés
Gyűjteményes kötetnél minden rövid mese külön `story`; egytörténetes könyvnél a
könyv egyetlen `story`. Kétsztoris kötetnél két `story` egy `volume` alatt.
"""))

    # ---------------- pipeline-extraction.md ---------------------------------
    w("pipeline-extraction.md", doc(
        "Pipeline", "Extrakciós pipeline",
        "PDF/DJVU/JPG → PNG oldalkép → vízió-ügynök → JSON → merge → content YAML.",
        ["extrakcio", "agents", "render"],
        f"""# Extrakciós pipeline

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
"""))

    # ---------------- merge-script.md ----------------------------------------
    w("merge-script.md", doc(
        "Script", "merge_extract.py — kanonikus szabályok",
        "Dedup, kanonikus címkék, aliasok, species, tárgy-csoportok, integritás.",
        ["merge", "python", "normalizalas"],
        """# `scripts/merge_extract.py`

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
"""))

    # ---------------- site-astro.md ------------------------------------------
    w("site-astro.md", doc(
        "Reference", "Astro oldal — oldalak, kereső, szűrők",
        "Az oldalgeneráló Astro projekt felépítése és a kliensoldali kereső/szűrő.",
        ["astro", "kereso", "szuro"],
        f"""# Astro oldal

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
"""))

    # ---------------- deploy.md -----------------------------------------------
    w("deploy.md", doc(
        "Runbook", "Deploy — GitHub Actions → Pages",
        "Hogyan épül és publikálódik az oldal.",
        ["deploy", "github-actions", "pages"],
        f"""# Deploy

- **Trigger:** push a `main`-re (`.github/workflows/deploy.yml`), vagy manuális
  `workflow_dispatch`.
- **Lépések:** Node telepítés → `npm ci` a `site/`-ban → `npm run build` →
  a `site/dist` feltöltése GitHub Pages-artifactként → deploy.
- **URL:** {cfg['base']}/ (project pages, base = a repó neve).
- **Ellenőrzés:** a build lógó hivatkozáson elbukik → a hibás content nem megy ki.
- **Analytics:** Cloudflare Web Analytics beacon (süti nélkül).

Kézi build lokálisan: `cd site && npm install && npm run build && npm run preview`.
"""))

    # ---------------- conventions.md -----------------------------------------
    w("conventions.md", doc(
        "Convention", "Konvenciók",
        "Ékezetek, slugok, csak-metaadat/jog, magyar UI.",
        ["konvencio", "jog", "ekezetek"],
        f"""# Konvenciók

- **Csak metaadat + saját összefoglaló.** Semmi szó szerinti mesekép/szöveg. A
  `pdfs/` gitignore-olt. A summary mindig a mi megfogalmazásunk.
- **Ékezetek:** a megjelenő szöveg (title/name/label/summary) **ékezetes magyar**;
  a slug/id **ékezet nélküli ASCII**. A merge kanonikus térképe őrzi ezt.
- **Slug-forma:** kisbetű, kötőjel, ékezet nélkül (`sutes-fozes`, `sun-soma`).
- **Szótár-újrahasznosítás:** új kötetnél a meglévő szereplő/helyszín/téma
  slugokat kell újrahasználni (lásd `scratch/EXTRACTION_GUIDE.md`), különben
  szinonima-robbanás lesz.
- **Magyar UI és branding:** a sorozatnév pontosan „{S}".
- **Attribúció:** minden oldalon Bartos Erika mint szerző és jogtulajdonos.
"""))

    # ---------------- runbook-add-volume.md ----------------------------------
    w("runbook-add-volume.md", doc(
        "Runbook", "Új kötet hozzáadása",
        "Lépésről lépésre: egy új kötet feldolgozása és publikálása.",
        ["runbook", "kotet"],
        f"""# Runbook — új kötet hozzáadása

1. **Forrás** a `pdfs/`-be (bármilyen: PDF/DJVU/JPG-mappa). Ellenőrizd, hogy
   tényleg *{S}* kötet-e.
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
"""))

    # ---------------- index.md (reserved) ------------------------------------
    w("index.md", f"""# {T} — projekt/tech tudáskatalógus

Ez a `wiki/` a **projekt és a technikai működés** LLM-barát tudásbázisa (OKF).
Nem a mesetartalmat katalogizálja — azt a weboldal teszi.

* [Erről a katalógusról](about.md) — mi ez, hogyan tartsd karban
* [Áttekintés](overview.md) — {c['volumes']} kötet · {c['stories']} mese · cél · jog
* [Architektúra](architecture.md) — adathalmaz, nem dokumentumok
* [Repo-felépítés](repo-structure.md)
* [Adatmodell](data-model.md) — entitások, szótár, slug/címke
* [Extrakciós pipeline](pipeline-extraction.md)
* [Merge script](merge-script.md)
* [Astro oldal](site-astro.md)
* [Deploy](deploy.md)
* [Konvenciók](conventions.md)
* [Runbook: új kötet](runbook-add-volume.md)
""")

    # ---------------- log.md (reserved) --------------------------------------
    w("log.md", f"""# Változásnapló

## {TODAY}
* **Inicializálás**: projekt/tech LLM-wiki (OKF) létrehozva — architektúra,
  pipeline, merge, Astro, deploy, konvenciók, runbook.
""")

    n = len(list(wiki.glob("*.md")))
    print(f"Project wiki written to {wiki}  ({n} concept files)")


def main():
    repo = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
           pathlib.Path(__file__).resolve().parents[1]
    build(repo)


if __name__ == "__main__":
    main()
