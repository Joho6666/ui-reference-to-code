#!/usr/bin/env python3
"""Deterministic Wow Gate: turns a filled-in wow-review.md plus checks.json into a verdict.

    python scripts/wow_gate.py <capture-dir>/wow-review.md

Exit codes: 0 accepted, 1 needs-polish, 2 incomplete (blank / unseen / unjustified), 3 invalid input.
The gate cannot see the pixels; it forces the reviewer to look (named screenshots, a note per item) and
caps the verdict with the automated page checks that capture.mjs wrote next to the review.
"""
import json
from pathlib import Path
import re
import sys

ITEMS = ['subject', 'scale', 'material', 'complete-fold', 'color', 'typography', 'negative-space', 'rhythm', 'mobile', 'motion']
PASS_TOTAL = 14
MIN_NOTE = 12


def parse(text):
    viewed = re.search(r'^viewed:\s*(.+)$', text, re.M)
    rows = {}
    for m in re.finditer(r'^\|\s*(\d+)\s*\|\s*([a-z-]+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$', text, re.M):
        rows[m.group(2)] = (m.group(3).strip(), m.group(4).strip())
    return (viewed.group(1).strip() if viewed else ''), rows


def evaluate(review_path):
    path = Path(review_path)
    text = path.read_text(encoding='utf-8')
    viewed, rows = parse(text)
    problems, scores = [], {}
    if not re.search(r'desktop', viewed, re.I) or not re.search(r'mobile', viewed, re.I):
        problems.append('viewed: must name both the desktop and the mobile screenshot you looked at')
    for item in ITEMS:
        score, note = rows.get(item, ('', ''))
        if score not in ('0', '1', '2'):
            problems.append('%s: score must be 0, 1 or 2 (got %r)' % (item, score)); continue
        if len(note) < MIN_NOTE or note.lower() in ('ok', 'good', 'fine', 'n/a'):
            problems.append('%s: write what you saw in the screenshot (>= %d chars)' % (item, MIN_NOTE)); continue
        scores[item] = int(score)
    checks_file = path.parent / 'checks.json'
    checks = json.loads(checks_file.read_text(encoding='utf-8')) if checks_file.is_file() else {'failures': ['checks.json missing: rerun capture.mjs']}
    if problems:
        return {'verdict': 'incomplete', 'problems': problems, 'auto_failures': checks['failures']}, 2
    total = sum(scores.values())
    zeros = [k for k, v in scores.items() if v == 0]
    reasons = []
    if total < PASS_TOTAL: reasons.append('total %d < %d' % (total, PASS_TOTAL))
    if zeros: reasons.append('zero-scored: ' + ', '.join(zeros))
    if checks['failures']: reasons.append('automated checks failed: ' + '; '.join(checks['failures']))
    verdict = 'needs-polish' if reasons else 'accepted'
    weakest = sorted(scores, key=lambda k: scores[k])[:2]
    return {'verdict': verdict, 'total': total, 'max': 2 * len(ITEMS), 'reasons': reasons, 'repair_next': weakest, 'auto_failures': checks['failures']}, (1 if reasons else 0)


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        print(__doc__); return 0
    if len(sys.argv) != 2:
        print(__doc__); return 3
    try:
        result, code = evaluate(sys.argv[1])
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({'error': str(error)})); return 3
    print(json.dumps(result, ensure_ascii=False, indent=2)); return code


if __name__ == '__main__':
    sys.exit(main())
