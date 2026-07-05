---
type: "Reference"
title: "Adatmodell és kontrollált szótár"
description: "Entitások, mezők, slug/címke konvenció, kontrollált szótár."
tags: ["schema", "szotar", "slug"]
timestamp: "2026-07-05"
---

# Adatmodell és kontrollált szótár

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
