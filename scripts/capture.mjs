#!/usr/bin/env node
// Capture desktop + mobile screenshots and capture receipts for the evidence contract.
// It never registers evidence: look at the PNGs first, then register with `evidence.py add --observer agent`.
//
//   node scripts/capture.mjs --url http://127.0.0.1:5173/ --run .ui-design/runs/<id> --iteration 1 [--out dir] [--settle 3500]
//
// Needs Playwright resolvable from the project (`npm i -D playwright`) or a global install.
import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const arg = (name, fallback) => {
  const i = process.argv.indexOf('--' + name);
  return i > -1 ? process.argv[i + 1] : fallback;
};
const url = arg('url');
const run = arg('run');
if (!url || !run) {
  console.error('usage: capture.mjs --url <url> --run <run-folder> [--iteration N] [--out dir] [--settle ms] [--theme dark|light]');
  process.exit(3);
}
const iteration = Number(arg('iteration', '1'));
const settle = Number(arg('settle', '3500')); // WebGL shader compile + transmission buffers need a moment
const theme = arg('theme', 'dark');
const out = resolve(arg('out', join(run, 'captures', `iter-${iteration}`)));
mkdirSync(out, { recursive: true });

const here = dirname(fileURLToPath(import.meta.url));
const evidence = join(here, 'evidence.py');
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');

const require = createRequire(join(process.cwd(), 'package.json'));
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  try {
    ({ chromium } = createRequire(import.meta.url)('playwright'));
  } catch {
    console.error('Playwright not found. Run `npm i -D playwright` (and `npx playwright install chromium`) in the project.');
    process.exit(3);
  }
}

// snapshot exits 2 when earlier evidence is stale (expected after every repair edit); the fingerprint is still valid
const snapshot = () => {
  const r = spawnSync(python, [evidence, 'snapshot', '--run', run], { encoding: 'utf8' });
  try {
    return JSON.parse(r.stdout);
  } catch {
    console.error('evidence.py snapshot failed:', (r.stdout + r.stderr).trim());
    process.exit(3);
  }
};
const runId = basename(resolve(run));
const before = snapshot().project_revision.fingerprint;

const devices = { desktop: { viewport: { width: 1440, height: 900 }, isMobile: false }, mobile: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } };
const browser = await chromium.launch({ args: ['--use-gl=angle', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const written = [];
const failures = [];
const warnings = [];
try {
  for (const [name, d] of Object.entries(devices)) {
    const context = await browser.newContext({ ...d, deviceScaleFactor: 1, colorScheme: theme });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForSelector('canvas[data-ready="true"]', { timeout: 15000 }).catch(() => {}); // no canvas = a 2D page, fine
    await page.waitForTimeout(settle);
    const regions = await page.evaluate(() => {
      const r = {};
      document.querySelectorAll('[data-region]').forEach((el) => {
        const b = el.getBoundingClientRect();
        const x = Math.max(0, Math.round(b.x)), y = Math.max(0, Math.round(b.y));
        const w = Math.round(Math.min(b.width, innerWidth - x)), h = Math.round(Math.min(b.height, innerHeight - y));
        if (w > 0 && h > 0) r[el.getAttribute('data-region')] = [x, y, w, h];
      });
      return r;
    });
    const probe = await page.evaluate(() => {
      const cta = document.querySelector('[data-cta]') || document.querySelector('.btn');
      const h1 = document.querySelector('h1');
      const lh = h1 ? parseFloat(getComputedStyle(h1).lineHeight) || parseFloat(getComputedStyle(h1).fontSize) * 1.1 : 0;
      const family = h1 ? getComputedStyle(h1).fontFamily : '';
      const first = family.split(',')[0].trim();
      return {
        overflowX: document.documentElement.scrollWidth - innerWidth,
        ctaBottom: cta ? Math.round(cta.getBoundingClientRect().bottom) : null,
        viewportH: innerHeight,
        h1Lines: h1 ? Math.round(h1.getBoundingClientRect().height / lh) : null,
        h1Font: first,
        h1FontLoaded: first ? document.fonts.check(`16px ${first}`) : true,
        sceneMounted: !!document.querySelector('.scene, [data-region="globe"]') ? !!document.querySelector('canvas') : null,
        canvasReady: document.querySelector('canvas') ? document.querySelector('canvas').dataset.ready === 'true' : null,
      };
    });
    const tag = (m) => `${name}: ${m}`;
    if (probe.overflowX > 1) failures.push(tag(`horizontal overflow of ${probe.overflowX}px`));
    if (probe.ctaBottom === null) warnings.push(tag('no [data-cta] or .btn found; fold check skipped'));
    else if (probe.ctaBottom > probe.viewportH) failures.push(tag(`primary CTA ends at ${probe.ctaBottom}px, below the ${probe.viewportH}px fold`));
    const maxLines = name === 'mobile' ? 4 : 3;
    if (probe.h1Lines && probe.h1Lines > maxLines) failures.push(tag(`h1 wraps to ${probe.h1Lines} lines (max ${maxLines})`));
    if (!probe.h1FontLoaded) failures.push(tag(`display font "${probe.h1Font}" not loaded (fallback font in use)`));
    if (probe.sceneMounted === false) failures.push(tag('3D scene wrapper present but no canvas mounted (CSS fallback is showing)'));
    if (probe.canvasReady === false) failures.push(tag('canvas never reported data-ready=true (textures/shaders did not finish)'));
    if (errors.some((e) => !/Failed to load resource/.test(e))) failures.push(tag(`page errors: ${errors.filter((e) => !/Failed to load resource/.test(e)).slice(0, 2).join(' | ')}`));
    if (errors.some((e) => /Failed to load resource/.test(e))) warnings.push(tag('some resources failed to load (check fonts/CDN)'));
    if (!Object.keys(regions).length) regions.page = [0, 0, d.viewport.width, d.viewport.height];
    const png = join(out, `${name}.png`);
    await page.screenshot({ path: png });
    const receipt = {
      run_id: runId, iteration, url, route: new URL(url).pathname || '/',
      viewport: [d.viewport.width, d.viewport.height], dpr: 1, theme, state: 'default', scroll: [0, 0],
      captured_at: new Date().toISOString(), source_revision: before, regions,
    };
    writeFileSync(join(out, `${name}.capture.json`), JSON.stringify(receipt, null, 2));
    written.push({ name, png, errors });
    await context.close();
  }
} finally {
  await browser.close();
}

writeFileSync(join(out, 'checks.json'), JSON.stringify({ iteration, failures, warnings }, null, 2));
const ITEMS = [
  ['subject', 'Can you name the main subject within 1 second?'],
  ['scale', 'Title or subject is dominant (title line >= 12% of viewport height, or subject >= 35% of width)'],
  ['material', 'Light, reflection and shadow agree; nothing black, plastic or pasted-on'],
  ['complete-fold', 'Title, sub-copy and CTA all visible in the first screen; subject not accidentally cropped'],
  ['color', '1 main + 1 accent + neutrals; accent used in 2-3 places'],
  ['typography', 'Display font has character and is actually loaded; contrast with body font'],
  ['negative-space', 'Breathing room between copy and subject; overlaps are deliberate and readable'],
  ['rhythm', 'The first transition changes the layout relationship'],
  ['mobile', 'Recomposed, not shrunk: subject still the focus, CTA reachable, title <= 4 lines'],
  ['motion', 'One primary motion; reduced-motion shows a static final state'],
];
const rel = (w) => w.png.replace(/.*captures/, 'captures');
const review = [
  `# Wow review — iteration ${iteration}`,
  '',
  '> Look at BOTH screenshots first. Score each item 0-2 and write what you actually saw (>= 12 chars).',
  '> Then run: python scripts/wow_gate.py <this file>',
  '',
  `viewed: desktop=${rel(written[0])} mobile=${rel(written[1])}`,
  '',
  `Automated checks: ${failures.length ? 'FAILED' : 'passed'}${failures.map((f) => '\n- ' + f).join('')}${warnings.map((f) => '\n- (warning) ' + f).join('')}`,
  '',
  '| # | item | score | what I saw |',
  '| --- | --- | --- | --- |',
  ...ITEMS.map(([k, q], i) => `| ${i + 1} | ${k} | | |`),
  '',
  'Questions:',
  ...ITEMS.map(([k, q], i) => `${i + 1}. ${k} — ${q}`),
  '',
].join('\n');
writeFileSync(join(out, 'wow-review.md'), review);

const after = snapshot().project_revision.fingerprint;
if (after !== before) console.error('WARNING: project files changed during capture; discard these captures and retake.');

for (const w of written) {
  console.log(`${w.name}: ${w.png}${w.errors.length ? `  (console errors: ${w.errors.length})` : ''}`);
  w.errors.slice(0, 3).forEach((e) => console.log('   ' + e));
}
console.log(failures.length ? `\nAUTOMATED CHECKS FAILED (${failures.length}):` : '\nautomated checks passed');
failures.forEach((f) => console.log('  x ' + f));
warnings.forEach((f) => console.log('  ! ' + f));
console.log(`\nNext: view both PNGs, fill ${join(out, 'wow-review.md')}, then run: python ${join(here, 'wow_gate.py')} <that file>`);
console.log('\nThen register what you actually looked at, e.g.:');
for (const w of written) {
  console.log(`  python ${join(here, 'evidence.py')} add --run ${run} --path ${w.png} --id impl-${w.name}-${iteration} --type screenshot --role implementation --capture ${w.png.replace(/\.png$/, '.capture.json')} --observer agent --iteration ${iteration}`);
}
