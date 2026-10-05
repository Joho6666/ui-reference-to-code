#!/usr/bin/env node
// One entry point for every harness. It only dispatches to the real scripts, so behaviour lives in one place.
//
//   node scripts/replica.mjs init   --out ./site --template globe|hero --name Brand [--variant ...] [--run-url http://127.0.0.1:5173/]
//   node scripts/replica.mjs assets list|fetch --pack earth [--out dir] [--yes]
//   node scripts/replica.mjs shoot  --url http://127.0.0.1:5173/ --run <run-folder> --iteration N
//   node scripts/replica.mjs probe                      # prints JS to evaluate in ANY browser tool (ego-browser, browser pane, DevTools)
//   node scripts/replica.mjs checks --out dir --iteration N --desktop-probe d.json --mobile-probe m.json --desktop-png d.png --mobile-png m.png [--run R --url U]
//   node scripts/replica.mjs image  --prompt "..." --out public/hero.png --yes      # optional GPT image generation (costs money)
//   node scripts/replica.mjs gate   <capture-dir>/wow-review.md
//   node scripts/replica.mjs qa     <run-folder>/qa-N.json
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
const [cmd, ...rest] = process.argv.slice(2);

const table = {
  init: [python, join(here, 'replica_init.py')],
  assets: [python, join(here, 'fetch_assets.py')],
  shoot: [process.execPath, join(here, 'capture.mjs')],
  probe: [process.execPath, join(here, 'page_checks.mjs'), '--print-probe'],
  checks: [process.execPath, join(here, 'page_checks.mjs')],
  image: [python, join(here, 'gen_image.py')],
  gate: [python, join(here, 'wow_gate.py')],
  qa: [python, join(here, 'qa_gate.py')],
};

if (!table[cmd]) {
  console.error('usage: replica.mjs <init|assets|shoot|probe|checks|image|gate|qa> [args]  (see header of this file)');
  process.exit(3);
}
const [bin, ...pre] = table[cmd];
const done = spawnSync(bin, [...pre, ...rest], { stdio: 'inherit' });
process.exit(done.status ?? 3);
