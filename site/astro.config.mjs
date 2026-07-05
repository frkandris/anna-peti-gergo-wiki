// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Project pages: https://frkandris.github.io/anna-peti-gergo-wiki
export default defineConfig({
  site: 'https://frkandris.github.io',
  base: '/anna-peti-gergo-wiki',
  trailingSlash: 'ignore',
  integrations: [sitemap()],
});
