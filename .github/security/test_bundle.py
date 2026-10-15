import json
from pathlib import Path
import tempfile
import unittest

from bundle import bundle


class BundleTests(unittest.TestCase):
    def test_combines_all_scanners_in_one_entry_point(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            context = dict(commit="a" * 40, run_id="123", run_attempt="1", job="build", workflow="Frontend")
            for phase, names in (("source", ["Trivy: source", "Semgrep: SAST"]), ("image", ["Trivy: image"])):
                folder = output / phase
                folder.mkdir()
                (folder / "report.json").write_text(json.dumps(dict(context, scans=[
                    dict(name=name, status="complete", findings=[]) for name in names])))
            self.assertEqual(bundle(output, "frontend", "enforce"), 0)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(len(report["scans"]), 3)
            content = (output / "index.html").read_text(encoding="utf-8")
            for name in ("Trivy: source", "Semgrep: SAST", "Trivy: image"):
                self.assertIn(name, content)
            self.assertTrue(report["passed"])

    def test_missing_phase_is_visible_and_enforce_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.assertEqual(bundle(output, "backend", "enforce"), 1)
            report = json.loads((output / "report.json").read_text())
            self.assertFalse(report["passed"])
            self.assertTrue(all(s["status"] == "not-run" for s in report["scans"]))
            self.assertEqual(bundle(output, "backend", "report-only"), 0)
            self.assertFalse(json.loads((output / "report.json").read_text())["passed"])


if __name__ == "__main__":
    unittest.main()
