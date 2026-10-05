#!/usr/bin/env python3
"""Optional GPT image generation for hero imagery, backgrounds and textures. Costs real money.

    python scripts/gen_image.py --prompt "..." --out public/hero.png [--size 1536x1024] [--quality medium] [--n 1] --yes
    python scripts/gen_image.py --prompt "..." --out public/hero.png --dry-run     # prints the request, spends nothing

Use this only when the harness has NO built-in image tool. Codex has a built-in `image_gen` tool: prefer it,
then run `--record-only --out <file> --prompt "..."` so the file still gets a provenance entry.

Safety rules baked in:
  * without --yes (or --dry-run) nothing is sent; the request is shown and the script exits 2, so the user can approve the cost
  * the API key is read from OPENAI_API_KEY and is never printed or written
  * every generated file is appended to .ui-design/generated-assets.json (model, prompt, size, date, sha256, license note)
  * the prompt is refused if it names a real person, a logo/brand mark or asks to copy a reference image
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

ENDPOINT = 'https://api.openai.com/v1/images/generations'
DEFAULT_MODEL = os.environ.get('IMAGE_MODEL', 'gpt-image-1')
REFUSE = re.compile(r'\b(logo|trademark|watermark|in the style of [A-Z][a-z]+ [A-Z][a-z]+|copy (this|the) (image|reference)|exact copy)\b', re.I)


def provenance_path(out):
    for parent in [out.parent, *out.parent.parents]:
        if (parent / '.ui-design').is_dir():
            return parent / '.ui-design' / 'generated-assets.json'
    return Path('.ui-design') / 'generated-assets.json'


def record(out, args, source):
    path = provenance_path(out.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else []
    entries.append({
        'file': str(out), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'source': source,
        'model': args.model, 'prompt': args.prompt, 'size': args.size,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'license': 'AI-generated for this project; no third-party reference image was copied',
    })
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prompt', required=True)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--size', default='1536x1024', help='1024x1024, 1536x1024 or 1024x1536')
    p.add_argument('--quality', default='medium', choices=['low', 'medium', 'high'])
    p.add_argument('--n', type=int, default=1)
    p.add_argument('--model', default=DEFAULT_MODEL)
    p.add_argument('--yes', action='store_true', help='the user approved this paid request')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--record-only', action='store_true', help='file already exists (made by a built-in tool); only write provenance')
    a = p.parse_args()

    if REFUSE.search(a.prompt):
        print('refused: the prompt asks for a logo / trademark / copied reference. Describe an original scene instead.')
        return 3
    body = {'model': a.model, 'prompt': a.prompt, 'size': a.size, 'quality': a.quality, 'n': a.n}
    if a.record_only:
        if not a.out.is_file():
            print('--record-only needs the file to exist: %s' % a.out); return 3
        print('recorded in %s' % record(a.out, a, 'built-in image tool')); return 0
    if a.dry_run or not a.yes:
        print(json.dumps({'would_post_to': ENDPOINT, 'body': body, 'output': str(a.out)}, ensure_ascii=False, indent=2))
        if not a.dry_run:
            print('\nNOT sent. Image generation is paid: show this to the user, get a clear yes, then re-run with --yes.')
            return 2
        return 0
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        print('OPENAI_API_KEY is not set; cannot generate. Use the harness built-in image tool or ask the user for a source image.')
        return 3
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        payload = json.loads(urllib.request.urlopen(request, timeout=300).read())
    except urllib.error.HTTPError as error:
        print('image API error %s: %s' % (error.code, error.read().decode('utf-8', 'replace')[:500])); return 3
    a.out.parent.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(payload['data']):
        target = a.out if len(payload['data']) == 1 else a.out.with_name('%s-%d%s' % (a.out.stem, index + 1, a.out.suffix))
        target.write_bytes(base64.b64decode(item['b64_json']))
        print('saved %s (provenance: %s)' % (target, record(target, a, 'OpenAI Images API')))
    print('Now LOOK at the image before using it: check light direction, palette, crop and stray text/artifacts.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
