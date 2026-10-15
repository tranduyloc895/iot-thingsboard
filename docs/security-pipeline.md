# Security checks in GitHub Actions

The backend and frontend build workflows require `Security scans` to pass before
building an image. Each image is built once, loaded locally, exported to a runner
temporary directory, scanned, and only then pushed to GHCR. The existing GitOps
update and production promotion PR use the registry digest of that scanned image.
Failed checks prevent the push, dev image update, and promotion PR.

## Coverage and policy

| Tool | Coverage | Blocking policy |
| --- | --- | --- |
| Trivy filesystem | Supported dependency manifests/lockfiles, current-tree secrets, Docker/Kubernetes/Helm misconfigurations | HIGH/CRITICAL vulnerabilities and misconfigurations; every secret |
| Semgrep OSS | Source code using `p/security-audit` and `p/owasp-top-ten` | ERROR findings (mapped to HIGH) |
| Trivy image | OS packages, installed application packages, secrets in the final image | HIGH/CRITICAL vulnerabilities; every secret |

Lower severities remain in reports. Unfixed vulnerabilities also block; there is
no blanket ignore file or `continue-on-error`. Scanner crashes, timeouts, invalid
output, Semgrep scan errors, and zero Semgrep coverage fail the gate. Fix findings
or review individual exceptions through code review; do not disable the gate to
publish an image.

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

In GitHub branch protection/rulesets, make **Source security gate** a required
check for `main` and `dev`, require review for production promotion PRs, and
restrict direct pushes. These repository settings must be configured separately;
workflow files cannot enforce them. Allow workflow PR creation if the existing
promotion automation needs it. No paid security service or new credential is
required. The scan job has only `contents: read`; scanners receive no GitHub token
or Docker socket. The publish job retains the permissions used by GitOps.

## HTML reports

Open an Actions run, download `security-source-<run>-<attempt>` or
`security-image-backend-<run>-<attempt>` / `security-image-frontend-<run>-<attempt>`,
unzip, and open **index.html**. `report.json` contains the same normalized findings
for automation. Artifacts are retained for 14 days and uploaded even when a scan
fails. A runner cancellation or failure before report generation can leave no
artifact; the upload step reports that as an error.

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
Semgrep registry must be reachable; download failures block publication.

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
