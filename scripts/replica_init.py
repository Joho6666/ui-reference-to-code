#!/usr/bin/env python3
"""One-command Replica bootstrap: copy the R3F hero template, seed .ui-design/, optionally create an evidence run.

    python scripts/replica_init.py --out ./my-site --name "Atelier" [--variant glass-knot|liquid-blob|orbit-cards] [--run-url http://127.0.0.1:5173/]

It writes files only. It never installs packages, starts servers or spends money.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / 'templates' / 'r3f-hero'
VARIANTS = ('glass-knot', 'liquid-blob', 'orbit-cards')
IGNORE = shutil.ignore_patterns('node_modules', 'dist', '.vite')

CARD = """# Replica Card — fill from OBSERVED evidence only (mark measured / estimated / unknown)

```yaml
template_name: ""
primary_url: ""
primary_role: "hero composition / editorial rhythm / product presentation"
page_type: ""
observed_viewport: "measured / estimated / unknown"
hero_silhouette: ""        # -> src/theme.ts hero.subjectSide / subjectWidth
grid: ""
type_hierarchy: ""         # -> src/theme.ts fonts + styles.css h1
image_crop: ""
color_roles: ""            # -> src/theme.ts colors
motion: "observed / inferred / unknown"
mobile_transformation: ""
unknowns: []
adaptation_boundary: ""
```

## Rules (>= 5, each tied to a screenshot region and an implementation)
1. silhouette:
2. type:
3. image / 3D subject:
4. rhythm (first transition):
5. mobile:

## Scene contract
```yaml
scene_goal: ""
subject: ""
camera: "static / orbit / scroll-controlled"
materials: ""
interaction: "one bounded pointer, touch or scroll response"
performance_budget: ""
mobile_fallback: "CSS silhouette (built in)"
reduced_motion: "final state, no continuous motion (built in)"
asset_license: "procedural geometry, no external assets"
```
"""


def scaffold(out, name, variant):
    if out.exists() and any(out.iterdir()):
        raise SystemExit('refusing to write into non-empty folder: %s' % out)
    shutil.copytree(TEMPLATE, out, ignore=IGNORE, dirs_exist_ok=True)
    theme = out / 'src' / 'theme.ts'
    text = theme.read_text(encoding='utf-8')
    text = re.sub(r"variant: '[a-z-]+' as SceneVariant", "variant: '%s' as SceneVariant" % variant, text)
    if name:
        text = re.sub(r"brand: '[^']*'", "brand: %s" % json.dumps(name, ensure_ascii=False).replace('"', "'"), text, count=1)
    theme.write_text(text, encoding='utf-8')
    design = out / '.ui-design'
    design.mkdir(exist_ok=True)
    (design / 'replica-card.md').write_text(CARD, encoding='utf-8')
    (design / 'pattern-library.md').write_text('# Pattern library\n\nEntries are added after an accepted replica (see references/template-replica-playbook.md).\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--name', default='')
    p.add_argument('--variant', default='glass-knot', choices=VARIANTS)
    p.add_argument('--run-url', help='also create an evidence run for this preview URL (needs git or selected files)')
    a = p.parse_args()
    if not TEMPLATE.is_dir():
        raise SystemExit('template missing: %s' % TEMPLATE)
    scaffold(a.out, a.name, a.variant)
    result = {'project': str(a.out), 'variant': a.variant, 'next': ['cd %s' % a.out, 'npm install', 'npm run dev']}
    if a.run_url:
        # evidence fingerprints tracked + non-ignored files; a repo keeps node_modules/dist out of that set
        if shutil.which('git') and not (a.out / '.git').exists():
            subprocess.run(['git', 'init', '-q'], cwd=str(a.out), check=False)
        done = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'evidence.py'), 'create-run', '--project', str(a.out), '--url', a.run_url],
                              capture_output=True, text=True)
        result['run'] = json.loads(done.stdout) if done.returncode == 0 and done.stdout.strip() else {'error': (done.stdout + done.stderr).strip()}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
