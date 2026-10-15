# Discord: CI, scaling và cảnh báo tài nguyên

## Hai kênh và hai webhook

Tạo hai text channel riêng, ví dụ `#ci-pipeline` và `#infra-alerts`. Trong từng
channel: **Edit Channel → Integrations → Webhooks → New Webhook → Copy Webhook URL**.
Không commit URL vào Git, Helm values, report hay log. Webhook là credential.

### Kênh CI

Trong GitHub repository → **Settings → Secrets and variables → Actions → New
repository secret**, tạo **`DISCORD_CI_WEBHOOK_URL`** với webhook của `#ci-pipeline`.

Backend CI, Frontend CI và standalone Security scans có bước cuối `if: always()`
để gửi PASS/FAIL/CANCELLED, commit, branch, run/attempt, bước lỗi, tóm tắt security,
link Actions/artifact và **ZIP chứa đúng cặp HTML/JSON đã redacted**. Demo CI có
thể PASS nhưng security FAIL; tin nhắn hiển thị cả hai, không đổi kết quả scan.

Nếu report chưa sinh hoặc ZIP quá 7 MiB, gửi trạng thái và link artifact thay vì
file. Không gửi raw scanner logs/source snippets/secret matches. Giới hạn retry
khi gặp HTTP 429/5xx; không in URL webhook khi lỗi. `allowed_mentions` tắt ping
ngoài ý muốn. Lỗi gửi Discord chỉ ghi warning, không làm đổi kết quả build/deploy.
Nếu chưa có Secret, step ghi notice và bỏ qua. PR workflow không dùng webhook;
các lượt push dev/main, manual/schedule thích hợp mới gửi. Không thể bảo đảm gửi
sau runner crash, checkout thất bại hoặc hard cancellation.

Kiểm tra: push thay đổi FE/BE lên dev hoặc chạy workflow thủ công, xem step
`Notify Discord with outcome and report`, tin nhắn trong channel và ZIP đính kèm.
Không cần thêm artifact lên GitHub; mỗi pipeline vẫn chỉ upload một artifact.

### Kênh hạ tầng

Tạo Kubernetes Secret **`discord-infra-webhook`**, key **`webhook-url`**, trong
**cùng namespace với observability release** (ví dụ `cmc-monitoring`). Tạo qua
secret manager/Devtron Secret UI. Nếu dùng CLI, đọc URL từ một file bảo mật ngoài
repository để không đưa token vào shell history:

```sh
kubectl --context "$CMC_CONTEXT" -n cmc-monitoring create secret generic discord-infra-webhook \
  --from-file=webhook-url=/secure/discord-infra-webhook.txt
```

File chỉ chứa URL, không thêm dấu nháy. Giới hạn quyền đọc và loại bỏ file tạm
sau khi nạp vào secret manager. Đây là lệnh mẫu, chưa được chạy tự động.

## Luồng metrics → Alertmanager → Discord

Repo có Prometheus CMC ở `prometheus-server.cmc-monitoring:80` nhưng chưa có
alerting do dự án quản lý. Chart observability bổ sung hai workload tùy chọn:

1. **Notification Prometheus** chỉ federation các metric cần thiết từ Prometheus
   CMC qua `/federate`; không cài lại exporter, không sửa Prometheus của provider.
2. **Alertmanager** nhóm/deduplicate alert và dùng native `discord_configs`, đọc
   webhook từ Secret file. Alert tài nguyên gửi cả FIRING/RESOLVED; scaling chỉ
   gửi thông tin thay đổi, không gửi thêm tin resolved.

`notifications.enabled` mặc định **false**, vì phải tạo Secret và xác nhận nguồn
metric trước. Bật bằng overlay `helm/observability/environments/discord.values.yaml`
trên **observability app/release hiện có**, giữ nguyên toàn bộ values đang dùng
cho Loki/S3/Grafana. Không cài release mới chồng lên tài nguyên cùng tên.

Hai Deployment dùng image version+digest cố định, non-root, filesystem read-only,
không mount service account token, có probes/resources và NetworkPolicy. PVC
mặc định: Prometheus 5 GiB, Alertmanager 1 GiB; không public ingress. Cần default
StorageClass hoặc cấu hình `notifications.<component>.persistence.storageClass`.
Giữ PVC khi disable/uninstall để giữ dữ liệu/silence; chỉ xóa riêng khi đã xác
nhận không cần. `Recreate` tránh xung đột RWO volume, nhưng có khoảng trống giám
sát khi restart; đây là cấu hình một replica, không phải HA.

## Metric cần có ở CMC Prometheus

- Node exporter: `node_cpu_seconds_total`, `node_memory_MemAvailable_bytes`,
  `node_memory_MemTotal_bytes`.
- kube-state-metrics: `kube_node_info`,
  `kube_horizontalpodautoscaler_status_current_replicas`,
  `kube_pod_container_resource_requests`, `kube_pod_container_resource_limits`.
- Kubelet/cAdvisor: `container_cpu_usage_seconds_total`,
  `container_memory_working_set_bytes`.
- Ingress-nginx: `nginx_ingress_controller_requests`, có label namespace/ingress.
  Cần bật `controller.metrics.enabled` và cấu hình CMC Prometheus scrape controller.
  Nếu ingress khác, thay metric/query tương ứng. Không có metric không được xem
  là RPS bằng 0; rule telemetry sẽ thông báo dữ liệu thiếu.

Provider cần cho phép `/federate` và truy cập từ notification Prometheus. Mặc định
chỉ lấy pod/HPA/ingress metrics trong `iot-dev|iot-prod`; node metrics là toàn
cluster CMC nguồn. Sửa namespace regex/cluster label nếu thực tế khác. Nếu nguồn
có authentication/TLS riêng, phải cấu hình scrape authentication/CA phù hợp trước
khi bật; không tắt kiểm tra TLS để bỏ qua lỗi. Node metrics được gắn nhãn theo
`instance` của exporter; không mặc định đó là tên cloud instance.

NetworkPolicy cho phép DNS kube-system, Prometheus nguồn namespace cmc-monitoring
trên TCP 80/9090, Alertmanager nội bộ và HTTPS ra Internet để gửi Discord. Nếu
dùng NodeLocal DNS, proxy hoặc endpoint/port khác, phải điều chỉnh policy cho môi
trường. Standard NetworkPolicy không whitelist Discord theo FQDN; HTTPS egress
được giới hạn bằng port và loại các CIDR private/link-local.

## Các ngưỡng ban đầu

| Alert | Điều kiện mặc định | Chờ |
| --- | --- | --- |
| Node CPU | >80% utilization | 5 phút |
| Node memory | >85% used (tính từ available) | 5 phút |
| Pod CPU / requests | >100% tổng CPU requests | 5 phút |
| Pod memory / requests | >100% tổng memory requests | 5 phút |
| Container memory / limit | Bất kỳ container có limit vượt 90% | 5 phút |
| HTTP RPS | >100 request/giây mỗi ingress/namespace, rate trung bình 5 phút | 5 phút |
| HPA scale | Current replica gauge thay đổi trong cửa sổ 5 phút | Một lần sau đánh giá |
| Node scale | Tổng số node quan sát được thay đổi trong cửa sổ 5 phút | Một lần sau đánh giá |

Đây là ngưỡng khởi đầu để hiệu chỉnh theo tải, không phải khẳng định capacity
production. Sửa tại `notifications.thresholds` trong Helm values. CPU/memory
requests là mức reservation để scheduling, vượt requests không đồng nghĩa vượt
hard limit. Requests/limits bằng 0 hoặc thiếu không được chia thành infinity.
CPU/RPS dùng rate 5 phút rồi mới đếm thời gian duy trì 5 phút; khi evaluator mới
khởi động có thể cần gần 10 phút để đủ dữ liệu và bắt đầu firing.

Scale dùng metric chứ không phải audit event stream: không bảo đảm một tin cho
từng lần scale liên tiếp, có thể gộp thay đổi trong 5 phút; scrape interval mặc
định 30 giây. Tin ghi số replica/node hiện tại, không suy đoán tác nhân autoscaler
hay thao tác tay, không đo lại hoạt động đã xảy ra trước khi evaluator có dữ liệu.
Node replacement giữ nguyên tổng số node không phải sự kiện thay đổi capacity.
Theo dõi actual node count không chứng minh VM/node group cloud đã resize hoàn
tất. Alert tài nguyên repeat 4h; scaling không lặp trong cùng cửa sổ 5 phút.

Rule kiểm tra nguồn federation down và thiếu node/pod/ingress metrics giúp phát
hiện blind spot. Không dựa vào chính Discord làm kênh duy nhất để phát hiện lỗi
gửi Discord; cần kiểm tra Alertmanager logs/metrics hoặc một kênh ngoài dự phòng.

## Render, kiểm tra và triển khai

Kiểm thử offline từ repository root (cần Python + PyYAML, Helm, promtool 3.15.0,
amtool 0.34.1 trên PATH; script không deploy và không gửi Discord):

```sh
python -m unittest discover -s .github/notifications -p 'test_*.py' -v
python tools/validate_discord_alerts.py
```

Rule fixtures kiểm tra HPA scale và trở lại ổn định, node count change, CPU request
ratio có duplicate scrape, thời gian `for` và requests bằng 0. Kiểm tra receiver
bằng `amtool check-config` dùng URL giả; không xác nhận delivery đến channel thật.

1. Xác nhận đúng context/cluster CMC và release/namespace trong Devtron.
   Context trên máy khi thực hiện yêu cầu này đang là **ecommerce-cluster**, không
   phải bằng chứng truy cập cluster CMC; không áp dụng vào context đó.
2. Kiểm tra các metric trên CMC Prometheus UI/API, `/federate` và Secret đã tồn tại.
3. Render và review diff cùng **values hiện tại** của release:

```sh
helm lint helm/observability -f helm/observability/environments/discord.values.yaml
helm template <existing-release> helm/observability -n <namespace> \
  -f <current-values.yaml> -f helm/observability/environments/discord.values.yaml
```

4. Nâng cấp observability app qua Devtron sau khi review, giữ app overrides hiện
   có. Không tự đổi source/values của dev/prod application trong bước này.
5. Chờ hai pod Ready; mở notification Prometheus qua port-forward hoặc Devtron,
   xem Targets → federation UP, query metric có dữ liệu và Rules không có lỗi.
6. Test receiver bằng một alert tổng hợp qua `/api/v2/alerts` của Alertmanager
   bằng port-forward nội bộ, với labels `cluster=hcm-flood-cmc`, `severity=info`,
   `alertname=DiscordSetupTest`, annotations summary/description và endsAt ngắn.
   Đây chỉ test đường gửi, không test query CPU/HPA.
7. Ở **dev**, thử scale/test tải có kiểm soát, xác nhận cảnh báo và resolved.
   Không scale production chỉ để thử thông báo.

Rollback: bỏ overlay hoặc đặt `notifications.enabled=false` trên release hiện
có và review/apply qua Devtron. Chỉ gỡ hai workload/rules/service/policy mới,
giữ PVC và các thành phần observability cũ. Tắt CI bằng cách xóa Secret webhook;
CI tiếp tục bình thường. Rotate webhook ở Discord rồi cập nhật secret khi cần;
restart Alertmanager sau rotate để kiểm chứng mount/receiver được cập nhật.

Tham khảo chính thức: [Prometheus federation](https://prometheus.io/docs/prometheus/latest/federation/),
[Alertmanager Discord receiver](https://prometheus.io/docs/alerting/latest/configuration/#discord_config),
[ingress-nginx metrics](https://kubernetes.github.io/ingress-nginx/user-guide/monitoring/).
