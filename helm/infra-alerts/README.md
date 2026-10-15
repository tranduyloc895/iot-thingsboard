# HCM Flood infrastructure alerts

Independent chart for the existing CMC cluster. It creates only notification
Prometheus, Alertmanager, configuration, Services, NetworkPolicy and two retained
PVCs. It does not adopt or update the existing observability Helm release.
Do not enable notifications in both charts: that would send duplicate alerts.

## Before sync

- Create Secret `discord-infra-webhook`, key `webhook-url`, in `cmc-monitoring`.
  Paste the HCM Infra Alerts Discord webhook in the Secret UI; never commit it.
- Source Prometheus: `prometheus-server.cmc-monitoring.svc.cluster.local:80`.
- Actual workload namespaces: `flood-portal`, `flood-portal-dev`, `thingsboard`, `ingress-nginx`.
- Default StorageClass `highio` was observed; requests are 5 GiB + 1 GiB.
- Check source metrics and `/federate` before enabling. HPA metrics require HPAs;
  ingress request metrics require ingress-nginx metrics to be enabled and scraped.

## Devtron / ArgoCD deployment

Merge the chart into main. In Devtron Resource Browser, create the Application
from `gitops/infra-alerts.yaml` in `argocd`. It uses the existing repository and
ArgoCD credentials, points to main, and has **manual sync** (no automated policy).
Open Infrastructure Management -> Applications -> ArgoCD Apps -> hcm-flood-alerts.
Review the diff, confirm only the new hcm-flood-alerts resources, then sync after
approval. Never import/adopt the existing observability release.

Chart defaults disabled. The Application explicitly enables notifications.
Defaults: node CPU >80%, node memory >85%, pod CPU/memory >requests, container
memory >90% limit, ingress >100 RPS; thresholds sustained for 5 minutes.
Node/HPA changes are coalesced over 5-minute windows, not a per-event audit log.
Resource alerts send FIRING and RESOLVED; scaling sends change notifications only.

## Verify

Check both new Deployments Ready, PVCs Bound, Prometheus federation UP, rule
health, and Alertmanager delivery. Use internal port forwarding/Devtron terminal;
there is no public ingress. Submit a short-lived `DiscordSetupTest` alert to
Alertmanager `/api/v2/alerts` first; then test HPA/thresholds in dev only.
An end-to-end delivery test is still required after provisioning the Secret.

Offline validation (Python PyYAML, Helm, promtool and amtool):

```sh
helm lint helm/infra-alerts --set notifications.enabled=true
python tools/validate_infra_alerts.py
```

## Rollback

Set Application Helm values `notifications.enabled: false` in Git, review diff,
and sync with prune to remove only this chart's workloads/config/services/policy.
PVCs carry `helm.sh/resource-policy: keep` and `argocd.argoproj.io/sync-options:
Prune=false` to retain data/silences. Keep the webhook Secret. Do not delete the
existing observability release. If deleting the Application instead, use
non-cascading deletion; explicitly remove only this app's resources after review.

## Observed preflight (2026-10-15)

Source `/federate` returned HTTP 200. Node exporter, kube-state-metrics,
cAdvisor CPU/memory/requests and HPA series were present. Source reported 9
nodes and 7 HPA series. The Discord Secret was absent at inspection.
`nginx_ingress_controller_requests` was absent; controller args lacked
`--enable-metrics`, and only the traffic/admission Services existed.

The existing ingress-nginx release is chart 4.15.1 / app 1.15.1, revision 1.
`gitops/ingress-nginx-metrics.values.yaml` is a proposed values overlay for that
release, not part of this Application and not deployed automatically. Merge it
with existing ingress values in Devtron and inspect the rendered diff. Preserve
all LB, replica, autoscaler and scheduling values; do not upgrade chart version.
Changing args/annotations rolls controller pods and needs separate approval.
Verify CMC Prometheus discovers annotated controller pods and request series
arrive after real traffic; otherwise configure its scrape discovery explicitly.
Rollback: restore the prior values/revision via Devtron after review.
Reference: https://kubernetes.github.io/ingress-nginx/user-guide/monitoring/

## Direct ingress request scrape

CMC source Prometheus only discovers explicitly selected provider jobs; pod scrape
annotations alone are insufficient in this cluster. Notification Prometheus
therefore uses DNS A discovery against a headless ingress metrics Service. Each
controller pod is scraped separately so counter resets/load balancing do not
corrupt RPS. No Kubernetes API access/service account is needed. Keep only the
request counter for selected application namespaces. This counter is excluded
from federation to prevent counting it twice if the provider adds scraping later.

Apply the ingress overlay to the existing 4.15.1 release with current values
preserved. The newly created metrics Service must be headless (`clusterIP: None`)
and internal. Existing public HTTP/HTTPS Service and LoadBalancer are unchanged.
NetworkPolicy permits TCP 10254 only to ingress controller pods in ingress-nginx.
After sync, verify both ingress targets UP, initialize counters using a few safe
GET requests, and verify HcmIngressMetricsMissing inactive and RPS rule healthy.
Do not load-test production to exceed the alert threshold.

Rollback the scrape change via Git/ArgoCD and restore the previous ingress
release revision. Disabling metrics while keeping scrape enabled intentionally
triggers telemetry missing alerts.
