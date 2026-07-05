import { getCollection, type CollectionEntry } from 'astro:content';

export type Story = CollectionEntry<'stories'>;
export type Volume = CollectionEntry<'volumes'>;

const byOrder = (a: Story, b: Story) =>
  (a.data.order ?? 0) - (b.data.order ?? 0) || a.data.title.localeCompare(b.data.title, 'hu');

/** All stories, ordered. */
export async function allStories(): Promise<Story[]> {
  return (await getCollection('stories')).sort(byOrder);
}

/** Stories that reference a given entity id in one of its list fields. */
export function storiesReferencing(
  stories: Story[],
  field: 'characters' | 'locations' | 'objects' | 'themes' | 'seasons' | 'holidays',
  id: string,
): Story[] {
  return stories.filter((s) => s.data[field].some((r) => r.id === id));
}

/** Build a name/label lookup for a collection (id → display string). */
export async function labelMap(
  collection: 'characters' | 'locations' | 'objects' | 'volumes' | 'themes' | 'seasons' | 'holidays',
): Promise<Map<string, string>> {
  const entries = await getCollection(collection);
  const m = new Map<string, string>();
  for (const e of entries) {
    const d = e.data as Record<string, unknown>;
    m.set(e.id, (d.name as string) ?? (d.title as string) ?? (d.label as string) ?? e.id);
  }
  return m;
}

/** Count how many stories reference each id of a collection. */
export function usageCounts(
  stories: Story[],
  field: 'characters' | 'locations' | 'objects' | 'themes' | 'seasons' | 'holidays',
): Map<string, number> {
  const counts = new Map<string, number>();
  for (const s of stories) {
    for (const r of s.data[field]) counts.set(r.id, (counts.get(r.id) ?? 0) + 1);
  }
  return counts;
}
