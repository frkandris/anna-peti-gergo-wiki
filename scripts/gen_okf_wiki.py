#!/usr/bin/env python3
"""Generate an OKF (Open Knowledge Format) bundle from the Astro content collections.

Reads  <repo>/site/src/content/{volumes,stories,characters,locations,objects,
                                 themes,seasons,holidays}/*.yaml
Writes <repo>/wiki/  — an OKF-conformant knowledge bundle: index.md, log.md,
about.md (type: Guide) and one concept file per entity, each with YAML
frontmatter and cross-links, plus per-collection index.md files.

Design references:
  - OKF SPEC:  github.com/GoogleCloudPlatform/knowledge-catalog (okf/SPEC.md)
  - LLM-wiki pattern: Andrej Karpathy, gist 442a6bf555914893e9891c11519de94f
    (raw sources -> generated wiki -> schema/how-to layer; ingest/query/lint ops)

The wiki is a *generated, compounding artifact*: the content YAML is the source
of truth, this bundle is regenerated from it — never hand-edit files under wiki/.

Usage: python3 scripts/gen_okf_wiki.py [<repo_root>]   (default: script's repo)
"""
import sys, json, pathlib, datetime

TODAY = datetime.date.today().isoformat()

# ---- per-repo config (keyed by repo dir basename) -------------------------
CONFIG = {
    "bogyo-es-baboca-wiki": {
        "title": "Bogyó és Babóca wiki",
        "base": "https://frkandris.github.io/bogyo-es-baboca-wiki",
        "author": "Bartos Erika",
        "intro": "Bartos Erika Bogyó és Babóca meséinek nem hivatalos, rajongói "
                 "referencia-katalógusa — melyik mese melyik kötetben, kik szerepelnek, "
                 "hol játszódik, miről szól.",
        "sibling": ("Anna, Peti, Gergő wiki", "https://frkandris.github.io/anna-peti-gergo-wiki/"),
    },
    "anna-peti-gergo-wiki": {
        "title": "Anna, Peti, Gergő wiki",
        "base": "https://frkandris.github.io/anna-peti-gergo-wiki",
        "author": "Bartos Erika",
        "intro": "Bartos Erika Anna, Peti, Gergő meséinek nem hivatalos, rajongói "
                 "referencia-katalógusa — melyik mese melyik kötetben, kik szerepelnek, "
                 "hol játszódik, miről szól.",
        "sibling": ("Bogyó és Babóca wiki", "https://frkandris.github.io/bogyo-es-baboca-wiki/"),
    },
}

# collection -> (okf type, url segment, display-name field, plural label)
COLLECTIONS = {
    "volumes":    ("Kötet",    "kotet",    "title", "Kötetek"),
    "stories":    ("Mese",     "mese",     "title", "Mesék"),
    "characters": ("Szereplő", "szereplo", "name",  "Szereplők"),
    "locations":  ("Helyszín", "helyszin", "name",  "Helyszínek"),
    "objects":    ("Tárgy",    "targy",    "name",  "Tárgyak"),
    "themes":     ("Téma",     "tema",     "label", "Témák"),
    "seasons":    ("Évszak",   "evszak",   "label", "Évszakok"),
    "holidays":   ("Ünnep",    "unnep",    "label", "Ünnepek"),
}
REF_FIELDS = ["characters", "locations", "objects", "themes", "seasons", "holidays"]
REF_LABEL = {"characters": "Szereplők", "locations": "Helyszínek", "objects": "Tárgyak",
             "themes": "Témák", "seasons": "Évszakok", "holidays": "Ünnepek"}
REF_COLL = {"characters": "characters", "locations": "locations", "objects": "objects",
            "themes": "themes", "seasons": "seasons", "holidays": "holidays"}

# ---- minimal reader for the emit_yaml format (JSON-quoted scalars) ---------
def parse_yaml(text):
    """Parse the flat YAML emitted by merge_extract.py (scalars + scalar lists)."""
    data, i, lines = {}, 0, text.splitlines()
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1; continue
        if ":" not in line:
            i += 1; continue
        key, _, rest = line.partition(":")
        key = key.strip(); rest = rest.strip()
        if rest == "" :  # list follows on indented lines
            items = []
            j = i + 1
            while j < n and lines[j].lstrip().startswith("- "):
                items.append(_scalar(lines[j].lstrip()[2:].strip()))
                j += 1
            data[key] = items; i = j
        elif rest == "[]":
            data[key] = []; i += 1
        else:
            data[key] = _scalar(rest); i += 1
    return data

def _scalar(s):
    s = s.strip()
    if s.startswith('"') or s.startswith("["):
        try: return json.loads(s)
        except Exception: return s.strip('"')
    if s.lstrip("-").isdigit():
        return int(s)
    return s

def load_collection(content_dir, name):
    d = content_dir / name
    out = {}
    if not d.exists(): return out
    for f in sorted(d.glob("*.yaml")):
        rec = parse_yaml(f.read_text(encoding="utf-8"))
        rec.setdefault("id", f.stem)
        out[rec["id"]] = rec
    return out

# ---- helpers --------------------------------------------------------------
def disp(coll_name, rec):
    field = COLLECTIONS[coll_name][2]
    return rec.get(field) or rec.get("title") or rec.get("name") or rec.get("label") or rec["id"]

def fm(d):
    """Render an ordered YAML frontmatter block."""
    lines = ["---"]
    for k, v in d.items():
        if v is None or v == "": continue
        if isinstance(v, list):
            if not v: continue
            lines.append(f"{k}: [{', '.join(json.dumps(x, ensure_ascii=False) for x in v)}]")
        else:
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)

def link(coll_name, rec_id, label):
    return f"[{label}](/{coll_name}/{rec_id}.md)"

def main():
    repo = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
           pathlib.Path(__file__).resolve().parents[1]
    cfg = CONFIG.get(repo.name)
    if not cfg:
        sys.exit(f"No CONFIG for repo '{repo.name}' — add it to gen_okf_wiki.py")
    content = repo / "site" / "src" / "content"
    wiki = repo / "wiki"

    coll = {name: load_collection(content, name) for name in COLLECTIONS}
    stories = coll["stories"]

    # back-references: for each referenced entity, which stories point at it
    backref = {name: {} for name in REF_COLL.values()}
    for sid, s in stories.items():
        for fld in REF_FIELDS:
            for rid in s.get(fld, []):
                backref[REF_COLL[fld]].setdefault(rid, []).append(sid)

    # fresh bundle
    if wiki.exists():
        for f in wiki.rglob("*.md"):
            f.unlink()
    wiki.mkdir(parents=True, exist_ok=True)

    def write(relpath, text):
        p = wiki / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text.rstrip() + "\n", encoding="utf-8")

    # ---------- concept files ----------
    for name, (otype, seg, _field, _plural) in COLLECTIONS.items():
        for rid, rec in coll[name].items():
            title = disp(name, rec)
            desc = rec.get("description") or rec.get("summary") or ""
            body_desc = desc
            tags = []
            front = {"type": otype, "title": title}
            if desc: front["description"] = desc.split(". ")[0][:180]
            front["resource"] = f"{cfg['base']}/{seg}/{rid}"
            body = [f"# {title}", ""]

            if name == "stories":
                vol = coll["volumes"].get(rec.get("volume"))
                if vol:
                    body.append(f"**Kötet:** {link('volumes', vol['id'], vol.get('title', vol['id']))}")
                if rec.get("pageStart"):
                    body.append(f"**Oldal:** {rec.get('pageStart')}–{rec.get('pageEnd','')}")
                body.append("")
                if body_desc: body += [body_desc, ""]
                tags = list(rec.get("themes", [])) + list(rec.get("seasons", [])) + list(rec.get("holidays", []))
                for fld in REF_FIELDS:
                    ids = rec.get(fld, [])
                    if not ids: continue
                    body.append(f"## {REF_LABEL[fld]}")
                    for rid2 in ids:
                        c2 = REF_COLL[fld]
                        lbl = disp(c2, coll[c2].get(rid2, {"id": rid2}))
                        body.append(f"- {link(c2, rid2, lbl)}")
                    body.append("")
                body += ["# Citations",
                         f"[1] {cfg['author']}: {coll['volumes'].get(rec.get('volume'),{}).get('title','')} "
                         f"(a kötet meséje; csak metaadat és saját összefoglaló)."]

            elif name == "volumes":
                meta = " · ".join(x for x in [rec.get("series"), rec.get("publisher")] if x)
                if meta: body += [f"*{meta}*", ""]
                if body_desc: body += [body_desc, ""]
                vstories = sorted([s for s in stories.values() if s.get("volume") == rid],
                                  key=lambda s: s.get("order", 0))
                body.append(f"## Mesék ({len(vstories)})")
                for s in vstories:
                    sd = (s.get("summary") or "").split(". ")[0]
                    body.append(f"- {link('stories', s['id'], s.get('title', s['id']))} — {sd}")

            else:  # entity / taxonomy pages
                sub = []
                if rec.get("species"): sub.append(rec["species"])
                if rec.get("category") == "vehicle": sub.append("jármű")
                if rec.get("group"): sub.append(rec["group"])
                if sub: body += [f"*{' · '.join(sub)}*", ""]
                if body_desc: body += [body_desc, ""]
                refs = backref[name].get(rid, [])
                body.append(f"## Mesék ({len(refs)})")
                for sid in sorted(refs, key=lambda x: (stories[x].get("volume",""), stories[x].get("order",0))):
                    s = stories[sid]
                    body.append(f"- {link('stories', sid, s.get('title', sid))}")
                front["tags"] = []

            front["timestamp"] = TODAY
            if tags: front["tags"] = list(dict.fromkeys(tags))
            write(f"{name}/{rid}.md", fm(front) + "\n\n" + "\n".join(body))

        # per-collection index.md
        idx = [f"# {COLLECTIONS[name][3]}", ""]
        entries = sorted(coll[name].values(), key=lambda r: disp(name, r).lower())
        for rec in entries:
            rid = rec["id"]
            d = (rec.get("description") or rec.get("summary") or "").split(". ")[0]
            cnt = len(backref[name].get(rid, [])) if name in backref else \
                  (len([s for s in stories.values() if s.get("volume") == rid]) if name == "volumes" else None)
            suffix = f" — {d}" if d else ""
            if cnt is not None and name != "stories":
                suffix = f" ({cnt} mese)" + suffix
            idx.append(f"* [{disp(name, rec)}]({rid}.md){suffix}")
        write(f"{name}/index.md", "\n".join(idx))

    # ---------- about.md (schema / how-to layer, Karpathy style) ----------
    about = f"""{fm({"type": "Guide", "title": f"{cfg['title']} — a tudáskatalógusról",
                     "description": "Mi ez az OKF-csomag és hogyan tartsd karban.",
                     "timestamp": TODAY})}

# {cfg['title']} — a tudáskatalógusról

{cfg['intro']}

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
Nem hivatalos, rajongói referencia. Szerző és jogtulajdonos: **{cfg['author']}**.
Csak metaadat és saját szavas összefoglalók — a mesék szövege/képei nem szerepelnek.

Testvéroldal: [{cfg['sibling'][0]}]({cfg['sibling'][1]}).
"""
    write("about.md", about)

    # ---------- top-level index.md ----------
    top = [f"# {cfg['title']} — tudáskatalógus", "", cfg["intro"], "",
           f"* [Erről a katalógusról](about.md)", ""]
    for name, (_t, _s, _f, plural) in COLLECTIONS.items():
        top.append(f"* [{plural}]({name}/) — {len(coll[name])} db")
    top += ["", "## Kiemelt mesék"]
    for s in sorted(stories.values(), key=lambda s: (s.get("volume",""), s.get("order",0)))[:8]:
        d = (s.get("summary") or "").split(". ")[0]
        top.append(f"* [{s.get('title', s['id'])}](stories/{s['id']}.md) — {d}")
    write("index.md", "\n".join(top))

    # ---------- log.md ----------
    counts = " · ".join(f"{len(coll[n])} {COLLECTIONS[n][3].lower()}" for n in COLLECTIONS)
    log = f"""# Változásnapló

## {TODAY}
* **Inicializálás**: OKF tudáskatalógus generálva a forrás-tartalomból ({counts}).
"""
    write("log.md", log)

    total = sum(len(coll[n]) for n in COLLECTIONS)
    print(f"OKF bundle written to {wiki}  ({total} concept files across {len(COLLECTIONS)} collections)")

if __name__ == "__main__":
    main()
