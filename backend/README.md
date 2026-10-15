# HCM Flood Tracker backend

Push a change under `backend/` to branch `dev` to run Backend CI. Download the
single `security-backend-*` artifact and open `index.html` for Semgrep and Trivy
results. Demo mode records findings without blocking the build. Image updates
stay on `dev`; production promotion requires a PR merge into `main`.

See [the promotion workflow](../docs/gitops-promotion.md) for the approval steps.
