#!/usr/bin/env python3
"""Run isolated scanners, publish redacted HTML/JSON, then enforce the gate."""
import argparse
import html
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import uuid

# Version + immutable manifest digest; update together after reviewing upstream releases.
TRIVY = "aquasec/trivy:0.76.0@sha256:2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222"
SEMGREP = "semgrep/semgrep:1.181.0@sha256:81474464c1f07483ba0682a44787fd93c91397419762a04abe2bafaae396304b"


def trivy_findings(data):
    if data.get("SchemaVersion") != 2:
        raise ValueError("unsupported Trivy report schema")
    findings = []
    for result in data.get("Results", []) or []:
        target = result.get("Target", "")
        for item in result.get("Vulnerabilities", []):
            findings.append(dict(kind="dependency", target=target,
                rule=item["VulnerabilityID"], severity=item["Severity"],
                message=f'{item.get("PkgName", "")} {item.get("InstalledVersion", "")}: {item.get("Title", "")}',
                fix=item.get("FixedVersion", "No fix published")))
        for item in result.get("Misconfigurations", []):
            if item.get("Status", "FAIL") == "FAIL":
                findings.append(dict(kind="configuration", target=target,
                    rule=item["ID"], severity=item["Severity"],
                    message=item.get("Title", ""), fix=item.get("Resolution", "")))
        for item in result.get("Secrets", []):
            # Never persist Match, Code, source lines, or the discovered value.
            findings.append(dict(kind="secret", target=f'{target}:{item.get("StartLine", "")}',
                rule=item["RuleID"], severity=item["Severity"],
                message="Secret detected; value and source redacted", fix="Revoke/rotate and remove from source"))
    return findings


def semgrep_findings(data):
    if not data.get("paths", {}).get("scanned"):
        raise ValueError("Semgrep scanned no source files")
    findings = []
    for item in data["results"]:
        extra = item["extra"]
        findings.append(dict(kind="code", target=f'{item["path"]}:{item["start"]["line"]}',
            rule=item["check_id"], severity={"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}.get(extra["severity"], "UNKNOWN"),
            # Rule messages can interpolate source metavariables; exclude them too.
            message="Review the matched security rule; source redacted", fix="Review code at the reported location"))
    return findings


def run_scan(name, image, args, mount, parser):
    command = ["docker", "run", "--rm", "--cap-drop=ALL", "--security-opt=no-new-privileges",
               "--mount", f"type=bind,source={mount},target=/src,readonly",
               "--workdir", "/src", "--env", "HOME=/tmp", "--env", "TRIVY_CACHE_DIR=/tmp/trivy",
               image, *args]
    print(f"Starting {name}", flush=True)
    exit_code = None
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=1200)
        exit_code = process.returncode
        data = json.loads(process.stdout)
        findings = parser(data)
        if process.returncode or data.get("errors"):
            # Only scanner-defined identifiers are retained, never messages/snippets.
            errors = []
            for error in data.get("errors", []):
                details = {key: error[key] for key in ("type", "level", "code")
                           if key in error and re.fullmatch(r"[A-Za-z0-9_ -]{1,80}", str(error[key]))}
                locations = [span["file"] for span in error.get("spans", [])
                             if isinstance(span.get("file"), str)]
                if locations:
                    details["files"] = locations
                if details:
                    errors.append(details)
            return dict(name=name, status="error", exit_code=exit_code,
                        error="Scanner reported errors or a nonzero exit", diagnostics=errors, findings=findings)
        return dict(name=name, status="complete", findings=findings)
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError, AttributeError) as error:
        # Raw stderr/stdout may include secrets. Publish only the error category.
        return dict(name=name, status="error", error=type(error).__name__, exit_code=exit_code, findings=[])


def blocked(finding):
    return finding["kind"] == "secret" or finding["severity"] not in ("MEDIUM", "LOW", "INFO")


def report_name(label, context):
    parts = [label, context["commit"], context["run_id"], f'attempt{context["run_attempt"]}', context["job"]]
    return "-".join(re.sub(r"[^A-Za-z0-9_.-]+", "-", str(part))[:96] for part in parts)


def scanner_name(scan):
    return "semgrep" if scan["name"].startswith("Semgrep") else "trivy"


def write_reports(scans, output, label, gate_mode="enforce", *, split_reports=True, context=None):
    context = context or dict(commit=os.getenv("GITHUB_SHA", "local"),
        run_id=os.getenv("GITHUB_RUN_ID") or f"local-{uuid.uuid4().hex[:12]}",
        run_attempt=os.getenv("GITHUB_RUN_ATTEMPT", "1"),
        job=os.getenv("GITHUB_JOB", "local"), workflow=os.getenv("GITHUB_WORKFLOW", "local"))
    filename = report_name(label, context)
    output.mkdir(parents=True, exist_ok=True)
    failed = any(s["status"] != "complete" or any(map(blocked, s["findings"])) for s in scans)
    report = dict(label=label, **context,
                  passed=not failed, gate_mode=gate_mode,
                  pipeline_passed=not failed or gate_mode == "report-only",
                  tools=dict(trivy=TRIVY, semgrep=SEMGREP), scans=scans)
    serialized = json.dumps(report, indent=2)
    (output / f"{filename}.json").write_text(serialized, encoding="utf-8")
    if split_reports:
        (output / "report.json").write_text(serialized, encoding="utf-8")
    esc = lambda value: html.escape(str(value), quote=True)
    sections = []
    for scan in scans:
        blocking = sum(map(blocked, scan["findings"]))
        detail = ""
        if scan["status"] != "complete":
            detail = f'{scan.get("error", "Scanner error")}; exit={scan.get("exit_code", "unavailable")}; {json.dumps(scan.get("diagnostics", []))}'
        print(f'{scan["name"]}: {scan["status"]}; {len(scan["findings"])} findings; {blocking} blocking. {detail}', flush=True)
        rows = "".join("<tr>" + "".join(f"<td>{esc(f[key])}</td>" for key in
                      ("severity", "kind", "target", "rule", "message", "fix")) + "</tr>" for f in scan["findings"])
        status = "COMPLETE" if scan["status"] == "complete" else "SCANNER ERROR — coverage unavailable; inspect CI runner/network and rerun"
        sections.append(f'<h2>{esc(scan["name"])}</h2><p>{esc(status)} · {len(scan["findings"])} findings · {blocking} blocking</p><p>{esc(detail)}</p>'
                        '<table><thead><tr><th>Severity</th><th>Type</th><th>Location</th><th>Rule</th><th>Finding</th><th>Remediation</th></tr></thead>'
                        f'<tbody>{rows}</tbody></table>')
    status = "FAIL" if failed else "PASS"
    gate_status = "BYPASSED (demo report-only)" if gate_mode == "report-only" else status
    print(f'Security result: {status}; pipeline gate: {gate_status}. Reports: {output / (filename + ".html")} and {output / (filename + ".json")}', flush=True)
    navigation = ""
    if split_reports:
        links = []
        for scan in scans:
            tool = scanner_name(scan)
            target = f'{tool}/{report_name(tool + "-" + label, context)}.html'
            links.append(f'<li><a href="{esc(target)}">{esc(scan["name"])} — separate report</a></li>')
        navigation = "<nav><ul>" + "".join(links) + "</ul></nav>"
    document = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<title>{esc(filename)}</title><style>body{{font:15px system-ui;margin:2rem;color:#172b4d}}'
                'table{border-collapse:collapse;width:100%;margin-bottom:2rem}td,th{border:1px solid #ccc;padding:.6rem;text-align:left;overflow-wrap:anywhere}'
                'th{background:#eef2f7}h1{color:#173d70}</style>'
                f'<h1>Security result: {status}</h1><p>Pipeline gate: {esc(gate_status)} · mode: {esc(gate_mode)}</p>'
                f'<p>{esc(label)} · commit {esc(report["commit"])}</p>'
                f'<p>Workflow: {esc(context["workflow"])} · run {esc(context["run_id"])} · attempt {esc(context["run_attempt"])} · job {esc(context["job"])}</p>'
                '<p>In enforce mode: blocks HIGH/CRITICAL vulnerabilities and misconfigurations, Semgrep ERROR findings, all secrets, and scanner errors. '
                'In report-only demo mode: findings and scanner errors are reported without blocking CI. '
                'Lower severities remain visible. Secret values and source snippets are excluded.</p>'
                + navigation + "".join(sections) + '</html>')
    (output / f"{filename}.html").write_text(document, encoding="utf-8")
    if split_reports:
        (output / "index.html").write_text(document, encoding="utf-8")
        for scan in scans:
            tool = scanner_name(scan)
            write_reports([scan], output / tool, f"{tool}-{label}", gate_mode,
                          split_reports=False, context=context)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(f"### {label}: security result {status} — pipeline gate: {gate_status}\n\nReport: `{filename}.html` (JSON also available).\n\n")
            for scan in scans:
                stream.write(f'- {scan["name"]}: {scan["status"]}, {len(scan["findings"])} findings, {sum(map(blocked, scan["findings"]))} blocking\n')
    return 1 if failed and gate_mode == "enforce" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["source", "image"])
    parser.add_argument("--image-archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--combined-only", action="store_true",
                        help="Write only uniquely named combined HTML/JSON, without aliases or per-tool copies")
    parser.add_argument("--gate-mode", choices=["enforce", "report-only"],
                        default=os.getenv("SECURITY_GATE_MODE", "enforce"))
    args = parser.parse_args()
    if args.gate_mode not in ("enforce", "report-only"):
        parser.error("SECURITY_GATE_MODE must be enforce or report-only")
    if args.mode == "source":
        scans = [run_scan("Trivy: dependencies, secrets, IaC", TRIVY,
            ["fs", "--scanners", "vuln,secret,misconfig", "--format", "json", "--exit-code", "0", "--timeout", "15m",
             "--skip-dirs", ".git,node_modules,security-reports,.agents,.codex", "/src"], Path.cwd(), trivy_findings),
            run_scan("Semgrep: SAST", SEMGREP,
            ["semgrep", "scan", "--config", "p/security-audit", "--config", "p/owasp-top-ten", "--strict",
             "--metrics=off", "--disable-version-check", "--json", "--exclude", "security-reports",
             # Go-templated Helm YAML is parsed by Trivy, not Semgrep's YAML parser.
             "--exclude", "helm/**/templates/**", "/src"],
             Path.cwd(), semgrep_findings)]
    else:
        if not args.image_archive or not args.image_archive.is_file():
            scans = [dict(name="Trivy: image", status="error", error="Missing image archive", findings=[])]
        else:
            archive = args.image_archive.resolve()
            scans = [run_scan("Trivy: image dependencies and secrets", TRIVY,
                ["image", "--input", f"/src/{archive.name}", "--scanners", "vuln,secret", "--format", "json",
                 "--exit-code", "0", "--timeout", "15m"], archive.parent, trivy_findings)]
    return write_reports(scans, args.output, args.mode, args.gate_mode,
                         split_reports=not args.combined_only)


if __name__ == "__main__":
    sys.exit(main())
