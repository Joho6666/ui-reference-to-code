import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT

ITEMS = ['subject', 'scale', 'material', 'complete-fold', 'color', 'typography', 'negative-space', 'rhythm', 'mobile', 'motion']


def review(scores, viewed='desktop=captures/iter-1/desktop.png mobile=captures/iter-1/mobile.png', note='saw it clearly in the shot'):
    rows = ['| %d | %s | %s | %s |' % (i + 1, k, scores.get(k, ''), note if scores.get(k, '') != '' else '') for i, k in enumerate(ITEMS)]
    return '# review\n\nviewed: %s\n\n| # | item | score | what I saw |\n| --- | --- | --- | --- |\n%s\n' % (viewed, '\n'.join(rows))


def gate(text, failures=()):
    with tempfile.TemporaryDirectory() as folder:
        (Path(folder) / 'wow-review.md').write_text(text, encoding='utf-8')
        (Path(folder) / 'checks.json').write_text(json.dumps({'failures': list(failures), 'warnings': []}), encoding='utf-8')
        done = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'wow_gate.py'), str(Path(folder) / 'wow-review.md')], capture_output=True, text=True)
        return done.returncode, json.loads(done.stdout)


class WowGateTests(unittest.TestCase):
    def test_all_twos_accepted(self):
        code, out = gate(review({k: 2 for k in ITEMS}))
        self.assertEqual((code, out['verdict'], out['total']), (0, 'accepted', 20))

    def test_blank_review_is_incomplete(self):
        code, out = gate(review({}))
        self.assertEqual((code, out['verdict']), (2, 'incomplete'))

    def test_missing_mobile_screenshot_is_incomplete(self):
        code, out = gate(review({k: 2 for k in ITEMS}, viewed='desktop=a.png'))
        self.assertEqual(code, 2)

    def test_throwaway_note_rejected(self):
        code, _ = gate(review({k: 2 for k in ITEMS}, note='ok'))
        self.assertEqual(code, 2)

    def test_zero_item_blocks_acceptance(self):
        scores = {k: 2 for k in ITEMS}; scores['material'] = 0
        code, out = gate(review(scores))
        self.assertEqual((code, out['verdict']), (1, 'needs-polish'))
        self.assertEqual(out['repair_next'][0], 'material')

    def test_automated_failure_caps_verdict(self):
        code, out = gate(review({k: 2 for k in ITEMS}), failures=['desktop: primary CTA ends at 950px, below the 900px fold'])
        self.assertEqual((code, out['verdict']), (1, 'needs-polish'))


class FetchAssetsTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / 'fetch_assets.py'), *args], capture_output=True, text=True)

    def test_list_shows_files_and_license(self):
        done = self.run_cli('list', '--pack', 'earth')
        self.assertEqual(done.returncode, 0)
        self.assertIn('earth_night_4096.jpg', done.stdout)
        self.assertIn('license', done.stdout)

    def test_fetch_without_yes_downloads_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            done = self.run_cli('fetch', '--pack', 'earth', '--out', folder)
            self.assertEqual(done.returncode, 2)
            self.assertEqual(list(Path(folder).iterdir()), [])


if __name__ == '__main__': unittest.main()
