import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from support import ROOT

GOOD = {'viewport': [1440, 900], 'dpr': 1, 'scroll': [0, 0], 'regions': {'hero': [0, 0, 1440, 900]}, 'overflowX': 0, 'ctaBottom': 500,
        'viewportH': 900, 'h1Lines': 1, 'h1Font': 'Cormorant Garamond', 'h1FontLoaded': True, 'sceneMounted': True, 'canvasReady': True}


def run_checks(desktop, mobile):
    node = shutil.which('node')
    with tempfile.TemporaryDirectory() as folder:
        f = Path(folder)
        (f / 'd.json').write_text(json.dumps(desktop)); (f / 'm.json').write_text(json.dumps(mobile))
        done = subprocess.run([node, str(ROOT / 'scripts' / 'page_checks.mjs'), '--out', str(f / 'out'), '--iteration', '1',
                               '--desktop-probe', str(f / 'd.json'), '--mobile-probe', str(f / 'm.json'),
                               '--desktop-png', 'd.png', '--mobile-png', 'm.png'], capture_output=True, text=True)
        checks = json.loads((f / 'out' / 'checks.json').read_text(encoding='utf-8'))
        review = (f / 'out' / 'wow-review.md').read_text(encoding='utf-8')
        return done.returncode, checks, review


@unittest.skipUnless(shutil.which('node'), 'node not installed')
class PageChecksTests(unittest.TestCase):
    def test_healthy_page_passes_and_writes_review(self):
        code, checks, review = run_checks(GOOD, {**GOOD, 'viewport': [390, 844], 'viewportH': 844, 'ctaBottom': 600})
        self.assertEqual((code, checks['failures']), (0, []))
        self.assertIn('| 10 | motion |', review)

    def test_cta_below_fold_and_font_fallback_fail(self):
        bad = {**GOOD, 'ctaBottom': 992, 'h1FontLoaded': False}
        code, checks, _ = run_checks(bad, {**GOOD, 'viewportH': 844, 'ctaBottom': 600})
        self.assertEqual(code, 1)
        self.assertTrue(any('below the 900px fold' in f for f in checks['failures']))
        self.assertTrue(any('not loaded' in f for f in checks['failures']))

    def test_unmounted_scene_and_wrapping_title_fail(self):
        bad = {**GOOD, 'sceneMounted': False, 'h1Lines': 5}
        _, checks, _ = run_checks(bad, {**GOOD, 'viewportH': 844, 'ctaBottom': 600})
        self.assertTrue(any('no canvas mounted' in f for f in checks['failures']))
        self.assertTrue(any('wraps to 5 lines' in f for f in checks['failures']))


class GenImageTests(unittest.TestCase):
    def cli(self, *args, env=None):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / 'gen_image.py'), *args], capture_output=True, text=True)

    def test_without_yes_nothing_is_sent(self):
        with tempfile.TemporaryDirectory() as folder:
            done = self.cli('--prompt', 'dark navy backdrop, no text', '--out', str(Path(folder) / 'a.png'))
            self.assertEqual(done.returncode, 2)
            self.assertIn('NOT sent', done.stdout)

    def test_logo_prompt_refused(self):
        self.assertEqual(self.cli('--prompt', 'a brand logo for Acme', '--out', 'x.png', '--yes').returncode, 3)

    def test_record_only_writes_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / '.ui-design').mkdir()
            image = Path(folder) / 'hero.png'; image.write_bytes(b'png')
            done = self.cli('--prompt', 'calm studio backdrop', '--out', str(image), '--record-only')
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            entries = json.loads((Path(folder) / '.ui-design' / 'generated-assets.json').read_text(encoding='utf-8'))
            self.assertEqual(entries[0]['source'], 'built-in image tool')
            self.assertEqual(len(entries[0]['sha256']), 64)


if __name__ == '__main__': unittest.main()
