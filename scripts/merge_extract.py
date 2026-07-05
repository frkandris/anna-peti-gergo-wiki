#!/usr/bin/env python3
"""Merge ALL per-batch extraction JSON into Astro content collection YAML files.

Reads every scratch/extract/*.json (one file per subagent batch, across all
volumes), then regenerates the entity/story/taxonomy collections from scratch so
the result is deterministic and idempotent. Volume YAMLs are hand-authored and
never touched.

- Dedups entities by id (prefers the richest description), globally across volumes.
- Resolves object category conflicts via CATEGORY_OVERRIDES.
- Forces canonical name/description/category for specific ids via ENTITY_OVERRIDES.
- Verifies every story reference resolves to an entity; stubs + warns on dangling.
- Emits dependency-free YAML (JSON-quoted scalars are valid YAML).
"""
import json, sys, pathlib, glob

ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = ROOT / "scratch" / "extract"
CONTENT = ROOT / "site" / "src" / "content"

# generated collections (volumes are hand-authored, excluded)
GENERATED = ["stories", "characters", "locations", "objects", "themes", "seasons", "holidays"]

# object id -> forced category when batches disagree
CATEGORY_OVERRIDES = {"babakocsi": "vehicle"}

# theme slug aliases -> canonical slug (merges synonym themes)
THEME_ALIASES = {
    "iskolakezdes": "iskola-kezdes",
    "ovoda-kezdes": "ovoda",
    "onallosodas": "onallosag",
    "harag": "duh",
    "testvervita": "testverfeltekenyseg",
}
# canonical labels for the merge targets (so an alias's label can't pollute them)
CANONICAL_THEME_LABELS = {
    "iskola-kezdes": "Iskolakezdés",
    "ovoda": "Óvoda",
    "onallosag": "Önállóság",
    "duh": "Düh",
    "testverfeltekenyseg": "Testvérféltékenység",
}

# id -> forced fields (applied after dedup). Keeps entities canonical across volumes.
ENTITY_OVERRIDES = {
    # The family's own red car — a distinct entity from the toy car (kisauto).
    "auto": {"name": "Piros autó", "category": "vehicle",
             "description": "A család saját piros autója, amivel kirándulni és nyaralni járnak."},
    "kisauto": {"name": "Kisautó (játék)", "category": "vehicle",
                "description": "Játékautó a gyerekek játékai között."},
}

def q(s): return json.dumps(str(s), ensure_ascii=False)

def emit_yaml(obj):
    """Minimal YAML for flat dicts with scalar or list-of-scalar values."""
    lines = []
    for k, v in obj.items():
        if v is None: continue
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for it in v:
                    lines.append(f"  - {q(it)}")
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {q(v)}")
    return "\n".join(lines) + "\n"

def better(a, b):
    """Pick the entity dict with the longer description."""
    if a is None: return b
    if b is None: return a
    la = len(a.get("description") or "")
    lb = len(b.get("description") or "")
    return a if la >= lb else b

def load():
    batches = []
    for p in sorted(EX.glob("*.json")):
        batches.append(json.loads(p.read_text(encoding="utf-8")))
    if not batches:
        sys.exit("No batch JSON files found in scratch/extract/")
    return batches

def main():
    batches = load()
    stories, chars, locs, objs = [], {}, {}, {}
    themes, seasons, holidays = {}, {}, {}

    for b in batches:
        stories.extend(b["stories"])
        for c in b["entities"].get("characters", []):
            chars[c["id"]] = better(chars.get(c["id"]), c)
        for l in b["entities"].get("locations", []):
            locs[l["id"]] = better(locs.get(l["id"]), l)
        for o in b["entities"].get("objects", []):
            objs[o["id"]] = better(objs.get(o["id"]), o)
        for t in b["taxonomy"].get("themes", []):
            slug = THEME_ALIASES.get(t["slug"], t["slug"])
            label = CANONICAL_THEME_LABELS.get(slug, t["label"])
            themes.setdefault(slug, label)
        for s in b["taxonomy"].get("seasons", []):
            seasons.setdefault(s["slug"], s["label"])
        for h in b["taxonomy"].get("holidays", []):
            holidays.setdefault(h["slug"], h["label"])

    # category overrides
    for oid, cat in CATEGORY_OVERRIDES.items():
        if oid in objs: objs[oid]["category"] = cat

    # entity field overrides (canonical name/desc/category)
    for tbl in (chars, locs, objs):
        for eid, fields in ENTITY_OVERRIDES.items():
            if eid in tbl:
                tbl[eid] = {**tbl[eid], **fields}

    # apply theme aliases to story references (dedup, preserve order)
    for s in stories:
        s["themes"] = list(dict.fromkeys(THEME_ALIASES.get(t, t) for t in s.get("themes", [])))
    # canonical labels win even if a canonical theme already existed with a weaker label
    for slug, label in CANONICAL_THEME_LABELS.items():
        if slug in themes:
            themes[slug] = label

    stories.sort(key=lambda s: (s.get("volume", ""), s.get("order", 0)))

    # referential integrity check + stubs
    warnings = []
    def ensure(refs, table, kind):
        for rid in refs:
            if rid not in table:
                warnings.append(f"  {kind}: dangling ref '{rid}' — stub created")
                table[rid] = {"id": rid, "name": rid.replace("-", " ").title(),
                              "kind": "other" if kind == "characters" else "real",
                              "category": "object"}
    for s in stories:
        ensure(s["characters"], chars, "characters")
        ensure(s["locations"], locs, "locations")
        ensure(s["objects"], objs, "objects")
        for th in s["themes"]: themes.setdefault(th, th.replace("-", " ").capitalize())
        for se in s["seasons"]: seasons.setdefault(se, se.capitalize())
        for ho in s["holidays"]: holidays.setdefault(ho, ho.capitalize())

    # clear generated dirs so removed/renamed ids don't linger
    for dirname in GENERATED:
        d = CONTENT / dirname
        if d.exists():
            for f in d.glob("*.yaml"):
                f.unlink()

    # write files
    def write(dirname, entries, key="id"):
        d = CONTENT / dirname
        d.mkdir(parents=True, exist_ok=True)
        for e in entries:
            (d / f"{e[key]}.yaml").write_text(emit_yaml(e), encoding="utf-8")

    write("stories", stories)
    write("characters", [{"id": k, **{kk: vv for kk, vv in v.items() if kk != "id"}} for k, v in chars.items()])
    write("locations", [{"id": k, **{kk: vv for kk, vv in v.items() if kk != "id"}} for k, v in locs.items()])
    write("objects", [{"id": k, **{kk: vv for kk, vv in v.items() if kk != "id"}} for k, v in objs.items()])
    write("themes", [{"id": k, "label": v} for k, v in themes.items()])
    write("seasons", [{"id": k, "label": v} for k, v in seasons.items()])
    write("holidays", [{"id": k, "label": v} for k, v in holidays.items()])

    print(f"stories={len(stories)} characters={len(chars)} locations={len(locs)} "
          f"objects={len(objs)} themes={len(themes)} seasons={len(seasons)} holidays={len(holidays)}")
    if warnings:
        print("WARNINGS:")
        print("\n".join(warnings))
    else:
        print("No dangling references.")

if __name__ == "__main__":
    main()
