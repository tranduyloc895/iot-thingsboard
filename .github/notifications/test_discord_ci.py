import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

spec = importlib.util.spec_from_file_location("discord_ci", Path(__file__).with_name("discord_ci.py"))
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class NotificationTests(unittest.TestCase):
    def test_failure_reason_and_report_attached_without_duplicate_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "security-test.json").write_text(json.dumps(dict(passed=False, gate_mode="report-only", scans=[
                dict(status="complete", findings=[dict(severity="HIGH")])])), encoding="utf-8")
            (path / "security-test.html").write_text("<html>redacted report</html>", encoding="utf-8")
            env = dict(PIPELINE_STATUS="failure", PIPELINE_STEPS_JSON=json.dumps({"publish-dev": {"outcome": "failure"}}))
            payload, attachment = ci.prepare(path, env)
            description = payload["embeds"][0]["description"]
            self.assertIn("Commit dev values on main", description)
            self.assertIn("mode=report-only", description)
            self.assertIn("HIGH/CRITICAL=1", description)
            self.assertEqual(payload["allowed_mentions"], {"parse": []})
            with zipfile.ZipFile(io.BytesIO(attachment)) as archive:
                self.assertEqual(sorted(archive.namelist()), ["security-test.html", "security-test.json"])

    def test_missing_reports_still_send_pipeline_failure(self):
        payload, attachment = ci.prepare(Path("nonexistent-report-dir"), {"PIPELINE_STATUS": "failure"})
        self.assertIsNone(attachment)
        self.assertIn("Report unavailable", payload["embeds"][0]["description"])

    def test_webhook_must_be_discord_https(self):
        with self.assertRaises(ValueError):
            ci.send("https://example.com/api/webhooks/123/test", {}, None)

    def test_rate_limit_retries_without_changing_payload(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        with patch.object(ci.request, "urlopen", side_effect=[
                HTTPError("credential-url", 429, "rate limit", {"Retry-After": "1"}, None), response]) as send, patch.object(ci.time, "sleep"):
            ci.send("https://discord.com/api/webhooks/123/test", {"allowed_mentions": {"parse": []}}, None)
            self.assertEqual(send.call_count, 2)

    def test_failure_logging_never_exposes_webhook(self):
        with patch.dict(ci.os.environ, {"DISCORD_CI_WEBHOOK_URL": "SECRET_URL", "GITHUB_EVENT_NAME": "push"}), \
                patch.object(ci, "prepare", side_effect=ValueError("SECRET_URL")), \
                patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(ci.main(), 1)
            self.assertNotIn("SECRET_URL", output.getvalue())


if __name__ == "__main__":
    unittest.main()
