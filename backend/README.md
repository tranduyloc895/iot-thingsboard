# HCM Flood Tracker backend

Push a change under `backend/` to branch `dev` to run Backend CI. Download the
single `security-backend-*` artifact and open its uniquely named `.html` file for Semgrep and Trivy
results. Demo mode records findings without blocking the build. Image updates
are committed to dev values on `main`; production values change only after a
promotion PR is merged into `main`. Both Devtron environments track `main`.

See [the promotion workflow](../docs/gitops-promotion.md) for the approval steps.
