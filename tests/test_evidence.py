import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, evidence, fixture, png


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name); self.folder, self.report, self.shot = fixture(self.project)

    def test_validate_registered_artifacts(self):
        self.assertEqual(evidence.validate(self.folder)[2], [])

    def test_duplicate_registration_rejected(self):
        with self.assertRaisesRegex(evidence.EvidenceError, 'already registered'):
            self.shot('desktop', 80)

    def test_old_capture_cannot_be_registered_as_current(self):
        (self.project / 'index.html').write_text('new code')
        with self.assertRaisesRegex(evidence.EvidenceError, 'STALE_EVIDENCE'):
            self.shot('old', 80)

    def test_crc_and_truncated_png(self):
        path = self.folder / 'bad.png'; png(path)
        good = path.read_bytes()
        for data in (good[:-10], good[:40] + b'corrupt' + good[47:]):
            path.write_bytes(data)
            with self.assertRaises(evidence.EvidenceError): evidence.png_size(path)

    def test_selected_dirty_git_is_supported(self):
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        subprocess.run(['git', '-C', str(self.project), 'add', 'index.html'], check=True)
        subprocess.run(['git', '-C', str(self.project), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-qm', 'baseline'], check=True)
        (self.project / 'index.html').write_text('dirty accepted')
        run = evidence.create_run(self.project, 'http://localhost:9000/', ['index.html'])
        self.assertTrue(evidence.load(run / 'run.json')['project_revision']['dirty'])
        (self.project / 'unselected.txt').write_text('outside declared scope')
        self.assertEqual(evidence.validate(run)[2], [])
        (self.project / 'index.html').write_text('stale selected code')
        self.assertEqual(evidence.validate(run)[2][0]['code'], 'STALE_EVIDENCE')

    def test_deleted_selected_source_is_stale(self):
        (self.project / 'index.html').unlink()
        with self.assertRaisesRegex(evidence.EvidenceError, 'no files'): evidence.validate(self.folder)

    def test_symlink_escape(self):
        (self.folder / 'escape').symlink_to(self.project)
        with self.assertRaises(evidence.EvidenceError): evidence.inside(self.folder, 'escape/index.html')

    def test_receipt_invalid_numeric_fields(self):
        m = evidence.load(self.folder / 'evidence.json'); receipt = m['artifacts'][1]['capture']
        for key, value in [('dpr', True), ('scroll', [0, float('nan')]), ('viewport', [True, 60]), ('regions', {'hero': [0, 0, 90, 60]})]:
            saved = receipt[key]; receipt[key] = value
            with self.assertRaises(evidence.EvidenceError): evidence.capture_valid(receipt, [80, 60])
            receipt[key] = saved

    def test_cli_smoke(self):
        script = ROOT / 'scripts/evidence.py'
        for command in ('validate', 'list'):
            result = subprocess.run([sys.executable, str(script), command, '--run', str(self.folder)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout); self.assertIn('run_id', json.loads(result.stdout))
        result = subprocess.run([sys.executable, str(script), 'create-run', '--project', str(self.project), '--url', 'http://localhost:9000/'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0); self.assertTrue(Path(json.loads(result.stdout)['run']).is_dir())


if __name__ == '__main__': unittest.main()
