---
type: "Overview"
title: "Anna, Peti, Gergő wiki — áttekintés"
description: "Statikus, kereshető katalógus Bartos Erika Anna, Peti, Gergő meséiről."
tags: ["projekt", "cel", "jog"]
timestamp: "2026-07-05"
---

# Anna, Peti, Gergő wiki — áttekintés

Statikus, kereshető **rajongói referencia-katalógus** Bartos Erika *Anna, Peti, Gergő*
könyveiről. Fő cél: a szülők gyorsan megtalálják, **melyik mese melyik kötetben**
van, és böngészhessenek szereplő, helyszín, tárgy, téma, évszak és ünnep szerint.

Jelenlegi méret: **9 kötet · 138 mese · 77
szereplő · 96 helyszín · 325 tárgy · 71 téma**.

## Alapelvek
- **Csak metaadat + saját szavas összefoglaló.** Bartos Erika a szerző és a
  jogtulajdonos; a mesék szövege és képei **nem** kerülnek a repóba vagy a
  weboldalra. A forrás-PDF-ek gitignore-oltak. Lásd [conventions](conventions.md).
- **Statikus.** Nincs backend, nincs adatbázis — Astro build → GitHub Pages.
- **Adathalmaz, nem dokumentumok.** A forrás-igazság strukturált YAML; minden
  oldal generált. Lásd [architecture](architecture.md).

Élő oldal: https://frkandris.github.io/anna-peti-gergo-wiki/
