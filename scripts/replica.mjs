#!/usr/bin/env node
// One entry point for every harness. It only dispatches to the real scripts, so behaviour lives in one place.
//
//   node scripts/replica.mjs init   --out ./site --template globe|hero --name Brand [--variant ...] [--run-url http://127.0.0.1:5173/]
//   node scripts/replica.mjs assets list|fetch --pack earth [--out dir] [--yes]
//   node scripts/replica.mjs shoot  --url http://127.0.0.1:5173/ --run <run-folder> --iteration N
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
  gate: [python, join(here, 'wow_gate.py')],
  qa: [python, join(here, 'qa_gate.py')],
};

if (!table[cmd]) {
  console.error('usage: replica.mjs <init|assets|shoot|gate|qa> [args]  (see header of this file)');
  process.exit(3);
}
const [bin, script] = table[cmd];
const done = spawnSync(bin, [script, ...rest], { stdio: 'inherit' });
process.exit(done.status ?? 3);
