# Bật scaling bằng Helm thủ công

Không thay đổi pipeline, không bật auto-sync, không chạy upgrade từ máy local.
Chart vẫn dùng Kafka 15.3.4 / image hiện hành; không nâng version dependency.

| Workload | Cấu hình khi dùng manual-scaling.yaml |
|---|---|
| MQTT transport | HPA CPU 70%, 2–6 pod |
| ThingsBoard node | HPA CPU 70%, 2–4 pod |
| Kafka | HPA CPU 70%, 1–3 broker, chỉ scale UP; mỗi 120s tối đa thêm 1 |

Đây là ngưỡng khởi đầu cho demo, chưa đo/tune trên cluster. Min node=2 làm tăng node ngay cả khi chưa có tải. Với requests prod, mức tối đa của riêng ba nhóm khoảng 7 CPU / 14Gi RAM; còn cần dung lượng cho workload khác và headroom.

Kafka mới không tự nhận partition cũ; HPA tăng số broker không đồng nghĩa tự cân bằng throughput. Không bật scale-down tự động vì cần chuyển partition ra trước khi bỏ broker. Kafka/ZooKeeper prod hiện dùng emptyDir: restart vẫn có nguy cơ mất queue/metadata. File scaling không chuyển PVC hoặc đổi replication factor để tránh gộp migration dữ liệu vào một lần upgrade. Đây không phải cấu hình Kafka HA production hoàn chỉnh.

## 1. Trên bastion: lấy chart đã sửa và kiểm tra live

Chép repo đã cập nhật (gồm template kafka-hpa.yaml, values.yaml và environments/manual-scaling.yaml) sang bastion bằng cách hiện dùng. Không chỉ copy file override vào chart cũ vì chart cũ không có template HPA Kafka.

```bash
# Đứng tại thư mục repo trên bastion
export RELEASE=iot-thingsboard
export NS=thingsboard
export CHART="$PWD/helm/thingsboard"
export OVERRIDE="$CHART/environments/manual-scaling.yaml"
test -f "$CHART/templates/kafka-hpa.yaml" || exit 1

kubectl config current-context
helm list -n "$NS"
helm status "$RELEASE" -n "$NS"
helm history "$RELEASE" -n "$NS"
kubectl get hpa,sts,pods -n "$NS" -o wide
kubectl top nodes
kubectl top pods -n "$NS"
```

Tên release phải khớp `helm list`. Nếu release đang do một GitOps controller quản lý, xác nhận auto-sync đã tắt trên đúng application trước khi upgrade thủ công; không bật sync hoặc chạy pipeline cho bài này. Các lệnh ở đây không sửa cấu hình CI/CD.

Kiểm tra HPA hiện có, đảm bảo không có HPA tên khác cùng target. Kiểm tra metrics có số liệu, không phải `<unknown>`. Với repo hiện tại, resource requests đã có; nếu live khác, phải kiểm tra requests từng container.

## 2. Backup protected values và render

```bash
umask 077
export BACKUP="$HOME/tb-scaling-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
helm get values "$RELEASE" -n "$NS" --all -o yaml > "$BACKUP/values-before.yaml"
helm get manifest "$RELEASE" -n "$NS" > "$BACKUP/manifest-before.yaml"
helm history "$RELEASE" -n "$NS" -o json > "$BACKUP/history-before.json"
kubectl get hpa -n "$NS" -o yaml > "$BACKUP/hpa-before.yaml"
kubectl get sts -n "$NS" -o yaml > "$BACKUP/sts-before.yaml"

# Đổi biến này nếu Kafka StatefulSet dùng fullnameOverride trên live.
export KAFKA_STS="${RELEASE}-kafka"
export KAFKA_REPLICAS=$(kubectl get sts "$KAFKA_STS" -n "$NS" -o jsonpath='{.spec.replicas}')
test "$KAFKA_REPLICAS" -ge 1 || exit 1
export KAFKA_MAX=3
# Không đặt max thấp hơn số broker hiện có.
if [ "$KAFKA_REPLICAS" -gt "$KAFKA_MAX" ]; then KAFKA_MAX="$KAFKA_REPLICAS"; fi

helm lint "$CHART" \
  -f "$BACKUP/values-before.yaml" -f "$OVERRIDE" \
  --set kafka.replicaCount="$KAFKA_REPLICAS" \
  --set kafkaAutoscaling.minReplicas="$KAFKA_REPLICAS" \
  --set kafkaAutoscaling.maxReplicas="$KAFKA_MAX"

helm template "$RELEASE" "$CHART" -n "$NS" \
  -f "$BACKUP/values-before.yaml" -f "$OVERRIDE" \
  --set kafka.replicaCount="$KAFKA_REPLICAS" \
  --set kafkaAutoscaling.minReplicas="$KAFKA_REPLICAS" \
  --set kafkaAutoscaling.maxReplicas="$KAFKA_MAX" \
  > "$BACKUP/manifest-after.yaml"

# Xem riêng trên bastion: diff có thể chứa Secrets, không paste lên chat/Git.
diff -u "$BACKUP/manifest-before.yaml" "$BACKUP/manifest-after.yaml" \
  > "$BACKUP/manifest.diff" || test "$?" -eq 1
less "$BACKUP/manifest.diff"
```

Kiểm tra thay đổi chính là HPA node/MQTT/Kafka và node bỏ spec.replicas để HPA quản lý. **Không tiếp tục nếu Kafka/ZooKeeper pod template, volumes, config checksum, image hoặc secret đổi ngoài dự kiến**; local chart có thể khác chart đã cài. Dùng đúng baseline chart hoặc xử lý khác biệt trước, vì rolling restart Kafka emptyDir có thể mất dữ liệu.

Giữ file backup private, không commit. Không chạy `helm dependency update`; các tarball dependency đã có trong chart.

Lý do truyền `kafka.replicaCount` live: subchart 15.3.4 luôn render trường này, dù HPA đang quản lý. Mỗi lần upgrade về sau phải đọc lại số broker live và giữ nguyên, tránh Helm đưa về 1 broker. HPA scale-down disabled không ngăn Helm hoặc người vận hành giảm replica.

## 3. Upgrade thủ công

Chạy ngay sau khi kiểm tra diff. Nếu số broker live đổi trong lúc review, render/review lại với số mới trước.

```bash
test "$(kubectl get sts "$KAFKA_STS" -n "$NS" -o jsonpath='{.spec.replicas}')" = "$KAFKA_REPLICAS" || {
  echo "Kafka replicas changed; repeat render/review with the current count"
  exit 1
}

helm upgrade "$RELEASE" "$CHART" -n "$NS" \
  -f "$BACKUP/values-before.yaml" \
  -f "$OVERRIDE" \
  --set kafka.replicaCount="$KAFKA_REPLICAS" \
  --set kafkaAutoscaling.minReplicas="$KAFKA_REPLICAS" \
  --set kafkaAutoscaling.maxReplicas="$KAFKA_MAX" \
  --wait --timeout 20m
```

Không dùng `--install` để tránh tạo nhầm release. Không dùng `--force`. Không dùng `--atomic`: rollback tự động về revision cũ có thể giảm Kafka về số broker cũ sau khi HPA đã scale-up.

Lệnh dùng toàn bộ values đang cài làm nền để giữ endpoint DB/Redis, secret references và image đang sử dụng; override scaling là file cuối. Không dùng riêng prod/values.yaml thay toàn bộ cấu hình live.

## 4. Xác minh và test

```bash
kubectl get hpa -n "$NS"
kubectl describe hpa "${RELEASE}-node" -n "$NS"
kubectl describe hpa "${RELEASE}-mqtt-transport" -n "$NS"
kubectl describe hpa "$KAFKA_STS" -n "$NS"
kubectl rollout status "sts/${RELEASE}-node" -n "$NS" --timeout=15m
kubectl get pods -n "$NS" -o wide
kubectl get events -n "$NS" --sort-by=.lastTimestamp
kubectl get hpa -n "$NS" -w
```

Mở terminal khác:

```bash
watch -n 5 'kubectl get sts -n thingsboard; kubectl top pods -n thingsboard'
```

Chạy nhóm 150 thiết bị thêm trên simulator theo BASTION_DEMO_RUNBOOK.md trong 10 phút. Chỉ scale khi CPU vượt target đủ lâu; không đảm bảo cả ba HPA scale với 150 thiết bị. HPA Kafka tính trung bình CPU, nên broker mới idle có thể làm giảm metric trung bình dù broker cũ còn nóng. Scale-down MQTT/node có thể gây reconnect/rebalance; không cam kết zero impact với 50 thiết bị cũ.

Xác nhận cả node mới và node cũ xử lý API/telemetry, ZooKeeper discovery và Kafka consumer groups hoạt động. ThingsBoard 3.4 dùng queue cho cluster messaging; khai báo containerPort 9090 và policy 9001 tự nó không chứng minh một RPC listener đang tồn tại hoặc bị chặn. Không tự đổi RPC env/port dựa vào giả định cũ.

## 5. Khi Kafka có broker mới

Kiểm tra broker IDs và partition hiện tại, không tự đoán broker IDs từ số pod:

```bash
kubectl exec -n "$NS" "${KAFKA_STS}-0" -- \
  /opt/bitnami/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
kubectl exec -n "$NS" "${KAFKA_STS}-0" -- \
  /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe
```

Để broker mới xử lý partition cũ, dùng Kafka reassignment: chọn topic cụ thể, generate plan theo broker IDs thật, lưu current assignment, review proposed assignment rồi execute/verify với throttle phù hợp. Không tự động chạy reassignment tất cả topic hoặc tăng replication factor trong demo này. Tham khảo [Apache Kafka: replication tools](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/31819985/Replication+tools).

## 6. Dừng autoscaling / khôi phục

Dừng container demo trước. Không `helm rollback` mù hoặc giảm Kafka replicas: broker mới có thể đã giữ partition. Có thể vô hiệu HPA bằng một Helm upgrade mới nhưng **giữ số broker live**, không phải trả Kafka về 1.

```bash
# Chụp lại values và counts NGAY TRƯỚC lần upgrade dừng autoscaling.
helm get values "$RELEASE" -n "$NS" --all -o yaml > "$BACKUP/values-current.yaml"
KAFKA_NOW=$(kubectl get sts "$KAFKA_STS" -n "$NS" -o jsonpath='{.spec.replicas}')
NODE_NOW=$(kubectl get sts "${RELEASE}-node" -n "$NS" -o jsonpath='{.spec.replicas}')
MQTT_NOW=$(kubectl get sts "${RELEASE}-mqtt-transport" -n "$NS" -o jsonpath='{.spec.replicas}')

# Chỉ dừng 3 HPA, giữ số pod hiện tại; đây không phải rollback dữ liệu.
# Nếu đang có scale event, chờ ổn định và đọc lại counts trước khi chạy.
helm upgrade "$RELEASE" "$CHART" -n "$NS" \
  -f "$BACKUP/values-current.yaml" \
  --set kafkaAutoscaling.enabled=false --set kafka.replicaCount="$KAFKA_NOW" \
  --set node.autoscaling.enabled=false --set node.replicaCount="$NODE_NOW" \
  --set mqtt.autoscaling.enabled=false --set mqtt.replicaCount="$MQTT_NOW" \
  --wait --timeout 20m
```

Muốn giảm Kafka về số broker ban đầu cần một thao tác bảo trì riêng: evacuate partition, xác minh ISR/replication và dữ liệu, rồi mới giảm replicas. Không xóa pod/volume Kafka để “cleanup test”.
