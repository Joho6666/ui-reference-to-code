"""Real file invariants using synthetic PNGs; no claims of real browser observation."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from support import ROOT, evidence, fixture, qa_gate as gate


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.folder, self.report, self.shot = fixture(self.project)

    def evaluate(self):
        return gate.evaluate(self.report, self.folder)

    def assertFailure(self, code, status='unverified'):
        result = self.evaluate(); self.assertEqual(result['status'], status)
        self.assertIn(code, [f['code'] for f in result['failures']])

    def artifact(self, identifier):
        m = evidence.load(self.folder / 'evidence.json')
        return m, next(i for i in m['artifacts'] if i['id'] == identifier)

    def test_registered_file_fixture_passes(self):
        self.assertEqual(self.evaluate()['status'], 'verified')

    def test_missing_image(self):
        m, a = self.artifact('desktop'); (self.folder / a['path']).unlink()
        self.assertFailure('EVIDENCE_INVALID')

    def test_corrupt_image_even_with_updated_hash(self):
        m, a = self.artifact('desktop'); path = self.folder / a['path']; path.write_bytes(b'not png')
        a.update(bytes=path.stat().st_size, sha256=evidence.digest(path.read_bytes()))
        evidence.save(self.folder / 'evidence.json', m); self.assertFailure('EVIDENCE_INVALID')

    def test_zero_byte_image(self):
        m, a = self.artifact('desktop'); (self.folder / a['path']).write_bytes(b'')
        self.assertFailure('EVIDENCE_INVALID')

    def test_modified_artifact_hash(self):
        m, a = self.artifact('desktop'); a['sha256'] = '0' * 64
        evidence.save(self.folder / 'evidence.json', m); self.assertFailure('EVIDENCE_INVALID')

    def test_dimensions_must_match_dpr(self):
        m, a = self.artifact('mobile'); a['capture']['dpr'] = 2
        evidence.save(self.folder / 'evidence.json', m); self.assertFailure('VIEWPORT_MISMATCH')

    def test_old_code_screenshot(self):
        (self.project / 'index.html').write_text('<h1>Changed</h1>')
        self.assertFailure('STALE_EVIDENCE')

    def test_added_source_file_invalidates_all_selection(self):
        (self.project / 'new.css').write_text('body{color:red}')
        self.assertFailure('STALE_EVIDENCE')

    def test_wrong_run(self):
        self.report['run_id'] = 'another'
        with self.assertRaises(gate.ReportError): self.evaluate()

    def test_unknown_versions(self):
        for name in ('qa', 'run', 'evidence'):
            with self.subTest(name=name):
                if name == 'qa':
                    self.report['schema_version'] = 99
                    with self.assertRaisesRegex(gate.ReportError, 'unsupported schema_version'): self.evaluate()
                    self.report['schema_version'] = 2
                else:
                    path = self.folder / (name + '.json'); saved = evidence.load(path); modified = copy.deepcopy(saved)
                    modified['schema_version'] = 99; evidence.save(path, modified)
                    with self.assertRaisesRegex(gate.ReportError, 'unsupported schema_version'): self.evaluate()
                    evidence.save(path, saved)

    def test_fake_evidence_id(self):
        self.report['dimensions']['layout']['evidence'][0]['artifact_id'] = 'invented'
        self.assertFailure('EVIDENCE_INVALID')

    def test_low_confidence_high_score(self):
        self.report['dimensions']['color']['confidence'] = 'low'
        self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_null_and_missing_evidence(self):
        for field, value in [('score', None), ('evidence', [])]:
            saved = self.report['dimensions']['layout'][field]; self.report['dimensions']['layout'][field] = value
            self.assertFailure('EVIDENCE_INSUFFICIENT'); self.report['dimensions']['layout'][field] = saved

    def test_unobserved_images(self):
        m, a = self.artifact('mobile'); a.update(observed=False, observer='unobserved')
        evidence.save(self.folder / 'evidence.json', m); self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_threshold_not_averaged(self):
        self.report['dimensions']['responsive']['score'] = 6
        self.assertFailure('VISUAL_MAJOR', 'needs-repair')
        self.report['dimensions']['responsive']['score'] = 7
        self.assertEqual(self.evaluate()['status'], 'verified')

    def test_nan_bool_scores(self):
        for value in (True, float('nan'), float('inf'), -1, 11):
            self.report['dimensions']['layout']['score'] = value
            with self.assertRaises(gate.ReportError): self.evaluate()

    def test_preservation_missing(self):
        self.report['preservation_checks'] = []
        self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_content_regression(self):
        m, a = self.artifact('preserve'); path = self.folder / a['path']; data = evidence.load(path)
        data['checks'][0].update(observed='#wrong', passed=False); evidence.save(path, data)
        a.update(bytes=path.stat().st_size, sha256=evidence.digest(path.read_bytes())); evidence.save(self.folder / 'evidence.json', m)
        self.assertFailure('CONTENT_REGRESSION', 'needs-repair')

    def test_unrelated_region(self):
        self.report['dimensions']['layout']['evidence'][0]['region_id'] = 'unknown'
        self.assertFailure('EVIDENCE_INVALID')

    def test_path_escape(self):
        m, a = self.artifact('desktop'); a['path'] = '../outside.png'; evidence.save(self.folder / 'evidence.json', m)
        with self.assertRaises(gate.ReportError): self.evaluate()

    def difference(self):
        return {'id': 'V1', 'severity': 'Major', 'region_id': 'hero', 'expected': 'CTA fits', 'observed': 'CTA overflows',
                'reference_artifact': 'spec', 'implementation_artifact': 'mobile', 'resolved': False, 'resolution': None}

    def test_boolean_resolution_cannot_pass(self):
        self.report['differences'] = [self.difference()]; self.assertFailure('VISUAL_MAJOR', 'needs-repair')
        self.report['differences'][0]['resolved'] = True; self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_same_resolution_capture_cannot_pass(self):
        self.report['differences'] = [self.difference()]
        self.report['differences'][0].update(resolved=True, resolution={'artifact_id': 'mobile', 'reviewed': True, 'observation': 'fixed'})
        self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_later_changed_resolution_capture(self):
        self.report['differences'] = [self.difference()]; self.report['iteration'] = 2
        self.shot('mobile-fixed', 40, color=240, iteration=2)
        self.report['differences'][0].update(resolved=True, resolution={'artifact_id': 'mobile-fixed', 'reviewed': True, 'observation': 'CTA fits'})
        self.assertEqual(self.evaluate()['status'], 'verified')

    def test_identical_bytes_even_new_capture_do_not_resolve(self):
        self.report['differences'] = [self.difference()]; self.report['iteration'] = 2
        self.shot('mobile-repeat', 40, iteration=2)
        self.report['differences'][0].update(resolved=True, resolution={'artifact_id': 'mobile-repeat', 'reviewed': True, 'observation': 'claimed fixed'})
        self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_previous_major_cannot_be_deleted(self):
        old = copy.deepcopy(self.report); old['differences'] = [self.difference()]
        evidence.save(self.folder / 'qa-1.json', old); self.report['iteration'] = 2
        self.assertFailure('EVIDENCE_INSUFFICIENT')

    def set_pixel(self):
        self.report['modifiers'] = ['E']
        self.report['dimensions'] = {n: copy.deepcopy(self.report['dimensions']['interaction' if n == 'interaction' else 'responsive' if n == 'responsive' else 'layout']) for n in gate.E_DIMENSIONS}
        self.shot('ref-desktop', 80, role='reference'); self.shot('ref-mobile', 40, role='reference')
        for c, r in zip(self.report['comparisons'], ['ref-desktop', 'ref-mobile']): c.update(kind='reference', reference_artifact=r)

    def test_pixel_matched(self):
        self.set_pixel(); self.assertEqual(self.evaluate()['status'], 'verified')

    def test_pixel_theme_state_viewport_scroll_mismatch(self):
        self.set_pixel()
        for key, val in [('theme', 'dark'), ('state', 'open'), ('viewport', [81, 60]), ('dpr', 2), ('scroll', [0, 50])]:
            m, a = self.artifact('ref-desktop'); old = a['capture'][key]; a['capture'][key] = val
            evidence.save(self.folder / 'evidence.json', m); self.assertFailure('VIEWPORT_MISMATCH')
            a['capture'][key] = old; evidence.save(self.folder / 'evidence.json', m)

    def test_inspiration_uses_own_dimensions(self):
        self.report['modifiers'] = ['F']
        with self.assertRaises(gate.ReportError): self.evaluate()
        self.report['dimensions'] = {n: copy.deepcopy(self.report['dimensions']['interaction' if n == 'interaction' else 'responsive' if n == 'responsive' else 'layout']) for n in gate.F_DIMENSIONS}
        self.assertEqual(self.evaluate()['status'], 'verified')

    def test_browser_interaction_failure_needs_repair(self):
        m, a = self.artifact('preserve'); path = self.folder / a['path']; data = evidence.load(path)
        data['checks'][0].update(method='browser-interaction', passed=False, observed='#wrong')
        evidence.save(path, data); a.update(bytes=path.stat().st_size, sha256=evidence.digest(path.read_bytes()))
        evidence.save(self.folder / 'evidence.json', m)
        self.assertFailure('FUNCTION_REGRESSION', 'needs-repair')

    def test_duplicate_design_region_rejected(self):
        m, a = self.artifact('spec'); path = self.folder / a['path']; spec = evidence.load(path)
        spec['regions'].append(copy.deepcopy(spec['regions'][0])); evidence.save(path, spec)
        a.update(bytes=path.stat().st_size, sha256=evidence.digest(path.read_bytes()))
        evidence.save(self.folder / 'evidence.json', m)
        with self.assertRaisesRegex(gate.ReportError, 'duplicate region'):
            self.evaluate()

    def test_code_log_cannot_be_only_passed_boolean(self):
        self.report['code_checks'] = []
        self.assertFailure('EVIDENCE_INSUFFICIENT')

    def test_cli_exit_codes(self):
        path = self.folder / 'qa.json'
        for expected in (0, 1, 2, 3):
            self.report['dimensions']['layout']['score'] = 8 if expected == 0 else 6 if expected == 1 else None
            evidence.save(path, self.report)
            if expected == 3: path.write_text('{')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/qa_gate.py'), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            self.assertIn('status', json.loads(result.stdout))


if __name__ == '__main__': unittest.main()
