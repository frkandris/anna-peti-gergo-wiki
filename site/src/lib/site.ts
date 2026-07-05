// Base-path aware URL helper. BASE_URL is "/anna-peti-gergo-wiki/".
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Build an internal href that respects the GitHub Pages base path. */
export function href(path = '/'): string {
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${BASE}${p}` || '/';
}

export const SITE = {
  title: 'Anna, Peti, Gergő Wiki',
  tagline: 'Melyik mese melyik kötetben? — kereshető katalógus szülőknek',
  author: 'Bartos Erika',
  publisher: 'Alexandra Kiadó',
};

// URL segments (Hungarian) for each entity type
export const SEG = {
  volume: 'kotet',
  story: 'mese',
  character: 'szereplo',
  location: 'helyszin',
  object: 'targy',
  theme: 'tema',
  season: 'evszak',
  holiday: 'unnep',
} as const;

// Human labels
export const LABEL = {
  volume: 'Kötet',
  volumes: 'Kötetek',
  story: 'Mese',
  stories: 'Mesék',
  character: 'Szereplő',
  characters: 'Szereplők',
  location: 'Helyszín',
  locations: 'Helyszínek',
  object: 'Tárgy',
  objects: 'Tárgyak',
  vehicle: 'Jármű',
  vehicles: 'Járművek',
  theme: 'Téma',
  themes: 'Témák',
  season: 'Évszak',
  seasons: 'Évszakok',
  holiday: 'Ünnep',
  holidays: 'Ünnepek',
} as const;

/** Strip Hungarian accents → ascii slug (mirror of the extraction rule). */
export function slugify(s: string): string {
  const map: Record<string, string> = {
    á: 'a', é: 'e', í: 'i', ó: 'o', ö: 'o', ő: 'o', ú: 'u', ü: 'u', ű: 'u',
  };
  return s
    .toLowerCase()
    .replace(/[áéíóöőúüű]/g, (c) => map[c] ?? c)
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
