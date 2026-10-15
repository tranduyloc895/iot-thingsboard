# Security checks in GitHub Actions

The backend and frontend build workflows require `Security scans` to pass before
building an image. Each image is built once, loaded locally, exported to a runner
temporary directory, scanned, and only then pushed to GHCR. The GitOps update writes only the dev values on branch `dev`. A separate
promotion PR changes only prod values on `main`, using the registry digest of
that same image. See [the approval workflow](gitops-promotion.md).

## Coverage and policy

| Tool | Coverage | Blocking policy |
| --- | --- | --- |
| Trivy filesystem | Supported dependency manifests/lockfiles, current-tree secrets, Docker/Kubernetes/Helm misconfigurations | HIGH/CRITICAL vulnerabilities and misconfigurations; every secret |
| Semgrep OSS | Source code using `p/security-audit` and `p/owasp-top-ten` | ERROR findings (mapped to HIGH) |
| Trivy image | OS packages, installed application packages, secrets in the final image | HIGH/CRITICAL vulnerabilities; every secret |

The workflows currently default to **demo `report-only` mode**: all scans still
run, HTML/JSON artifacts are still uploaded, and security findings or scanner
errors do not block CI. Build, registry, Git, PR creation, and artifact upload
failures still fail normally. This mode does not repair or conceal findings.

Use **Settings → Secrets and variables → Actions → Variables** to create or edit
repository variable `SECURITY_GATE_MODE`:

| Value | CI behavior |
| --- | --- |
| `report-only` (workflow default if unset) | Allow CI to proceed; explicitly label the gate BYPASSED for demo |
| `enforce` | Fail CI on blocking findings or scanner errors |

This variable controls both source scans and image scans. Report JSON retains
`passed` as the actual security result and adds `pipeline_passed` and `gate_mode`.
HTML and job summaries display the security result separately from the pipeline
gate. Reports can therefore say FAIL while a demo pipeline succeeds. The local
CLI defaults to `enforce`; use `--gate-mode report-only` for an explicit local
bypass. An invalid mode fails rather than silently bypassing.

In `enforce` mode, lower severities remain in reports and unfixed HIGH/CRITICAL
vulnerabilities block too. Scanner crashes, timeouts, invalid output, Semgrep scan
errors, and zero Semgrep coverage also block.

Filesystem dependency analysis depends on supported manifests and lockfiles;
the image scan covers the resolved Python packages installed from the backend's
unpinned requirements. Scanning final frontend images alone would miss npm build
dependencies, so source dependency scanning is required too. IaC scanning covers
the checked-in configurations and scanner-supported Helm evaluation; this does
not replace deployment-specific rendering/policy checks or live cluster audits.
Secret scanning covers the current checkout and image, not all Git history.
Semgrep excludes `helm/**/templates/**`: these are Go templates rather than plain
YAML and cause syntax errors in its YAML parser. Trivy still scans those Helm
templates; the exclusion does not apply to the IaC scan.
These checks do not perform authenticated DAST against a running environment.

## Triggers and required checks

`security.yml` runs on PRs to `main`/`dev`, pushes to those branches, manual runs,
and daily at 01:23 UTC (08:23 Vietnam time). The daily scan uses the default
branch and fresh vulnerability data. The build workflows also call it directly,
so their dependency gate does not rely on a separate workflow finishing first.
The standalone run can overlap with a build's source scan.

Where supported by your GitHub plan, require **Source security gate** and at
least one approval for `main`, and restrict direct pushes. Keep bot writes to
dev allowed, since CI commits dev image values there. These repository settings must be configured separately;
workflow files cannot enforce them. Allow workflow PR creation if the existing
promotion automation needs it. No paid security service or new credential is
required. The scan job has only `contents: read`; scanners receive no GitHub token
or Docker socket. The publish job retains the permissions used by GitOps.

## HTML reports

Each Actions run now publishes clearly named artifacts:

| Artifact prefix | Contents |
| --- | --- |
| `security-source-` | Combined source report, with links to individual scanner reports |
| `semgrep-source-` | Semgrep SAST only, HTML + normalized JSON |
| `trivy-source-` | Trivy dependencies, secrets, IaC only, HTML + normalized JSON |
| `trivy-image-backend-` / `trivy-image-frontend-` | Image scan report for the component |

Every artifact name ends with `<full-commit-sha>-<run-id>-attempt<attempt>`.
The run ID separates workflows scanning the same commit, and the attempt separates
reruns. HTML/JSON filenames additionally include the job ID, for example:

```text
semgrep-source-<full-sha>-38679651208-attempt1-source-security.html
semgrep-source-<full-sha>-38679651208-attempt1-source-security.json
```

Download the `semgrep-source-*` artifact to see Semgrep directly; open its named
HTML file. Semgrep previously appeared inside the combined `security-source`
report; it was already being scanned. Individual reports are also generated when
the scanner errors or finds nothing, so missing coverage is visible.

The combined artifact retains `index.html` / `report.json` as convenience aliases
alongside uniquely named files. Its `index.html` links to `semgrep/` and `trivy/`.
Commit, workflow, job, run ID, and attempt are embedded in each report. Artifacts
are retained for 14 days and uploaded even when a scan fails. A runner cancellation
or failure before report generation can leave no artifact; the upload step reports
that as an error.

Reports contain commit identity, gate status, locations, rule/CVE IDs, severity,
and remediation information. Secret values, source snippets, Semgrep messages
(which may interpolate source), and raw scanner output are excluded. Findings
are HTML-escaped. Treat reports as internal security information and limit
repository/Actions access. Reports are not published to a public website.
The scan step also prints finding/blocker counts and safe scanner error identifiers
and exit codes, so a policy failure can be distinguished from an operational error.

## Maintenance and local verification

Scanner containers are pinned by version and immutable registry manifest digest
in `.github/security/scan.py`; Actions are pinned by commit SHA. Review upstream
releases and update versions and digests together. Trivy databases/check bundles
and Semgrep registry rule packs are downloaded at scan time for current coverage;
rule packs are not immutable. Docker Hub, Trivy database registries, and the
Semgrep registry must be reachable. In enforce mode, download failures block
publication; demo report-only mode records the failure and allows CI to proceed.

Run from the repository root with Python 3 and a running Linux Docker engine:

```sh
python3 -m unittest discover -s .github/security -p 'test_*.py' -v
python3 .github/security/scan.py source --output security-reports/source
docker build -t hcm-flood-backend:security ./backend
mkdir -p /tmp/hcm-security-image
docker save hcm-flood-backend:security -o /tmp/hcm-security-image/image.tar
python3 .github/security/scan.py image --image-archive /tmp/hcm-security-image/image.tar --output security-reports/image
```

To revert the integration, revert the security integration commit through a
reviewed PR and rerun CI; this removes the gate and reports. No Kubernetes
resources or running deployments are changed by this integration itself.
