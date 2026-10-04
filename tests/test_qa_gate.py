"""Meaningful failure paths for the visual completion gate (no browser claims)."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "qa_gate.py"
spec = importlib.util.spec_from_file_location("qa_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def report():
    return {
        "schema_version": 1, "mode": "D", "modifiers": [], "scope": "hero", "iteration": 1,
        "code_checks": "passed", "preservation": "passed",
        "browser": {
            "desktop": {"observed": True, "screenshot": "desktop.png", "viewport": [1440, 900]},
            "mobile": {"observed": True, "screenshot": "mobile.png", "viewport": [390, 844]},
        },
        "comparison": {"reviewed": True, "kind": "design-spec", "baseline": "spec.md",
                       "implemented": "desktop.png", "same_conditions": False},
        "dimensions": {name: {"applicable": True, "score": 8, "evidence": ["observation:" + name]}
                       for name in gate.DIMENSIONS},
        "differences": [],
    }


class GateTests(unittest.TestCase):
    def test_observed_report_passes(self):
        self.assertEqual(gate.evaluate(report())["status"], "verified")

    def test_threshold_is_not_averaged(self):
        data = report()
        for name in gate.DIMENSIONS:
            data["dimensions"][name]["score"] = 10
        data["dimensions"]["responsive"]["score"] = 6
        self.assertEqual(gate.evaluate(data)["status"], "needs-repair")
        data["dimensions"]["responsive"]["score"] = 7
        self.assertEqual(gate.evaluate(data)["status"], "verified")

    def test_missing_mobile_prevents_completion(self):
        data = report()
        data["browser"]["mobile"]["observed"] = False
        self.assertEqual(gate.evaluate(data)["status"], "unverified")

    def test_high_score_without_evidence_does_not_pass(self):
        data = report()
        data["dimensions"]["color"]["evidence"] = []
        self.assertEqual(gate.evaluate(data)["status"], "unverified")

    def test_unknown_score_is_not_a_default_pass(self):
        data = report()
        data["dimensions"]["layout"]["score"] = None
        self.assertEqual(gate.evaluate(data)["status"], "unverified")

    def test_severe_defect_wins_over_high_scores(self):
        data = report()
        data["differences"] = [{"id": "V1", "severity": "Critical", "resolved": False,
                                "location": "hero", "evidence": "mobile.png", "description": "CTA covered"}]
        self.assertEqual(gate.evaluate(data)["status"], "needs-repair")
        data["differences"][0]["resolved"] = True
        self.assertEqual(gate.evaluate(data)["status"], "verified")

    def test_minor_difference_can_remain(self):
        data = report()
        data["differences"] = [{"id": "V2", "severity": "Minor", "resolved": False,
                                "location": "card", "evidence": "desktop.png", "description": "1px radius difference"}]
        self.assertEqual(gate.evaluate(data)["status"], "verified")

    def test_fidelity_requires_matched_reference(self):
        data = report()
        data["modifiers"] = ["E"]
        self.assertEqual(gate.evaluate(data)["status"], "unverified")
        data["comparison"].update(kind="reference", baseline="source.png", same_conditions=True)
        self.assertEqual(gate.evaluate(data)["status"], "verified")

    def test_content_regression_fails(self):
        data = report()
        data["preservation"] = "failed"
        self.assertEqual(gate.evaluate(data)["status"], "needs-repair")

    def test_only_scoped_dimensions_can_be_not_applicable(self):
        data = report()
        data["dimensions"]["interaction"] = {"applicable": False, "score": None, "reason": "No interactive component changed"}
        self.assertEqual(gate.evaluate(data)["status"], "verified")
        data["dimensions"]["responsive"] = copy.deepcopy(data["dimensions"]["interaction"])
        with self.assertRaises(gate.ReportError):
            gate.evaluate(data)

    def test_malformed_scores_and_dimensions_are_rejected(self):
        for score in (True, float("nan"), float("inf"), -1, 11):
            with self.subTest(score=score):
                data = report()
                data["dimensions"]["layout"]["score"] = score
                with self.assertRaises(gate.ReportError):
                    gate.evaluate(data)
        data = report()
        data["dimensions"].pop("responsive")
        with self.assertRaises(gate.ReportError):
            gate.evaluate(data)

    def test_cli_exit_codes_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "qa.json"
            data = report()
            for expected in (0, 1, 2):
                if expected == 1:
                    data["dimensions"]["layout"]["score"] = 6
                elif expected == 2:
                    data["dimensions"]["layout"]["score"] = None
                path.write_text(json.dumps(data), encoding="utf-8")
                result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected)
                self.assertIn("status", json.loads(result.stdout))
            path.write_text("{", encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads(result.stdout)["status"], "invalid-report")


if __name__ == "__main__":
    unittest.main()
