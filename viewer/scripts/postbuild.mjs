import { readFile, writeFile } from 'node:fs/promises';
const html = await readFile('dist/index.html', 'utf8');
if (!html.includes('name="robots" content="noindex, nofollow, noimageindex"')) {
  throw new Error('Production HTML must prohibit indexing');
}
await writeFile('dist/404.html', '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noimageindex"><title>Page not found</title></head><body><h1>Page not found</h1><p>Open the original house-study link to return to the viewer.</p></body></html>');
await writeFile('dist/.nojekyll', '');
