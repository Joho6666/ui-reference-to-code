#!/usr/bin/env python3
"""Download a pinned asset pack, but only after the user has approved the listed files.

    python scripts/fetch_assets.py list  --pack earth
    python scripts/fetch_assets.py fetch --pack earth --out ./site/public/textures --yes

`fetch` without --yes prints exactly what would be downloaded (file, size, source) and exits 2, so an agent
cannot download silently: show the listing to the user, get a clear yes in chat, then re-run with --yes.
Every file is verified against the sha256 pinned in assets/manifest.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

MANIFEST = Path(__file__).resolve().parent.parent / 'assets' / 'manifest.json'


def load_pack(name):
    packs = json.loads(MANIFEST.read_text(encoding='utf-8'))['packs']
    if name not in packs:
        raise SystemExit('unknown pack %r; available: %s' % (name, ', '.join(sorted(packs))))
    return packs[name]


def describe(pack):
    total = sum(f['bytes'] for f in pack['files'])
    lines = ['source:  %s' % pack['source'], 'license: %s' % pack['license'], 'files:']
    lines += ['  - %-28s %8.0f KB' % (f['name'], f['bytes'] / 1024) for f in pack['files']]
    lines.append('total:   %.2f MB' % (total / 1048576))
    return '\n'.join(lines)


def fetch(pack, out):
    out.mkdir(parents=True, exist_ok=True)
    for f in pack['files']:
        target = out / f['name']
        data = urllib.request.urlopen(pack['base_url'] + f['name'], timeout=60).read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != f['sha256']:
            raise SystemExit('checksum mismatch for %s (got %s); refusing to keep it' % (f['name'], digest))
        target.write_bytes(data)
        print('ok  %s' % target)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    ls = sub.add_parser('list'); ls.add_argument('--pack', required=True)
    fe = sub.add_parser('fetch'); fe.add_argument('--pack', required=True); fe.add_argument('--out', required=True, type=Path)
    fe.add_argument('--yes', action='store_true', help='the user approved the listed download')
    a = p.parse_args()
    pack = load_pack(a.pack)
    if a.command == 'list':
        print(describe(pack)); return 0
    if not a.yes:
        print('NOT downloaded. Ask the user to approve this download, then re-run with --yes:\n')
        print(describe(pack)); return 2
    fetch(pack, a.out); return 0


if __name__ == '__main__':
    sys.exit(main())
