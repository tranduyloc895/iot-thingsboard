# Observability Stack (Grafana + Loki S3 + Promtail + CMC Prometheus)

Stack giám sát và lưu vết log tập trung cho dự án **HCM Flood Warning IoT** trên nền tảng **CMC Cloud Kubernetes (CKE)**.

## 1. Thành phần
- **Grafana (v11.2.0)**: Giao diện trực quan hóa, ghim tại `System NodeGroup` (`cmccloud-k8s-nodegroups: system`), ingress tại `grafana.flood.web-ui.com`.
- **Loki Single-Binary (v2.9.8)**: Gom log, nén chunks và đẩy thẳng lên **CMC S3 Object Storage**, ghim tại `System NodeGroup`.
- **Promtail (v2.9.8)**: DaemonSet chạy trên các nodes, tự động gắn nhãn Kubernetes metadata (`namespace`, `pod`, `node`, `container`).
- **CMC Prometheus Integration**: Tự động kết nối tới `http://prometheus-server.cmc-monitoring:80`.

## 2. Quản lý Secret S3 (Access Key & Secret Key)

### Cách 1: Khai báo qua `values.yaml`
Trong `values.yaml`:
```yaml
loki:
  s3:
    enabled: true
    endpoint: "https://s3.cmccloud.vn"   # Thay bằng endpoint S3 của CMC
    bucket: "hcm-flood-logs"              # Tên bucket S3
    region: "hcm-1"
    secret:
      create: true
      name: "cmc-s3-secret"
      accessKey: "<CMC_S3_ACCESS_KEY>"
      secretKey: "<CMC_S3_SECRET_KEY>"
```

### Cách 2: Tạo Secret thủ công trước (Bảo mật tối đa)
Chạy lệnh trực tiếp trên bastion:
```bash
kubectl create secret generic cmc-s3-secret \
  -n cmc-monitoring \
  --from-literal=access-key="<CMC_S3_ACCESS_KEY>" \
  --from-literal=secret-key="<CMC_S3_SECRET_KEY>"
```
Và trong `values.yaml` đặt `loki.s3.secret.create: false` và `loki.s3.secret.name: "cmc-s3-secret"`.

## 3. Triển khai qua Devtron (GitOps)
1. Commit thư mục `helm/observability` lên GitHub repo.
2. Trên Devtron UI:
   - Vào **Applications** -> **Create Custom App** hoặc **Create Helm App**.
   - Tên App: `hcm-flood-observability`
   - Project: `default`
   - Target Namespace: `cmc-monitoring` (hoặc `monitoring`)
   - Git Repository: Chọn repo hiện tại, đường dẫn chart: `helm/observability`.
3. Bấm **Deploy**.
