#!/usr/bin/env python3
"""Send a CI outcome and a ZIP of redacted security reports to a Discord webhook."""
import io
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib import error, parse, request
import uuid
import zipfile

STEP_NAMES = {"scan-source": "Source security scan", "build-local": "Docker build",
              "export-image": "Export image", "scan-image": "Image security scan",
              "security-bundle": "Assemble security report", "security-artifact": "Upload report",
              "registry-login": "GHCR login", "build": "Push image / registry digest",
              "publish-dev": "Commit dev values on main", "promote-prod": "Open production promotion PR"}
MAX_ATTACHMENT = 7 * 1024 * 1024  # Conservative limit below Discord's upload cap.


def prepare(report_dir, env):
    status = env.get("PIPELINE_STATUS", "unknown")
    steps = json.loads(env.get("PIPELINE_STEPS_JSON", "{}"))
    failures = [STEP_NAMES.get(name, name) for name, result in steps.items()
                if result.get("outcome") == "failure"]
    reports = sorted(report_dir.glob("*.json")) if report_dir.is_dir() else []
    security = "Report unavailable (scan/build may not have reached report generation)"
    if reports:
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        findings = [f for scan in data.get("scans", []) for f in scan.get("findings", [])]
        high = sum(f.get("severity") in ("HIGH", "CRITICAL") for f in findings)
        errors = sum(s.get("status") != "complete" for s in data.get("scans", []))
        security = f'{"PASS" if data.get("passed") else "FAIL"} | mode={data.get("gate_mode", "unknown")} | findings={len(findings)}, HIGH/CRITICAL={high}, scanner unavailable={errors}'
    reason = ", ".join(failures) if failures else (
        "All executed steps completed" if status == "success" else "Cancelled, timed out, or failed outside named steps; inspect the Actions run")
    run_url = f'{env.get("GITHUB_SERVER_URL", "https://github.com")}/{env.get("GITHUB_REPOSITORY", "")}/actions/runs/{env.get("GITHUB_RUN_ID", "")}'
    description = f'Commit `{env.get("GITHUB_SHA", "local")[:12]}` · branch `{env.get("GITHUB_REF_NAME", "unknown")}`\nReason: {reason}\nSecurity: {security}\n[Actions run]({run_url})'
    if env.get("REPORT_ARTIFACT_URL"):
        description += f' · [Report artifact]({env["REPORT_ARTIFACT_URL"]})'
    if env.get("PROMOTION_PR_URL"):
        description += f'\n[Production promotion PR — review and merge manually]({env["PROMOTION_PR_URL"]})'
    if re.fullmatch(r"sha256:[0-9a-f]{64}", env.get("IMAGE_DIGEST", "")):
        description += f'\nImage digest: `{env["IMAGE_DIGEST"]}`'
    payload = dict(allowed_mentions=dict(parse=[]), embeds=[dict(
        title=f'{env.get("GITHUB_WORKFLOW", "Pipeline")} — {status.upper()}'[:256],
        description=description[:3900], color=0x2ECC71 if status == "success" else 0xE74C3C,
        footer=dict(text=f'run {env.get("GITHUB_RUN_ID", "local")} · attempt {env.get("GITHUB_RUN_ATTEMPT", "1")}'))])
    attachment = None
    if report_dir.is_dir():
        files = sorted(p for p in report_dir.iterdir() if p.is_file() and p.suffix in (".html", ".json"))
        if files and sum(p.stat().st_size for p in files) <= 32 * 1024 * 1024:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in files:
                    archive.write(path, path.name)
            if buffer.tell() <= MAX_ATTACHMENT:
                attachment = buffer.getvalue()
    if attachment is None:
        payload["embeds"][0]["description"] += "\nZIP not attached (missing report or size limit); use the Actions artifact link."
    else:
        stem = re.sub(r"[^A-Za-z0-9_.-]", "-", reports[0].stem if reports else "security-report")
        payload["attachments"] = [dict(id=0, filename=f"{stem}.zip")]
    return payload, attachment


def send(webhook, payload, attachment):
    url = parse.urlsplit(webhook)
    if url.scheme != "https" or url.hostname not in ("discord.com", "discordapp.com") or not re.fullmatch(r"/api(?:/v\d+)?/webhooks/\d+/[A-Za-z0-9._-]+", url.path):
        raise ValueError("Invalid Discord webhook URL")
    params = parse.parse_qs(url.query)
    params["wait"] = ["true"]
    endpoint = parse.urlunsplit((url.scheme, url.netloc, url.path, parse.urlencode(params, doseq=True), ""))
    headers = {"User-Agent": "HCM-Flood-CI-Notifier/1.0"}
    if attachment is None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    else:
        boundary = uuid.uuid4().hex
        filename = payload["attachments"][0]["filename"]
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n'.encode()
                + json.dumps(payload).encode()
                + f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; filename="{filename}"\r\nContent-Type: application/zip\r\n\r\n'.encode()
                + attachment + f'\r\n--{boundary}--\r\n'.encode())
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    for attempt in range(3):
        try:
            with request.urlopen(request.Request(endpoint, body, headers), timeout=20) as response:
                response.read()
            return
        except error.HTTPError as exc:
            if attempt == 2 or (exc.code != 429 and exc.code < 500):
                raise RuntimeError(f"Discord delivery HTTP {exc.code}") from None
            delay = min(float(exc.headers.get("Retry-After", 2 ** attempt)), 30)
            time.sleep(max(delay, 1))
        except (error.URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("Discord delivery network failure") from None
            time.sleep(2 ** attempt)


def main():
    webhook = os.getenv("DISCORD_CI_WEBHOOK_URL", "")
    if not webhook:
        print("::notice::Discord CI notification disabled: configure DISCORD_CI_WEBHOOK_URL in Actions Secrets.")
        return 0
    # Fork PRs never receive or use the notification credential.
    if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
        print("::notice::Discord notification skipped for pull_request; build notifications run on dev pushes.")
        return 0
    try:
        payload, attachment = prepare(Path(os.getenv("REPORT_DIR", "security-reports")), os.environ)
        send(webhook, payload, attachment)
        print("Discord notification delivered.")
        return 0
    except Exception as exc:
        # Exception text may contain a credential-bearing request URL; never print it.
        print(f"::warning::Discord notification failed ({type(exc).__name__}); inspect webhook permissions/connectivity.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
