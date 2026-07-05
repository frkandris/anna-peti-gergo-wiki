#!/usr/bin/env python3
"""Merge duplicate character entries in the Astro content (same person, multiple slugs).

Groups by identical display name, plus explicit cross-name pairs (same person shown
under different names). Rewrites story references, dedups story lists, keeps the
fullest description, deletes the redundant character files.
"""
import pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "site/src/content/characters"
ST = ROOT / "site/src/content/stories"

# explicit "same person, different display name" merges: alias id -> canonical id
EXPLICIT = {"doktor": "elemer-doktor", "attila": "attila-papa"}
# preferred canonical id when a name-group must choose
CANON_PREF = {"Elemér doktor": "elemer-doktor", "Attila papa": "attila-papa"}

def field(text, key):
    m = re.search(rf'{key}:\s*"(.*)"', text)
    return m.group(1) if m else ""

chars = {}
for f in CH.glob("*.yaml"):
    t = f.read_text(encoding="utf-8")
    chars[f.stem] = {"name": field(t, "name"), "kind": field(t, "kind") or "person",
                     "desc": field(t, "description"), "file": f}

story_text = {f: f.read_text(encoding="utf-8") for f in ST.glob("*.yaml")}
def refcount(cid):
    return sum(1 for t in story_text.values() if f'"{cid}"' in t)

# groups keyed by canonical target
name_groups = collections.defaultdict(set)
for cid, d in chars.items():
    name_groups[d["name"]].add(cid)
# fold explicit aliases into the target's name group
for a, c in EXPLICIT.items():
    if a in chars and c in chars:
        name_groups[chars[c]["name"]].update({a, c})

alias = {}          # alias id -> canonical id
for name, ids in name_groups.items():
    ids = [i for i in ids if i in chars]
    if len(ids) <= 1:
        continue
    canon = CANON_PREF.get(name)
    if canon not in ids:
        canon = max(ids, key=lambda i: (refcount(i), len(i)))
    for i in ids:
        if i != canon:
            alias[i] = canon

if not alias:
    print("no duplicates found"); raise SystemExit

print("MERGE PLAN:")
for a, c in sorted(alias.items()):
    print(f"  {a!r} ({chars[a]['name']}) -> {c!r}")

# update canonical files: keep name, use fullest description in the group
canon_groups = collections.defaultdict(list)
for a, c in alias.items():
    canon_groups[c].append(a)
for c, aliases in canon_groups.items():
    grp = [c] + aliases
    best = max((chars[i]["desc"] for i in grp), key=len)
    chars[c]["file"].write_text(
        f'id: "{c}"\nname: "{chars[c]["name"]}"\nkind: "{chars[c]["kind"]}"\ndescription: "{best}"\n',
        encoding="utf-8")

# rewrite story references + dedup the characters list
def dedup_char_list(text):
    lines = text.split("\n")
    out, in_chars, seen = [], False, set()
    for ln in lines:
        if re.match(r'^characters:', ln):
            in_chars = True; seen = set(); out.append(ln); continue
        if in_chars:
            m = re.match(r'^  - "(.+)"$', ln)
            if m:
                if m.group(1) in seen:
                    continue  # drop duplicate
                seen.add(m.group(1)); out.append(ln); continue
            else:
                in_chars = False
        out.append(ln)
    return "\n".join(out)

changed = 0
for f, t in story_text.items():
    nt = t
    for a, c in alias.items():
        nt = nt.replace(f'"{a}"', f'"{c}"')
    nt = dedup_char_list(nt)
    if nt != t:
        f.write_text(nt, encoding="utf-8"); changed += 1

for a in alias:
    chars[a]["file"].unlink()

print(f"\nrewrote {changed} stories, deleted {len(alias)} duplicate character files")
print(f"characters now: {len(list(CH.glob('*.yaml')))}")
