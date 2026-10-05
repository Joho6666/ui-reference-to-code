#!/usr/bin/env node
// The single implementation of the automated page checks, shared by every browser route:
//   - capture.mjs (Playwright) imports it
//   - any other browser tool (ego-browser, Claude's browser pane, chatcut-web-browser, a human DevTools console)
//     evaluates PROBE_SOURCE in the page, saves the returned JSON, and runs this file as a CLI.
//
// CLI (external browser route):
//   1. In the page at desktop width (>= 1280) and again at mobile width (~390), evaluate the output of
//        node scripts/page_checks.mjs --print-probe
//      and save each returned object as JSON (add an "errors": ["..."] array if you saw page errors).
//   2. node scripts/page_checks.mjs --out <dir> --iteration N \
//        --desktop-probe d.json --mobile-probe m.json --desktop-png d.png --mobile-png m.png \
//        [--run <run-folder> --url <preview-url>]
//      -> <dir>/checks.json, <dir>/wow-review.md and, with --run, desktop/mobile .capture.json receipts.
import { spawnSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const PROBE_SOURCE = `(() => {
  const cta = document.querySelector('[data-cta]') || document.querySelector('.btn');
  const h1 = document.querySelector('h1');
  const lh = h1 ? parseFloat(getComputedStyle(h1).lineHeight) || parseFloat(getComputedStyle(h1).fontSize) * 1.1 : 0;
  const first = h1 ? getComputedStyle(h1).fontFamily.split(',')[0].trim() : '';
  const regions = {};
  document.querySelectorAll('[data-region]').forEach((el) => {
    const b = el.getBoundingClientRect();
    const x = Math.max(0, Math.round(b.x)), y = Math.max(0, Math.round(b.y));
    const w = Math.round(Math.min(b.width, innerWidth - x)), h = Math.round(Math.min(b.height, innerHeight - y));
    if (w > 0 && h > 0) regions[el.getAttribute('data-region')] = [x, y, w, h];
  });
  const canvas = document.querySelector('canvas');
  return {
    viewport: [innerWidth, innerHeight], dpr: devicePixelRatio, scroll: [Math.round(scrollX), Math.round(scrollY)], regions,
    overflowX: document.documentElement.scrollWidth - innerWidth,
    ctaBottom: cta ? Math.round(cta.getBoundingClientRect().bottom) : null,
    viewportH: innerHeight,
    h1Lines: h1 ? Math.round(h1.getBoundingClientRect().height / lh) : null,
    h1Font: first,
    h1FontLoaded: first ? document.fonts.check('16px ' + first) : true,
    sceneMounted: document.querySelector('.scene, [data-region="globe"]') ? !!canvas : null,
    canvasReady: canvas ? canvas.dataset.ready === 'true' : null,
  };
})()`;

/** @returns {{failures: string[], warnings: string[]}} */
export function evaluateProbe(name, probe, errors = []) {
  const failures = [], warnings = [];
  const tag = (m) => `${name}: ${m}`;
  if (probe.overflowX > 1) failures.push(tag(`horizontal overflow of ${probe.overflowX}px`));
  if (probe.ctaBottom === null) warnings.push(tag('no [data-cta] or .btn found; fold check skipped'));
  else if (probe.ctaBottom > probe.viewportH) failures.push(tag(`primary CTA ends at ${probe.ctaBottom}px, below the ${probe.viewportH}px fold`));
  const maxLines = name === 'mobile' ? 4 : 3;
  if (probe.h1Lines && probe.h1Lines > maxLines) failures.push(tag(`h1 wraps to ${probe.h1Lines} lines (max ${maxLines})`));
  if (!probe.h1FontLoaded) failures.push(tag(`display font "${probe.h1Font}" not loaded (fallback font in use)`));
  if (probe.sceneMounted === false) failures.push(tag('3D scene wrapper present but no canvas mounted (CSS fallback is showing)'));
  if (probe.canvasReady === false) failures.push(tag('canvas never reported data-ready=true (textures/shaders did not finish)'));
  const hard = errors.filter((e) => !/Failed to load resource/.test(e));
  if (hard.length) failures.push(tag(`page errors: ${hard.slice(0, 2).join(' | ')}`));
  if (errors.some((e) => /Failed to load resource/.test(e))) warnings.push(tag('some resources failed to load (check fonts/CDN)'));
  return { failures, warnings };
}

export const ITEMS = [
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

export function reviewMarkdown({ iteration, desktopPng, mobilePng, failures, warnings }) {
  return [
    `# Wow review — iteration ${iteration}`,
    '',
    '> Look at BOTH screenshots first. Score each item 0-2 and write what you actually saw (>= 12 chars).',
    '> Then run: node scripts/replica.mjs gate <this file>',
    '',
    `viewed: desktop=${desktopPng} mobile=${mobilePng}`,
    '',
    `Automated checks: ${failures.length ? 'FAILED' : 'passed'}${failures.map((f) => '\n- ' + f).join('')}${warnings.map((f) => '\n- (warning) ' + f).join('')}`,
    '',
    '| # | item | score | what I saw |',
    '| --- | --- | --- | --- |',
    ...ITEMS.map(([k], i) => `| ${i + 1} | ${k} | | |`),
    '',
    'Questions:',
    ...ITEMS.map(([k, q], i) => `${i + 1}. ${k} — ${q}`),
    '',
  ].join('\n');
}

export function receiptFor({ runId, iteration, url, probe, theme, fingerprint }) {
  const regions = Object.keys(probe.regions || {}).length ? probe.regions : { page: [0, 0, probe.viewport[0], probe.viewport[1]] };
  return {
    run_id: runId, iteration, url, route: new URL(url).pathname || '/',
    viewport: probe.viewport, dpr: probe.dpr, theme, state: 'default', scroll: probe.scroll,
    captured_at: new Date().toISOString(), source_revision: fingerprint, regions,
  };
}

// ---- CLI -------------------------------------------------------------------------------------------------------
const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const arg = (n, d) => { const i = process.argv.indexOf('--' + n); return i > -1 ? process.argv[i + 1] : d; };
  if (process.argv.includes('--print-probe')) {
    console.log(PROBE_SOURCE);
    process.exit(0);
  }
  const need = ['out', 'desktop-probe', 'mobile-probe', 'desktop-png', 'mobile-png'].filter((k) => !arg(k));
  if (need.length) {
    console.error('missing: ' + need.map((k) => '--' + k).join(' ') + '\nsee the header of scripts/page_checks.mjs');
    process.exit(3);
  }
  const out = resolve(arg('out'));
  const iteration = Number(arg('iteration', '1'));
  mkdirSync(out, { recursive: true });
  const load = (p) => JSON.parse(readFileSync(p, 'utf8'));
  const probes = { desktop: load(arg('desktop-probe')), mobile: load(arg('mobile-probe')) };
  const failures = [], warnings = [];
  for (const [name, probe] of Object.entries(probes)) {
    const r = evaluateProbe(name, probe, probe.errors || []);
    failures.push(...r.failures); warnings.push(...r.warnings);
  }
  writeFileSync(join(out, 'checks.json'), JSON.stringify({ iteration, failures, warnings }, null, 2));
  writeFileSync(join(out, 'wow-review.md'), reviewMarkdown({ iteration, desktopPng: resolve(arg('desktop-png')), mobilePng: resolve(arg('mobile-png')), failures, warnings }));
  const run = arg('run'), url = arg('url');
  if (run && url) {
    const here = dirname(fileURLToPath(import.meta.url));
    const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
    const snap = spawnSync(python, [join(here, 'evidence.py'), 'snapshot', '--run', run], { encoding: 'utf8' });
    const fingerprint = JSON.parse(snap.stdout).project_revision.fingerprint;
    for (const [name, probe] of Object.entries(probes)) {
      writeFileSync(join(out, `${name}.capture.json`), JSON.stringify(receiptFor({ runId: basename(resolve(run)), iteration, url, probe, theme: arg('theme', 'dark'), fingerprint }), null, 2));
    }
  }
  console.log(failures.length ? `AUTOMATED CHECKS FAILED (${failures.length}):` : 'automated checks passed');
  failures.forEach((f) => console.log('  x ' + f));
  warnings.forEach((f) => console.log('  ! ' + f));
  console.log(`\nNext: view both PNGs, fill ${join(out, 'wow-review.md')}, then: node scripts/replica.mjs gate <that file>`);
  process.exit(failures.length ? 1 : 0);
}
