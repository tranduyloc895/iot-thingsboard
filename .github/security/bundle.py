#!/usr/bin/env python3
"""Combine source and image findings into one HTML/JSON report per build."""
import argparse
import json
import os
from pathlib import Path

from scan import report_name, write_reports


def bundle(output, component, gate_mode):
    scans = []
    context = None
    for phase in ("source", "image"):
        path = output / phase / "report.json"
        if path.is_file():
            report = json.loads(path.read_text(encoding="utf-8"))
            context = context or {key: report[key] for key in
                ("commit", "run_id", "run_attempt", "job", "workflow")}
            scans.extend(report["scans"])
        else:
            scans.append(dict(name=f"{phase}: not run", status="not-run",
                              error="Scan stage did not produce a report", findings=[]))
    if context is None:
        context = dict(commit=os.getenv("GITHUB_SHA", "local"), run_id=os.getenv("GITHUB_RUN_ID", "local"),
                       run_attempt=os.getenv("GITHUB_RUN_ATTEMPT", "1"), job=os.getenv("GITHUB_JOB", component),
                       workflow=os.getenv("GITHUB_WORKFLOW", "local"))
    label = f"security-{component}"
    result = write_reports(scans, output, label, gate_mode, split_reports=False, context=context)
    filename = report_name(label, context)
    # Convenient entry point; canonical filenames still identify the commit/run/job.
    (output / "index.html").write_bytes((output / f"{filename}.html").read_bytes())
    (output / "report.json").write_bytes((output / f"{filename}.json").read_bytes())
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--component", choices=["backend", "frontend"], required=True)
    parser.add_argument("--gate-mode", choices=["enforce", "report-only"], default=os.getenv("SECURITY_GATE_MODE", "enforce"))
    args = parser.parse_args()
    if args.gate_mode not in ("enforce", "report-only"):
        parser.error("Invalid SECURITY_GATE_MODE")
    raise SystemExit(bundle(args.output, args.component, args.gate_mode))
