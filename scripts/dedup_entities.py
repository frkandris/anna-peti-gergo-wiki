#!/usr/bin/env python3
"""Generic same-name dedup for locations & objects (characters handled separately)."""
import pathlib, re, collections, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "site/src/content"
ST = CONTENT / "stories"
story_text = {f: f.read_text(encoding="utf-8") for f in ST.glob("*.yaml")}

def field(text, key):
    m = re.search(rf'{key}:\s*"(.*)"', text)
    return m.group(1) if m else ""
def refcount(cid):
    return sum(1 for t in story_text.values() if f'"{cid}"' in t)

def dedup_list(text, listkey):
    lines, out, inl, seen = text.split("\n"), [], False, set()
    for ln in lines:
        if re.match(rf'^{listkey}:', ln):
            inl, seen = True, set(); out.append(ln); continue
        if inl:
            m = re.match(r'^  - "(.+)"$', ln)
            if m:
                if m.group(1) in seen: continue
                seen.add(m.group(1)); out.append(ln); continue
            inl = False
        out.append(ln)
    return "\n".join(out)

def run(coll, listkey):
    d = CONTENT / coll
    ents = {}
    for f in d.glob("*.yaml"):
        t = f.read_text(encoding="utf-8")
        ents[f.stem] = {"name": field(t, "name"), "text": t, "file": f}
    groups = collections.defaultdict(list)
    for cid, e in ents.items():
        groups[e["name"]].append(cid)
    alias = {}
    for name, ids in groups.items():
        if len(ids) <= 1: continue
        canon = max(ids, key=lambda i: (refcount(i), len(i)))
        for i in ids:
            if i != canon: alias[i] = canon
    if not alias:
        print(f"{coll}: no duplicates"); return
    print(f"{coll} MERGE PLAN:")
    for a, c in sorted(alias.items()): print(f"  {a!r} ({ents[a]['name']}) -> {c!r}")
    # keep fullest text (longest description) on canonical
    canon_groups = collections.defaultdict(list)
    for a, c in alias.items(): canon_groups[c].append(a)
    for c, al in canon_groups.items():
        grp = [c] + al
        best = max((ents[i]["text"] for i in grp), key=len)
        # rewrite id in the chosen text to the canonical id
        best = re.sub(r'^id:\s*".*"', f'id: "{c}"', best, count=1, flags=re.M)
        ents[c]["file"].write_text(best, encoding="utf-8")
    changed = 0
    for f, t in list(story_text.items()):
        nt = t
        for a, c in alias.items(): nt = nt.replace(f'"{a}"', f'"{c}"')
        nt = dedup_list(nt, listkey)
        if nt != t:
            f.write_text(nt, encoding="utf-8"); story_text[f] = nt; changed += 1
    for a in alias: ents[a]["file"].unlink()
    print(f"  -> rewrote {changed} stories, removed {len(alias)} files, {coll} now: {len(list(d.glob('*.yaml')))}")

run("locations", "locations")
run("objects", "objects")
