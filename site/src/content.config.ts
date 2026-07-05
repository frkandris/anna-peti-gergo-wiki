import { defineCollection, reference, z } from 'astro:content';
import { glob } from 'astro/loaders';

const yaml = (dir: string) =>
  glob({ pattern: '**/*.{yaml,yml}', base: `./src/content/${dir}` });

// --- Controlled vocabularies (themes / seasons / holidays) ---
const vocab = defineCollection({
  loader: yaml('themes'),
  schema: z.object({
    id: z.string().optional(),
    label: z.string(),
    description: z.string().optional(),
  }),
});

const seasons = defineCollection({
  loader: yaml('seasons'),
  schema: z.object({ id: z.string().optional(), label: z.string() }),
});

const holidays = defineCollection({
  loader: yaml('holidays'),
  schema: z.object({ id: z.string().optional(), label: z.string() }),
});

// --- Entities ---
const characters = defineCollection({
  loader: yaml('characters'),
  schema: z.object({
    id: z.string().optional(),
    name: z.string(),
    kind: z.enum(['person', 'animal', 'toy', 'other']).default('person'),
    description: z.string().optional(),
  }),
});

const locations = defineCollection({
  loader: yaml('locations'),
  schema: z.object({
    id: z.string().optional(),
    name: z.string(),
    kind: z.enum(['real', 'fictional']).default('real'),
    description: z.string().optional(),
  }),
});

const objects = defineCollection({
  loader: yaml('objects'),
  schema: z.object({
    id: z.string().optional(),
    name: z.string(),
    category: z.enum(['object', 'vehicle']).default('object'),
    description: z.string().optional(),
  }),
});

// --- Volumes & stories ---
const volumes = defineCollection({
  loader: yaml('volumes'),
  schema: z.object({
    id: z.string().optional(),
    title: z.string(),
    series: z.string(),
    publisher: z.string().optional(),
    year: z.number().optional(),
    description: z.string().optional(),
    coverNote: z.string().optional(),
  }),
});

const stories = defineCollection({
  loader: yaml('stories'),
  schema: z.object({
    id: z.string().optional(),
    title: z.string(),
    volume: reference('volumes'),
    order: z.number().default(0),
    pageStart: z.number().optional(),
    pageEnd: z.number().optional(),
    summary: z.string(),
    characters: z.array(reference('characters')).default([]),
    locations: z.array(reference('locations')).default([]),
    objects: z.array(reference('objects')).default([]),
    themes: z.array(reference('themes')).default([]),
    seasons: z.array(reference('seasons')).default([]),
    holidays: z.array(reference('holidays')).default([]),
  }),
});

export const collections = {
  themes: vocab,
  seasons,
  holidays,
  characters,
  locations,
  objects,
  volumes,
  stories,
};
