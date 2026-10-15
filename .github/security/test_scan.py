"""Regression tests for the security gate and report data handling (no Docker needed)."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("scan", Path(__file__).with_name("scan.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


class SecurityGateTests(unittest.TestCase):
    def test_thresholds_and_secrets(self):
        for kind in ("dependency", "configuration", "code"):
            for severity in ("HIGH", "CRITICAL", "UNKNOWN", "unexpected"):
                self.assertTrue(scan.blocked(dict(kind=kind, severity=severity)))
            for severity in ("MEDIUM", "LOW"):
                self.assertFalse(scan.blocked(dict(kind=kind, severity=severity)))
        self.assertTrue(scan.blocked(dict(kind="secret", severity="LOW")))

    def test_secret_data_and_source_are_never_published(self):
        marker = "DO_NOT_PUBLISH_SECRET_VALUE"
        raw = dict(SchemaVersion=2, Results=[dict(Target=".env", Secrets=[dict(
            RuleID="test-secret", Severity="HIGH", Match=marker,
            Code=dict(Lines=[dict(Content=marker)]), StartLine=3)])])
        findings = scan.trivy_findings(raw)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.assertEqual(scan.write_reports([dict(name="Trivy", status="complete", findings=findings)], output, "source"), 1)
            for path in output.iterdir():
                self.assertNotIn(marker, path.read_text(encoding="utf-8"))

    def test_html_escapes_untrusted_fields(self):
        finding = dict(kind="dependency", severity="HIGH", target='<script>alert("x")</script>',
                       rule="CVE-test", message="unsafe <img src=x onerror=alert(1)>", fix="upgrade")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            scan.write_reports([dict(name="test", status="complete", findings=[finding])], output, "source")
            content = (output / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>", content)
            self.assertNotIn("<img", content)
            self.assertIn("&lt;script&gt;", content)

    def test_semgrep_maps_severity_without_source_or_messages(self):
        raw = dict(paths=dict(scanned=["app.py"]), results=[dict(check_id="python.test", path="app.py", start=dict(line=4),
                   extra=dict(severity="ERROR", lines="SECRET_VALUE", message="SECRET_VALUE"))])
        findings = scan.semgrep_findings(raw)
        self.assertEqual(findings[0]["severity"], "HIGH")
        self.assertNotIn("SECRET_VALUE", json.dumps(findings))

    def test_semgrep_empty_coverage_fails(self):
        with self.assertRaises(ValueError):
            scan.semgrep_findings(dict(results=[], paths=dict(scanned=[])))

    def test_scanner_errors_fail_and_still_write_reports(self):
        outcomes = [OSError("SECRET_VALUE"), subprocess.TimeoutExpired("docker", 1200),
                    subprocess.CompletedProcess([], 1, "", "SECRET_VALUE"),
                    subprocess.CompletedProcess([], 0, "not-json", ""),
                    subprocess.CompletedProcess([], 0, '{"errors":[{"message":"SECRET_VALUE"}]}', ""),
                    subprocess.CompletedProcess([], 0, '{}', "")]
        for outcome in outcomes:
            kwargs = dict(side_effect=outcome) if isinstance(outcome, Exception) else dict(return_value=outcome)
            with self.subTest(outcome=type(outcome).__name__), patch.object(scan.subprocess, "run", **kwargs):
                result = scan.run_scan("Trivy", scan.TRIVY, [], Path.cwd(), scan.trivy_findings)
                self.assertEqual(result["status"], "error")
                with tempfile.TemporaryDirectory() as directory:
                    self.assertEqual(scan.write_reports([result], Path(directory), "source"), 1)
                    self.assertTrue((Path(directory) / "index.html").is_file())
                    self.assertNotIn("SECRET_VALUE", (Path(directory) / "report.json").read_text())

    def test_success_with_no_findings_and_container_isolation(self):
        with patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 0, '{"SchemaVersion":2,"Results":[]}', "")) as run:
            result = scan.run_scan("Trivy", scan.TRIVY, ["fs", "/src"], Path.cwd(), scan.trivy_findings)
            command = run.call_args.args[0]
            self.assertIn("--cap-drop=ALL", command)
            self.assertTrue(any("readonly" in item for item in command))
            self.assertFalse(any("docker.sock" in item or "GITHUB_TOKEN" in item for item in command))
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(scan.write_reports([result], Path(directory), "source"), 0)

    def test_semgrep_nonzero_preserves_findings_and_safe_diagnostics(self):
        data = dict(paths=dict(scanned=["app.py"]), results=[dict(check_id="test", path="app.py", start=dict(line=1),
                    extra=dict(severity="ERROR", message="SECRET_VALUE"))],
                    errors=[dict(type="PartialParsing", level="warn", code=3, message="SECRET_VALUE",
                                 spans=[dict(file="app.py", source="SECRET_VALUE")])])
        with patch.object(scan.subprocess, "run", return_value=subprocess.CompletedProcess([], 3, json.dumps(data), "SECRET_VALUE")):
            result = scan.run_scan("Semgrep", scan.SEMGREP, [], Path.cwd(), scan.semgrep_findings)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["exit_code"], 3)
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["diagnostics"], [dict(type="PartialParsing", level="warn", code=3, files=["app.py"])])
        self.assertNotIn("SECRET_VALUE", json.dumps(result))

    def test_missing_archive_fails_with_report(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("sys.argv", ["scan.py", "image", "--output", directory]):
                self.assertEqual(scan.main(), 1)
            self.assertFalse(json.loads((Path(directory) / "report.json").read_text())["passed"])

    def test_demo_passes_ci_without_hiding_failed_security_result(self):
        finding = dict(kind="dependency", severity="CRITICAL", target="app", rule="CVE-test", message="test", fix="upgrade")
        for results in ([dict(name="Trivy", status="complete", findings=[finding])],
                        [dict(name="Semgrep", status="error", error="TimeoutExpired", findings=[])]):
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                self.assertEqual(scan.write_reports(results, output, "source", "report-only"), 0)
                report = json.loads((output / "report.json").read_text())
                self.assertFalse(report["passed"])
                self.assertTrue(report["pipeline_passed"])
                self.assertEqual(report["gate_mode"], "report-only")
                content = (output / "index.html").read_text(encoding="utf-8")
                self.assertIn("Security result: FAIL", content)
                self.assertIn("BYPASSED (demo report-only)", content)


if __name__ == "__main__":
    unittest.main()
