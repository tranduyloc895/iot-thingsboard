# Demo NetworkPolicy, isolated MQTT fleet, ThingsBoard HPA

Các lệnh dưới đây dùng **Bash trên Linux**, không phải PowerShell. Bastion cần kubeconfig; máy simulator cần Docker. Chưa chạy trên cluster thật. Kiểm tra tên live trước khi dùng các tên từ repo.

## 0. Những điểm khác kế hoạch cũ

- 50 thiết bị hiện tại + 100 mới = 150; +150 mới = 200; +250 mới = 300.
- `single_device_simulator.py` chỉ nhận NODE_INDEX 0..49. Không scale service cũ, không dùng lại token hoặc client ID của 50 thiết bị.
- Script trong kế hoạch dùng `DEV_SURGE_TOKEN_*` chưa được provision, chưa chờ CONNACK, chưa kiểm tra `is_published()` và barrier có thể treo. Dùng `demo_surge.py` đi kèm tài liệu này.
- Script mới dùng provisioning helper sẵn có, tên `DEMO-SURGE-001..`, volume riêng, không gửi station_id/đo đạc ngập giả vào 50 station thật. Nên dùng Device Profile test riêng, cho phép tạo thiết bị mới. Rule chain/profile vẫn cần xử lý telemetry nếu muốn đo toàn bộ luồng. Dữ liệu test được lưu thật trong ThingsBoard.
- Chỉ nhóm mới gửi đồng bộ từng đợt; 50 thiết bị cũ vẫn gửi theo chu kỳ 3–5 giây. Tổng 200 online không có nghĩa 200 gửi đồng thời. Muốn 200/300 thiết bị đồng bộ mà giữ nguyên 50 cũ, chạy thêm 200/300 (tổng 250/350).
- Prod values: MQTT HPA bật (2–6, CPU 70%, request 250m); node HPA tắt. Web UI HPA bật (2–4, CPU 75%). MQTT không tạo tải đáng kể cho Web UI.
- Dừng container demo không dừng fleet cũ. Tuy nhiên hai nhóm dùng chung ThingsBoard/Kafka/DB; quá tải hoặc HPA scale-down vẫn có thể ảnh hưởng kết nối cũ. Không thể cam kết hoàn toàn không ảnh hưởng dịch vụ khi stress test.

## 1. NetworkPolicy — chạy trên bastion

### Kiểm tra trước

```bash
kubectl config current-context
kubectl get pods,svc,networkpolicy -n flood-portal -o wide
kubectl get pods,svc,networkpolicy,hpa -n thingsboard -o wide
kubectl get networkpolicy -n flood-portal -o yaml
kubectl get networkpolicy -n thingsboard -o yaml
kubectl get endpointslices -n flood-portal
kubectl get endpointslices -n thingsboard

FE_POD=$(kubectl get pods -n flood-portal -l app.kubernetes.io/name=hcm-flood-frontend --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
BE_POD=$(kubectl get pods -n flood-portal -l app.kubernetes.io/name=hcm-flood-backend --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
BE_IP=$(kubectl get pod -n flood-portal "$BE_POD" -o jsonpath='{.status.podIP}')
TB_IP=$(kubectl get pod -n thingsboard iot-thingsboard-node-0 -o jsonpath='{.status.podIP}')
MQTT_IP=$(kubectl get svc -n thingsboard iot-thingsboard-mqtt -o jsonpath='{.spec.clusterIP}')
printf 'FE=%s BE=%s BE_IP=%s TB_IP=%s MQTT_IP=%s\n' "$FE_POD" "$BE_POD" "$BE_IP" "$TB_IP" "$MQTT_IP"
```

Đổi tên workload/service nếu live khác repo. Phải có Pod Ready và endpoints trước khi đánh giá timeout. Kiểm tra cả policy cấp cluster của Calico nếu có; timeout đơn lẻ không chứng minh chính xác policy nào chặn.

### Các luồng được phép

```bash
# Frontend -> backend: kỳ vọng JSON health, exit 0
kubectl exec -n flood-portal "$FE_POD" -- wget -qO- -T 5 http://hcm-flood-backend:8000/healthz

# Backend -> ThingsBoard: kỳ vọng HTTP 200 hoặc phản hồi HTTP hợp lệ.
# 401/404 cũng chứng minh đã tới HTTP server, nhưng không đạt kiểm tra endpoint 200.
kubectl exec -n flood-portal "$BE_POD" -- python -c "import urllib.request; print(urllib.request.urlopen('http://iot-thingsboard-node.thingsboard.svc.cluster.local:8080/login', timeout=5).status)"

# Backend -> API ngoài qua HTTPS: kỳ vọng HTTP 200
kubectl exec -n flood-portal "$BE_POD" -- python -c "import urllib.request; print(urllib.request.urlopen('https://api.open-meteo.com/v1/forecast?latitude=10.8&longitude=106.7&current=temperature_2m', timeout=10).status)"
```

Nếu wget thiếu trong FE, không cài package vào container đang chạy; dùng image debug đã được cluster cho phép với nhãn nguồn tương ứng và kiểm tra policy chọn nguồn đó.

### Tạo một pod kiểm tra riêng, không mang nhãn ứng dụng

```bash
kubectl apply -f - <<'YAML'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: demo-netcheck
  namespace: flood-portal
automountServiceAccountToken: false
---
apiVersion: v1
kind: Pod
metadata:
  name: demo-netcheck
  namespace: flood-portal
  labels:
    app: demo-netcheck
spec:
  serviceAccountName: demo-netcheck
  automountServiceAccountToken: false
  restartPolicy: Never
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: probe
      image: python:3.11-slim
      command: ["python", "-c", "import time; time.sleep(3600)"]
      resources:
        requests: {cpu: 10m, memory: 32Mi}
        limits: {cpu: 100m, memory: 64Mi}
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
YAML
kubectl wait -n flood-portal --for=condition=Ready pod/demo-netcheck --timeout=120s
```

Pod chẩn đoán ngắn hạn, không phải service production. Nếu admission từ chối image, dùng registry mirror đã được duyệt. Không đổi policy để ép test thành công.

### Test TCP trực tiếp: loại trừ lỗi DNS

```bash
# In OPEN / TIMEOUT / REFUSED / ERROR; không đánh đồng mọi lỗi với PASS.
tcp_probe() {
  kubectl exec -i -n "$1" "$2" -- python - "$3" "$4" <<'PY'
import socket, sys
host, port = sys.argv[1], int(sys.argv[2])
try:
    with socket.create_connection((host, port), timeout=5):
        print(f'OPEN {host}:{port}')
except socket.timeout:
    print(f'TIMEOUT {host}:{port}')
except ConnectionRefusedError:
    print(f'REFUSED {host}:{port} — check listener/endpoints')
except OSError as exc:
    print(f'ERROR {host}:{port}: {exc}')
PY
}

```

Positive control cùng đích, cùng port. FE dùng wget vì image NGINX thường không có Python:

```bash
kubectl exec -n flood-portal "$FE_POD" -- wget -qO- -T 5 "http://$BE_IP:8000/healthz"
tcp_probe flood-portal "$BE_POD" "$TB_IP" 8080

# Negative ingress: pod lạ -> backend, TB; kỳ vọng TIMEOUT
tcp_probe flood-portal demo-netcheck "$BE_IP" 8000
tcp_probe flood-portal demo-netcheck "$TB_IP" 8080

# Positive control MQTT: kỳ vọng OPEN; service 8883 -> container 8081,
# ssl.enabled=false trong repo, số port 8883 ở đây không hàm ý TLS.
tcp_probe flood-portal demo-netcheck "$MQTT_IP" 8883

# Negative egress từ backend -> cùng đích MQTT: kỳ vọng TIMEOUT.
# Ingress MQTT cho phép mọi nguồn tại port đích 8081;
# backend egress chỉ cho TB core 8080, DNS và public HTTPS.
tcp_probe flood-portal "$BE_POD" "$MQTT_IP" 8883

# Negative bổ sung trong kế hoạch: backend -> Kafka
KAFKA_IP=$(kubectl get svc -n thingsboard iot-thingsboard-kafka -o jsonpath='{.spec.clusterIP}')
tcp_probe flood-portal demo-netcheck "$KAFKA_IP" 9092
tcp_probe flood-portal "$BE_POD" "$KAFKA_IP" 9092
```

PASS cho cặp test khi nguồn hợp lệ OPEN, nguồn bị cấm TIMEOUT và policy live đúng selector. Nếu cả hai timeout: chưa kết luận; kiểm tra endpoints, routing, Calico và các policy khác. Với Kafka, nếu positive control cũng bị policy chặn thì dùng cặp MQTT để chứng minh backend egress. NetworkPolicy có tính cộng dồn; cả ingress đích và egress nguồn đều phải cho phép kết nối. [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/).

```bash
# Cleanup đúng 2 resource demo
kubectl delete pod/demo-netcheck serviceaccount/demo-netcheck -n flood-portal
```

## 2. Thêm 150 thiết bị trên máy simulator, tách khỏi 50 cũ

Từ bastion SSH vào host simulator bằng user/IP thực tế:

```bash
ssh USER@SIMULATOR_IP
# cd vào thư mục simulator của bản repo đã chứa demo_surge.py và Dockerfile.demo
cd /YOUR/REPO/thingsboard-ce-k8s/simulator

# Ghi baseline container đang chạy
docker ps --format '{{.ID}} {{.Names}} {{.Status}}'
docker build -f Dockerfile.demo -t tb-demo-surge:local .
docker volume create tb-demo-surge-state

export THINGSBOARD_HOST=10.0.1.200
export PORT=1883
# Đây là endpoint từ README của simulator; xác minh route/firewall thực tế.
# Không dùng *.svc.cluster.local trên máy simulator bên ngoài Kubernetes.
read -r -s -p 'Provision key của profile test: ' PROVISION_KEY; echo
read -r -s -p 'Provision secret của profile test: ' PROVISION_SECRET; echo
export PROVISION_KEY PROVISION_SECRET

# Chuẩn bị devices/token trước, chưa gửi telemetry. Chạy một lần;
# lần sau giữ nguyên volume để dùng lại token.
docker run --rm --name tb-demo-prepare \
  -e THINGSBOARD_HOST -e PORT -e PROVISION_KEY -e PROVISION_SECRET \
  -v tb-demo-surge-state:/demo-state \
  tb-demo-surge:local --prepare --devices 150
unset PROVISION_KEY PROVISION_SECRET
```

Phải có đủ 150 dòng `PREPARED ... CONNACK OK`. Provisioning thất bại thì xử lý credentials/profile trước; không xóa volume để retry mù. Nếu đã tạo thiết bị mà mất response/token, khôi phục credentials đúng từ ThingsBoard. Không chạy hai bản demo cùng lúc vì chúng dùng chung `DEMO-SURGE-*` client ID.

**Demo burst: 150 thiết bị mới gửi cùng mỗi đợt, 5 đợt, khoảng cách tối thiểu 1 giây.**

```bash
docker run -d --name tb-demo-surge \
  -e THINGSBOARD_HOST -e PORT \
  -v tb-demo-surge-state:/demo-state \
  tb-demo-surge:local --devices 150 --cycles 5 --interval 1
docker logs -f tb-demo-surge
docker inspect -f 'exit={{.State.ExitCode}} status={{.State.Status}}' tb-demo-surge
```

Kỳ vọng `READY 150 clients`, `Planned=750 PUBACK=750 unconfirmed_or_unsent=0`, exit=0. Barrier đồng bộ mỗi đợt sau khi mọi client đã có CONNACK; thread scheduling/network vẫn tạo độ lệch nhỏ, không phải đồng thời tuyệt đối. Nếu một client lỗi thì dừng cả bài test, không treo barrier vô hạn. PUBACK chỉ xác nhận tầng MQTT, **không chứng minh dữ liệu đã lưu PostgreSQL**.

Trong ThingsBoard, tìm `DEMO-SURGE-001`, `DEMO-SURGE-075`, `DEMO-SURGE-150`, xem Latest telemetry `demo_seq=4`, `source=load-test` và timestamp mới. Muốn chứng minh không thiếu bản tin end-to-end phải đối soát timeseries từng thiết bị và từng `demo_seq`, không chỉ lấy Latest telemetry. Tiêu chí kế hoạch: PUBACK >=99%, p95 <500ms, p99 <1500ms; kết quả 150 client không thay thế phép đo 300 client.

**Dừng/xóa đúng container mới:**

```bash
docker stop -t 30 tb-demo-surge
docker logs --tail 20 tb-demo-surge
docker rm tb-demo-surge
docker ps --format '{{.ID}} {{.Names}} {{.Status}}'
```

Giữ volume `tb-demo-surge-state` cho lần sau. Không dùng `docker compose down`, `docker stop $(docker ps -q)` hoặc xóa volume của fleet 50. Các device demo vẫn tồn tại trong ThingsBoard nhưng ngừng gửi; không tự động xóa device.

Muốn thêm 100: đổi `--devices 150` thành `100` ở cả prepare/run. Muốn tổng 300: prepare/run 250. Chuẩn bị thêm trước khi chạy; không sửa `generate_compose.py` hoặc fleet cũ.

## 3. HPA ThingsBoard — dùng tải MQTT, quan sát ở bastion

### Xác nhận HPA live trước

```bash
kubectl get hpa -n thingsboard -o wide
kubectl get hpa -n thingsboard -o custom-columns='NAME:.metadata.name,KIND:.spec.scaleTargetRef.kind,TARGET:.spec.scaleTargetRef.name,MIN:.spec.minReplicas,MAX:.spec.maxReplicas'
kubectl describe hpa -n thingsboard iot-thingsboard-mqtt-transport
kubectl get sts -n thingsboard iot-thingsboard-mqtt-transport -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{" requests="}{.resources.requests}{" limits="}{.resources.limits}{"\n"}{end}'
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl top nodes
kubectl top pods -n thingsboard
kubectl get pods -n thingsboard -o wide
```

`TARGETS <unknown>` hoặc `ScalingActive=False`: sửa metrics-server/CPU requests trước. Nếu HPA MQTT chưa có trên live, bật `mqtt.autoscaling.enabled: true`, min=2, max=6, CPU=70 qua values của release/GitOps hiện hành rồi sync; không tạo HPA thứ hai cùng target. Cần tài nguyên cho pod mới; Pending do thiếu CPU/RAM không phải lỗi thuật toán HPA.

HPA CPU tính theo **requests**, không phải limits. Với request 250m và target 70%, ngưỡng tương ứng khoảng **175m CPU trung bình/pod**. Scale-down mặc định có cửa sổ ổn định 300 giây; values/controller live có thể thay đổi. [Kubernetes HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).

### Tải kéo dài trên máy simulator

Chỉ chạy sau khi container burst đã dừng và được `docker rm`. Bắt đầu 1 giây/đợt (~150 msg/s), giữ khoảng 10 phút. Thời gian thực tế dài hơn nếu PUBACK chậm.

```bash
docker run -d --name tb-demo-surge \
  -e THINGSBOARD_HOST -e PORT \
  -v tb-demo-surge-state:/demo-state \
  tb-demo-surge:local --devices 150 --cycles 600 --interval 1
docker logs -f tb-demo-surge
```

Nếu CPU vẫn dưới ngưỡng và hệ thống ổn định, dừng/xóa container demo rồi chạy lại với `--cycles 1200 --interval 0.5` (~300 msg/s) hoặc `--cycles 3000 --interval 0.2` (~750 msg/s). Đây là tải mục tiêu; PUBACK chậm sẽ giảm throughput. Theo dõi cả CPU máy simulator (`docker stats tb-demo-surge`), tránh nhầm giới hạn máy phát tải với giới hạn ThingsBoard.

### Ba terminal trên bastion

```bash
# Terminal 1: HPA desired/current replicas
kubectl get hpa -n thingsboard -w
```

```bash
# Terminal 2: pod thực tế + CPU
watch -n 5 'kubectl get sts -n thingsboard; kubectl get pods -n thingsboard; kubectl top pods -n thingsboard'
```

```bash
# Terminal 3: bằng chứng scale / lỗi tài nguyên
kubectl get events -n thingsboard --sort-by=.lastTimestamp
kubectl describe hpa -n thingsboard iot-thingsboard-mqtt-transport
kubectl logs -n thingsboard iot-thingsboard-mqtt-transport-0 --since=10m --tail=100
kubectl logs -n thingsboard iot-thingsboard-node-0 --since=10m --tail=100

# Kafka: lấy group thật trước, không giả định tb-node-consumer-group tồn tại.
kubectl exec -n thingsboard iot-thingsboard-kafka-0 -- \
  /opt/bitnami/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
# Thay GROUP_THUC_TE bằng group vừa tìm được; có auth thì dùng client config hiện hành.
kubectl exec -n thingsboard iot-thingsboard-kafka-0 -- \
  /opt/bitnami/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group GROUP_THUC_TE
```

MQTT là kết nối dài: pod mới không tự nhận lại kết nối đang nằm trên pod cũ. Sau scale-up, có thể stop/rm và chạy lại **container demo** để nhóm demo kết nối lại qua LB. Không restart 50 container cũ; phân phối qua LB không được đảm bảo đều tuyệt đối.

### Kết thúc và tiêu chí

1. HPA ghi nhận CPU vượt target kéo dài và tăng desired replicas; có `SuccessfulRescale`.
2. StatefulSet tạo pod mới và pod đạt Ready; không tăng restart/OOM/DB timeout; xác nhận telemetry đến ThingsBoard.
3. Trên simulator: `docker stop -t 30 tb-demo-surge` rồi `docker rm tb-demo-surge`.
4. Quan sát 5–10 phút hoặc lâu hơn theo policy live. Replicas giảm khi CPU/tải nền cho phép; 50 thiết bị cũ vẫn đang tạo tải nên không bắt buộc trở về min ngay.
5. Xác nhận timestamp 50 station gốc tiếp tục cập nhật và container ID/start time không đổi. CPU chưa vượt target thì **chưa kích hoạt điều kiện scale**, không kết luận HPA hỏng. Một burst 5 giây thường không đủ kiểm chứng HPA.

Nếu chỉ cần minh họa thuật toán khi tải nhỏ, có thể hạ CPU target tạm qua GitOps sau khi ghi giá trị ban đầu; đó là demo ngưỡng nhân tạo, phải khôi phục sau test, không dùng làm kết luận năng lực tải. Không cần CPU busy-loop trong pod ThingsBoard đang phục vụ.

### Riêng `tb-node`

Prod values mặc định đang tắt node HPA; không kỳ vọng node tự scale dù MQTT HPA scale. File override `helm/thingsboard/environments/manual-scaling.yaml` bổ sung bật node HPA cho upgrade Helm thủ công; xem [HELM_MANUAL_SCALING.md](HELM_MANUAL_SCALING.md). Không dùng CI/CD auto-sync cho quy trình này.

Đính chính nhận định trước: ThingsBoard 3.4 dùng queue cho cluster messaging. `node.port.rpc=9090` trong values và 9001 trong NetworkPolicy chưa đủ để kết luận multi-node bị chặn; khai báo containerPort không chứng minh ứng dụng có listener tương ứng. Không tự sửa port theo giả định. Sau upgrade, xác minh node Ready, ZooKeeper discovery, Kafka consumers và telemetry/API trên các node.
