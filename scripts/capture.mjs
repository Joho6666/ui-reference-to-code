#!/usr/bin/env node
// Playwright route: capture desktop + mobile screenshots, receipts, automated checks and a blank wow-review.
// It never registers evidence: look at the PNGs first, then register with `evidence.py add --observer agent`.
//
//   node scripts/capture.mjs --url http://127.0.0.1:5173/ --run .ui-design/runs/<id> --iteration 1 [--out dir] [--settle 3500]
//
// Needs Playwright resolvable from the project (`npm i -D playwright`) or a global install.
// No Playwright? Use your harness's browser tool (ego-browser, browser pane, ...) and scripts/page_checks.mjs instead.
import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PROBE_SOURCE, evaluateProbe, receiptFor, reviewMarkdown } from './page_checks.mjs';

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
    console.error('Playwright not found. Run `npm i -D playwright` and `npx playwright install chromium` in the project,\n'
      + 'or use your harness browser tool with scripts/page_checks.mjs (see docs/HARNESS_ADAPTERS.md).');
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
    const probe = await page.evaluate(PROBE_SOURCE);
    const r = evaluateProbe(name, probe, errors);
    failures.push(...r.failures); warnings.push(...r.warnings);
    const png = join(out, `${name}.png`);
    await page.screenshot({ path: png });
    writeFileSync(join(out, `${name}.capture.json`), JSON.stringify(receiptFor({ runId, iteration, url, probe, theme, fingerprint: before }), null, 2));
    written.push({ name, png, errors });
    await context.close();
  }
} finally {
  await browser.close();
}

writeFileSync(join(out, 'checks.json'), JSON.stringify({ iteration, failures, warnings }, null, 2));
writeFileSync(join(out, 'wow-review.md'), reviewMarkdown({ iteration, desktopPng: written[0].png, mobilePng: written[1].png, failures, warnings }));

const after = snapshot().project_revision.fingerprint;
if (after !== before) console.error('WARNING: project files changed during capture; discard these captures and retake.');

for (const w of written) {
  console.log(`${w.name}: ${w.png}${w.errors.length ? `  (console errors: ${w.errors.length})` : ''}`);
  w.errors.slice(0, 3).forEach((e) => console.log('   ' + e));
}
console.log(failures.length ? `\nAUTOMATED CHECKS FAILED (${failures.length}):` : '\nautomated checks passed');
failures.forEach((f) => console.log('  x ' + f));
warnings.forEach((f) => console.log('  ! ' + f));
console.log(`\nNext: view both PNGs, fill ${join(out, 'wow-review.md')}, then run: node ${join(here, 'replica.mjs')} gate <that file>`);
console.log('\nThen register what you actually looked at, e.g.:');
for (const w of written) {
  console.log(`  python ${evidence} add --run ${run} --path ${w.png} --id impl-${w.name}-${iteration} --type screenshot --role implementation --capture ${w.png.replace(/\.png$/, '.capture.json')} --observer agent --iteration ${iteration}`);
}
