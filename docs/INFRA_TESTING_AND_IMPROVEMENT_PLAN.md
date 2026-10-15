# KẾ HOẠCH KIỂM THỬ HẠ TẦNG VÀ ĐỀ XUẤT CẢI TIẾN
## HỆ THỐNG CẢNH BÁO NGẬP VÀ THỜI TIẾT TP.HCM (CMC CLOUD KUBERNETES)

---

## 1. TỔNG QUAN HIỂU BIẾT VỀ DỰ ÁN (Architecture, Components & Flows)

### 1.1 Mục Tiêu & Bản Chất Dự Án
- **Tên dự án:** Hệ thống quan trắc, cảnh báo ngập lụt và thời tiết TP.HCM.
- **Mục tiêu hạ tầng:** Vận hành ổn định nền tảng IoT ThingsBoard CE cùng ứng dụng Cổng thông tin Cảnh báo ngập trên CMC Kubernetes Engine (CKE) với tính sẵn sàng cao, bảo mật phân vùng mạng theo nguyên tắc đặc quyền tối thiểu (Least Privilege), và tự động hóa qua GitOps (Devtron / ArgoCD).
- **Môi trường mục tiêu:** CMC Cloud (OpenStack based), VPC `10.0.0.0/16`, Calico CNI v3.31.0, Cinder CSI storage, CMC DBaaS (PostgreSQL & Redis), CMC S3 Object Storage.

### 1.2 Bản Đồ Thành Phần (Workloads & Services)
Hệ thống được chia thành 3 phân vùng logic chính:

| Phân vùng | Namespace | Thành phần (Workload) | Loại Workload & Replicas | Cổng / Giao thức | Vai trò chức năng | Bằng chứng mã nguồn / cấu hình |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IoT Platform** | `thingsboard` | `tb-mqtt-transport` | StatefulSet (2) | TCP 1883, 8081 | Tiếp nhận telemetry MQTT từ cảm biến | [helm/thingsboard/templates/mqtt-transport.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/templates/mqtt-transport.yaml) |
| | | `tb-http-transport` | StatefulSet (2) | TCP 8082 | Tiếp nhận telemetry HTTP | [helm/thingsboard/templates/http-transport.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/templates/http-transport.yaml) |
| | | `tb-coap-transport` | StatefulSet (1) | UDP 8083 | Tiếp nhận telemetry CoAP | [helm/thingsboard/templates/coap-transport.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/templates/coap-transport.yaml) |
| | | `tb-node` | StatefulSet (1) | TCP 8080 (HTTP), 9001 (RPC) | Core monolith ThingsBoard: Rule Engine, Akka actors, REST/WebSocket API | [helm/thingsboard/templates/node.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/templates/node.yaml) |
| | | `tb-js-executor` | Deployment (2) | Microservice queue-based | Sandbox chạy JavaScript Rule Chains | [helm/thingsboard/templates/js-executor.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/templates/js-executor.yaml) |
| | | `tb-web-ui` | Deployment (2) | TCP 8084 | Dashboard quản trị ThingsBoard | [helm/thingsboard/templates/web-ui.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/templates/web-ui.yaml) |
| | | `kafka` + `zookeeper` | StatefulSet (1) | TCP 9092, 2181 | Message queue đệm dữ liệu cảm biến | [helm/thingsboard/Chart.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/Chart.yaml) |
| **Portal App** | `flood-portal` | `hcm-flood-backend` | Deployment (2) | TCP 8000 (HTTP/WS) | FastAPI microservice tổng hợp dữ liệu ThingsBoard, thủy triều, thời tiết Open-Meteo | [backend/app/main.py](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/backend/app/main.py) |
| | | `hcm-flood-frontend` | Deployment (2) | TCP 80 (HTTP) | React/Vite SPA giao diện bản đồ ngập cho người dân | [frontend/nginx.conf](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/frontend/nginx.conf) |
| **Observability** | `cmc-monitoring` | `loki` | Deployment/StatefulSet | TCP 3100 | Log aggregation lưu trữ ra CMC S3 | [helm/observability/values.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/observability/values.yaml) |
| | | `promtail` | DaemonSet | Host log agent | Thu gom log từ các container | [helm/observability/values.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/observability/values.yaml) |
| | | `grafana` | Deployment (1) | TCP 80 | Trực quan hóa metrics & logs | [helm/observability/values.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/observability/values.yaml) |
| | | `prometheus` | Pre-installed | TCP 80 / 9090 | Thu thập metrics từ cluster | [helm/observability/values.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/observability/values.yaml) |

### 1.3 Phân Loại Hiện Trạng Chức Năng
1. **Đã có bằng chứng hoạt động thực tế trên cluster (Verified Live):**
   - Đã kết nối thành công ThingsBoard Node tới CMC DBaaS PostgreSQL `10.0.4.189:5432` (`iot_thingsboard`) và Redis `10.0.4.203:6379`.
   - Bộ 4 Kubernetes NetworkPolicies đã được triển khai và kiểm thử 100% đạt chuẩn:
     + Ingress Backend: chỉ nhận Frontend và Ingress Controller (chặn Pod lạ).
     + Ingress ThingsBoard Node: chỉ nhận Backend và Ingress Controller (chặn truy cập ngoài namespace).
     + Cross-namespace Egress Backend -> ThingsBoard Node: HTTP 200.
     + Egress Backend -> Internet Open-Meteo: HTTPS 443 OK.
     + Chặn Egress trái phép Backend -> Kafka: Timed out.
   - NGINX Ingress Controller đang tiếp nhận traffic định tuyến đến các dịch vụ.
2. **Có mã nguồn/cấu hình nhưng chưa xác minh thực tế:**
   - Cơ chế lưu log Loki lên CMC S3 (`https://s3.hcm-5.cloud.cmctelecom.vn`).
   - Tự động co giãn HPA trên `hcm-flood-backend` và `hcm-flood-frontend` khi CPU > 70%.
   - Chịu tải của WebSocket live stream `/ws/live` khi có hàng ngàn kết nối đồng thời.
   - Cơ chế quét Kyverno Admission Policy khi apply manifest.
3. **Dữ liệu Mock / Fallback:**
   - Dữ liệu 50 trạm quan trắc tĩnh (`ALL_50_STATIONS`) trong [backend/app/services/thingsboard_service.py](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/backend/app/services/thingsboard_service.py#L2854) hoạt động như cơ chế dự phòng (fallback) khi ThingsBoard chưa kết nối cảm biến thật.
   - Dữ liệu thủy triều trong `tide_service.py` được tính toán mô phỏng theo giờ.
   - Cảm biến IoT ngoài thực địa hiện được thay thế bởi bộ giả lập `simulator/single_device_simulator.py`.

### 1.4 Các Điểm Mâu Thuẫn Giữa Tài Liệu Và Cấu Hình Thực Tế
| Nội dung | Tài liệu ghi nhận | Thực tế cấu hình & Live Cluster | Phân tích & Rủi ro |
| :--- | :--- | :--- | :--- |
| **Dải mạng DBaaS Subnet** | `10.0.5.0/24` ([SYSTEM_TRAFFIC_ARCHITECTURE.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/docs/SYSTEM_TRAFFIC_ARCHITECTURE.md#L58)) hoặc `10.0.2.0/24` ([AI_LAB_INSTRUCTIONS.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/AI_LAB_INSTRUCTIONS.md#L25)) | IP thực tế của PostgreSQL là `10.0.4.189` và Redis là `10.0.4.203` (chung dải `10.0.4.0/24` với K8s nodes) | Từng gây ra lỗi `SocketTimeoutException` làm sập Pod ThingsBoard do Calico drop gói tin khi NetworkPolicy chặn dải ngoài `10.0.5.0/24`. Đã được khắc phục bằng CIDR `10.0.0.0/16`. |
| **Kiến trúc Tường lửa** | Palo Alto Firewall Active/Standby L7 với 2 chân Untrust/Trust ([SYSTEM_TRAFFIC_ARCHITECTURE.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/docs/SYSTEM_TRAFFIC_ARCHITECTURE.md#L25-L35)) | CMC Cloud Security Groups (L3/L4) kết hợp Calico NetworkPolicies trực tiếp trong Kubernetes | Tài liệu mô tả thiết kế phòng thủ chuyên sâu dự kiến, trong khi triển khai hiện tại dùng Native K8s NetworkPolicies. |
| **Namespace Production** | `iot-prod` ([docs/gitops-promotion.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/docs/gitops-promotion.md#L43)) | `flood-portal` (Portal) và `thingsboard` (ThingsBoard Platform) | Cấu hình GitOps ArgoCD cần đồng bộ đúng namespace thực tế để tránh deploy nhầm đích. |
| **Tính bền vững Kafka & ZooKeeper** | Đảm bảo hàng đợi an toàn chống mất gói tin ([SYSTEM_TRAFFIC_ARCHITECTURE.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/docs/SYSTEM_TRAFFIC_ARCHITECTURE.md#L105)) | `persistence.enabled: false` trong [helm/thingsboard/environments/prod/values.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/environments/prod/values.yaml#L184) | **RỦI RO CAO:** Khi Pod Kafka restart hoặc Node gặp sự cố, toàn bộ dữ liệu queue chưa kịp xử lý sẽ bị mất sạch vì chạy trên `emptyDir`. |

---

## 2. XÁC MINH MÔI TRƯỜNG THỰC TẾ & NHÓM LỆNH CẦN CHẠY

### 2.1 Các Thông Số Đã Xác Minh Trực Tiếp
- **Nền tảng Cloud:** CMC Cloud (OpenStack engine).
- **Kubernetes Version & Nodes:** CMC Kubernetes Engine (CKE), 9 nodes (System & Workload nodegroups).
- **CNI:** Calico v3.31.0 (hỗ trợ đầy đủ Ingress & Egress NetworkPolicies).
- **CSI Plugin:** `csi-cinder-nodeplugin` (Cinder Block Storage).
- **Ingress Controller:** Ingress-NGINX v1.15.1 (namespace `ingress-nginx`).
- **PostgreSQL Database:** CMC DBaaS IP `10.0.4.189:5432`, Database: `iot_thingsboard`, User: `iot_thingsboard`.
- **Redis Cache:** CMC DBaaS IP `10.0.4.203:6379`, mode standalone.

### 2.2 Nhóm Lệnh Chỉ Đọc Xác Minh Bổ Sung (Cần Chạy Trên Bastion)
Để hoàn thiện các giả định về lưu trữ, scheduling và giám sát, cần chạy các lệnh sau:

```bash
# Lệnh 1: Kiểm tra danh sách và cấu hình StorageClasses của CMC Cloud
kubectl get sc
kubectl describe sc $(kubectl get sc -o jsonpath='{.items[0].metadata.name}')

# Lệnh 2: Kiểm tra Node Labels và Taints giữa System và Workload NodeGroups
kubectl get nodes --show-labels
kubectl describe nodes | grep -E "Name:|Taints:|cmccloud-k8s-nodegroups|nodegroup"

# Lệnh 3: Kiểm tra mức tiêu thụ tài nguyên thực tế (Resource Metrics)
kubectl top nodes
kubectl top pods -n flood-portal
kubectl top pods -n thingsboard

# Lệnh 4: Kiểm tra trạng thái CSI Driver và Persistent Volumes
kubectl get csidrivers
kubectl get pv,pvc -A

# Lệnh 5: Kiểm tra kết nối của Loki tới CMC S3
kubectl logs -n cmc-monitoring -l app.kubernetes.io/name=loki --tail=40
```

---

## 3. KỊCH BẢN KIỂM THỬ TOÀN DIỆN (Prioritized Test Suite)

### 3.1 Ma Trận Kiểm Thử

| Mã Test | Hạng mục | Tên Kịch bản | Mức Ưu Tiên | Phân loại | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-NET-01** | Networking & Security | Kiểm tra toàn diện NetworkPolicy & Phân vùng cô lập | **P1 (Cao nhất)** | Kiểm tra chỉ đọc & Thâm nhập | **Sẵn sàng chạy** |
| **TC-WRK-02** | Workload Resilience | Khả năng phục hồi khi Pod ThingsBoard Node / Backend bị dừng đột ngột | **P1 (Cao nhất)** | Fault Injection (Pod disruption) | **Sẵn sàng chạy** |
| **TC-STO-03** | Storage & Persistence | Kiểm tra tính bền vững của Kafka Volume trên Cinder CSI khi Pod dời Node | **P1 (Cao nhất)** | Fault Injection & Storage check | **Thiếu dữ kiện SC** |
| **TC-IOT-04** | IoT Ingestion & Stress | Kiểm tra chịu tải tức thời khi 200 - 300 trạm cảm biến đồng thời gửi telemetry qua MQTT | **P1 (Cao nhất)** | Load & Stress Test (Async MQTT) | **Sẵn sàng chạy** |
| **TC-HPA-05** | Scaling & Load | Kiểm tra khả năng tự co giãn (HPA) của Backend và Frontend dưới tải lớn | **P2 (Trung bình)** | Load Test (k6 / wrk) | **Cần tài nguyên test** |
| **TC-GTO-06** | GitOps & Deployment | Kiểm tra Zero-Downtime Rolling Update & Rollback qua Devtron/ArgoCD | **P2 (Trung bình)** | Deployment verification | **Sẵn sàng chạy** |
| **TC-OBS-07** | Observability | Kiểm tra luồng đẩy Log lên CMC S3, Scraping Prometheus & Kích hoạt Alert | **P2 (Trung bình)** | Kiểm tra chỉ đọc & Alert trigger | **Sẵn sàng chạy** |

---

### 3.2 Chi Tiết Các Kịch Bản Kiểm Thử

#### TC-NET-01: NetworkPolicy Enforcement & Isolation Test
- **Mục tiêu:** Chứng minh toàn bộ lưu lượng nghiệp vụ được bảo toàn và 100% lưu lượng trái phép/ngoài luồng bị DROP.
- **Tiền đề:** Các NetworkPolicies đã được apply trong `flood-portal` và `thingsboard`.
- **Môi trường & Phạm vi:** Production (`flood-portal`, `thingsboard`, `default`).
- **Phân loại:** Kiểm tra chỉ đọc & thử nghiệm thâm nhập (Negative test).
- **Các bước thực hiện:**
  ```bash
  # 1. Test Ingress Backend từ Frontend (Hợp lệ)
  FE_POD=$(kubectl get pod -n flood-portal -l app.kubernetes.io/name=hcm-flood-frontend -o jsonpath='{.items[0].metadata.name}')
  kubectl exec -n flood-portal $FE_POD -- wget -qO- --timeout=5 http://hcm-flood-backend:8000/healthz

  # 2. Test Ingress ThingsBoard từ Backend (Hợp lệ)
  BE_POD=$(kubectl get pod -n flood-portal -l app.kubernetes.io/name=hcm-flood-backend -o jsonpath='{.items[0].metadata.name}')
  kubectl exec -n flood-portal $BE_POD -- python -c "import urllib.request; print(urllib.request.urlopen('http://iot-thingsboard-node.thingsboard.svc.cluster.local:8080/login', timeout=5).getcode())"

  # 3. Test Negative: Pod lạ trong flood-portal chọc vào Backend
  kubectl run intruder-portal -n flood-portal --image=curlimages/curl --rm -it --restart=Never --command -- curl --connect-timeout 4 http://hcm-flood-backend:8000/healthz

  # 4. Test Negative: Backend chọc cổng lạ vào hạ tầng nội bộ (Kafka 9092)
  kubectl exec -n flood-portal $BE_POD -- python -c "import socket; s = socket.socket(); s.settimeout(4); s.connect(('iot-thingsboard-kafka.thingsboard.svc.cluster.local', 9092))"
  ```
- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - Bước 1 & 2: HTTP 200 (PASS).
  - Bước 3 & 4: `Connection timed out` sau 4 giây (PASS). Nếu có bất kỳ kết nối nào thành công ở bước 3 & 4 -> FAIL.
- **Evidence lưu trữ:** Output terminal ghi nhận HTTP 200 và Connection timed out.
- **Cleanup & Rollback:** Tự động xóa (do có `--rm`).

---

#### TC-WRK-02: Workload Resiliency & Self-Healing Test
- **Mục tiêu:** Kiểm tra cơ chế tự phục hồi, startup probe, liveness probe và thời gian downtime khi Pod gặp sự cố sập.
- **Tiền đề:** Cluster đang vận hành ổn định; `iot-thingsboard-node-0` và `hcm-flood-backend` đang trạng thái `Running 1/1`.
- **Môi trường & Phạm vi:** `thingsboard`, `flood-portal`.
- **Phân loại:** Fault Injection (Kill pod).
- **Các bước thực hiện:**
  ```bash
  # 1. Đo thời gian phục hồi của Backend (Deployment có 2 replicas)
  # Kiểm tra liên tục availability qua Ingress trong lúc kill 1 pod:
  kubectl delete pod -n flood-portal -l app.kubernetes.io/name=hcm-flood-backend --wait=false
  for i in {1..30}; do curl -s -o /dev/null -w "%{http_code}\n" http://flood.web-ui.com/healthz; sleep 1; done

  # 2. Xóa Pod ThingsBoard Node (StatefulSet 1 replica) và theo dõi quá trình khởi động lại:
  kubectl delete pod iot-thingsboard-node-0 -n thingsboard --wait=false
  kubectl get pod iot-thingsboard-node-0 -n thingsboard -w
  ```
- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - Backend: Tỷ lệ HTTP 200 đạt 100% (không có 502/503) vì replica còn lại tiếp nhận traffic qua Service.
  - ThingsBoard: Pod tự tạo lại, vượt qua Startup Probe trong vòng 90-180s và chuyển sang `1/1 Running` mà không rơi vào `CrashLoopBackOff`.
- **Evidence lưu trữ:** Bảng mã trạng thái HTTP curl và log sự kiện `kubectl get pod -w`.
- **Cleanup & Rollback:** Không cần dọn dẹp (K8s controllers tự tái tạo pod).

---

#### TC-STO-03: Storage Persistence & Failover Test
- **Mục tiêu:** Xác minh dữ liệu không bị thất thoát khi Pod di chuyển giữa các Node khác nhau trên CMC Cloud.
- **Tiền đề:** Cần kích hoạt PVC cho Kafka trên StorageClass của CMC.
- **Môi trường & Phạm vi:** `thingsboard` namespace, `Workload NodeGroup`.
- **Phân loại:** Fault Injection & Data validation.
- **Các bước thực hiện:**
  ```bash
  # 1. Bơm message test vào Kafka topic 'tb-transport-test'
  # 2. Cordon worker node hiện tại chứa Kafka pod:
  KAFKA_NODE=$(kubectl get pod -n thingsboard iot-thingsboard-kafka-0 -o jsonpath='{.spec.nodeName}')
  kubectl cordon $KAFKA_NODE

  # 3. Xóa pod Kafka để scheduler chuyển sang worker node khác:
  kubectl delete pod iot-thingsboard-kafka-0 -n thingsboard

  # 4. Kiểm tra Cinder volume unattach khỏi node cũ và attach thành công vào node mới:
  kubectl describe pod iot-thingsboard-kafka-0 -n thingsboard | grep -E "Successfully attached|Mounted"

  # 5. Uncordon node cũ:
  kubectl uncordon $KAFKA_NODE
  ```
- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - Pod Kafka khởi động thành công trên node mới.
  - Dữ liệu topic và offset được giữ nguyên vẹn.
- **Evidence lưu trữ:** Log MountVolume/AttachVolume từ `kubectl describe pod`.
- **Cleanup & Rollback:** `kubectl uncordon $KAFKA_NODE`.

---

#### TC-IOT-04: Concurrent IoT Telemetry Ingestion Stress Test (200 - 300 Thiết Bị Gửi Đồng Thời Cùng 1 Lúc)
- **Mục tiêu:**
  - Kiểm tra độ bền vững, thông lượng (throughput) và khả năng đệm hàng đợi của chuỗi:
    `300 Sensors -> NGINX Ingress / LB (TCP 1883 / 8883) -> tb-mqtt-transport (2 replicas) -> Redis (Auth Cache 6379) -> Apache Kafka (Topic 9092) -> tb-node (Core & Rule Engine) -> PostgreSQL (5432)`.
  - Giả lập đúng tình huống thực tế: **Khi mưa dông cực đoan hoặc đỉnh triều xuất hiện, toàn bộ 200 - 300 trạm cảm biến đồng loạt chuyển trạng thái và gửi telemetry khẩn cấp về hệ thống trong cùng 1 cửa sổ thời gian (Thundering Herd / Simultaneous Surge)**.
  - Đánh giá khả năng chống nghẽn (backpressure) và quan sát phản ứng của các cảnh báo Prometheus trong [notification-rules.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/observability/files/notification-rules.yaml):
    + `HcmPodCpuAboveRequests`: Khi CPU của `tb-mqtt-transport` hoặc `tb-node` tăng đột biến.
    + `HcmPodMemoryNearLimit`: Khi bộ nhớ JVM hoặc buffer tăng cao tiệm cận limit 1Gi.
    + `HcmNodeCpuHigh`: Khi worker node chịu tải xả 300 kết nối đồng thời.

- **Tiền đề & Lưu ý Kiến Trúc Cổng (Port Resolution):**
  - Các Pod `iot-thingsboard-mqtt-transport-*`, `iot-thingsboard-kafka-0`, `iot-thingsboard-node-0` đang ở trạng thái `Running 1/1`.
  - **Lưu ý cổng MQTT nội bộ K8s:**
    + Service nội bộ `iot-thingsboard-mqtt.thingsboard.svc.cluster.local` theo cấu hình Helm [prod/values.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/environments/prod/values.yaml#L251) mở cổng **8883** (mapping tới container port **8081**).
    + Service LoadBalancer `iot-thingsboard-mqtt-lb` ([ingress/mqtt-loadbalancer.yaml](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/ingress/mqtt-loadbalancer.yaml)) mở cổng **1883** (mapping tới container port **8081**).
    + Script test dưới đây tự động hỗ trợ chọn Service / Port phù hợp.

- **Môi trường & Phạm vi:** `thingsboard` namespace, `Workload NodeGroup`.
- **Phân loại:** Load & Stress Test (Áp lực tải đồng thời nhiều thiết bị).

- **Các bước thực hiện:**
  ```bash
  # 1. Chạy Pod stress generator trong cluster sử dụng Threading Barrier để đồng loạt xả 200 - 300 kết nối cùng 1 giây
  kubectl run iot-stress-generator -n thingsboard --image=python:3.11-slim --rm -it --restart=Never -- /bin/bash -c "
  pip install --quiet paho-mqtt
  python3 -c \"
  import paho.mqtt.client as mqtt
  import threading, json, random, time, sys

  # Cấu hình kiểm thử
  BROKER = 'iot-thingsboard-mqtt.thingsboard.svc.cluster.local'
  PORT = 8883  # Mặc định của Service nội bộ (hoặc 1883 nếu qua Service iot-thingsboard-mqtt-lb)
  NUM_DEVICES = 300       # Số lượng thiết bị đồng thời (200 - 300)
  BURST_CYCLES = 5        # Mỗi thiết bị gửi 5 bản tin liên tiếp sau khi kích hoạt

  print(f'======================================================================')
  print(f'=== KỊCH BẢN: {NUM_DEVICES} THIẾT BỊ GỬI DỮ LIỆU ĐỒNG THỜI VỀ {BROKER}:{PORT} ===')
  print(f'=== SỬ DỤNG THREADING BARRIER ĐỂ ĐỒNG BỘ THỜI ĐIỂM GỬI TỨC THỜI (T0) ===')
  print(f'======================================================================')

  barrier = threading.Barrier(NUM_DEVICES)
  latencies = []
  success_count = 0
  fail_count = 0
  lock = threading.Lock()

  def run_sensor(dev_idx):
      global success_count, fail_count
      client_id = f'surge-sensor-{dev_idx:03d}'
      token = f'DEV_SURGE_TOKEN_{dev_idx:03d}'
      client = mqtt.Client(client_id=client_id)
      client.username_pw_set(token)

      try:
          client.connect(BROKER, PORT, keepalive=60)
          client.loop_start()

          # Đợi toàn bộ 300 thiết bị kết nối xong để cùng kích hoạt phát xung tại điểm T0
          barrier.wait()

          for c in range(BURST_CYCLES):
              t0 = time.time()
              payload = {
                  'water_level_cm': round(random.uniform(25.0, 75.0), 1),
                  'rainfall_mm': round(random.uniform(20.0, 60.0), 1),
                  'temperature_c': round(random.uniform(27.5, 31.5), 1),
                  'station_id': f'VN-HCM-{dev_idx:03d}',
                  'ts': int(time.time() * 1000)
              }
              info = client.publish('v1/devices/me/telemetry', json.dumps(payload), qos=1)
              info.wait_for_publish(timeout=5)
              lat = (time.time() - t0) * 1000  # ms
              with lock:
                  latencies.append(lat)
                  success_count += 1
              time.sleep(random.uniform(0.2, 0.5))

          client.loop_stop()
          client.disconnect()
      except Exception as e:
          with lock:
              fail_count += 1

  threads = []
  start_wall_time = time.time()
  for i in range(1, NUM_DEVICES + 1):
      t = threading.Thread(target=run_sensor, args=(i,))
      threads.append(t)
      t.start()

  for t in threads:
      t.join()

  total_wall_time = time.time() - start_wall_time
  latencies.sort()

  print(f'\n================ KẾT QUẢ ĐO ĐẠC HIỆU NĂNG ================')
  print(f'Tổng số thiết bị giả lập  : {NUM_DEVICES}')
  print(f'Tổng số tin nhắn gửi đi   : {success_count + fail_count}')
  print(f'Thành công (QoS 1 ACK)    : {success_count}')
  print(f'Thất bại / Timeout        : {fail_count}')
  print(f'Tỷ lệ thành công          : {(success_count / max(1, success_count + fail_count)) * 100:.2f}%')
  print(f'Thời gian hoàn tất        : {total_wall_time:.2f}s')
  if latencies:
      p50 = latencies[int(len(latencies) * 0.50)]
      p95 = latencies[int(len(latencies) * 0.95)]
      p99 = latencies[int(len(latencies) * 0.99)]
      avg_lat = sum(latencies) / len(latencies)
      print(f'Publish Latency (Avg)     : {avg_lat:.2f} ms')
      print(f'Publish Latency (p50)     : {p50:.2f} ms')
      print(f'Publish Latency (p95)     : {p95:.2f} ms')
      print(f'Publish Latency (p99)     : {p99:.2f} ms')
  print(f'==========================================================')
  \"
  "

  # 2. Đồng thời mở terminal thứ hai theo dõi tài nguyên Pods và Kafka consumer lag lúc xả tải:
  kubectl top pods -n thingsboard
  kubectl exec -n thingsboard iot-thingsboard-kafka-0 -- kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 --describe --group tb-node-consumer-group

  # 3. Mở terminal thứ ba theo dõi log của tb-mqtt-transport và tb-node xem có hiện tượng OOM / DB Timeout không:
  kubectl logs -n thingsboard -l app.kubernetes.io/name=thingsboard-mqtt --tail=50 -f
  kubectl logs -n thingsboard iot-thingsboard-node-0 -c thingsboard --tail=50 -f | grep -E "HikariPool|Connection timed out|Overwhelming"
  ```

- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - **Tỷ lệ thành công:** >= 99.0% bản tin nhận được PUBACK QoS 1 từ `tb-mqtt-transport`.
  - **Độ trễ phản hồi:** p95 latency < 500ms; p99 latency < 1500ms dưới tải đồng thời 300 clients.
  - **Khả năng đệm Kafka:** Broker tiếp nhận toàn bộ ~1,500 bản tin trong vài giây mà không bị crash. Consumer lag của `tb-node` tăng tạm thời rồi tự động xả về 0 trong < 30 giây.
  - **Tài nguyên Pods & Ổn định:**
    + `tb-mqtt-transport` (2 replicas): Phân bổ đều kết nối (~150 kết nối/pod), CPU không bị bão hòa 100%, RAM làm việc không vượt quá 85% limit (không bị OOMKilled).
    + `tb-node`: Pool kết nối DBaaS HikariCP không xuất hiện lỗi `Connection is not available, request timed out after 30000ms`.
    + Không có Pod nào bị restart (`Restarts: 0`) hay chuyển sang `CrashLoopBackOff`.
  - **Quan sát Alerts:** Nếu Prometheus alert `HcmPodCpuAboveRequests` kích hoạt, ghi nhận lại để điều chỉnh CPU request trong Helm chart.

- **Evidence lưu trữ:**
  - Thống kê tỷ lệ thành công và các mốc p50/p95/p99 từ stdout của Pod generator.
  - Snapshot `kubectl top pods -n thingsboard` lúc đỉnh điểm xung tải.
  - Báo cáo lag của Consumer Group từ Kafka CLI.

- **Cleanup & Rollback:**
  - Pod `iot-stress-generator` tự động hủy sau khi hoàn thành nhờ cờ `--rm`.

---

#### TC-HPA-05: Horizontal Pod Autoscaler (HPA) Load Test
- **Mục tiêu:** Đánh giá phản ứng tự động co giãn của Frontend và Backend khi tải tăng đột biến do thiên tai / mưa bão.
- **Tiền đề:** HPA đã được cấu hình (`minReplicas: 2`, `maxReplicas: 6`, `targetCPU: 70%`).
- **Môi trường & Phạm vi:** `flood-portal`.
- **Phân loại:** Load Test (Áp lực tải).
- **Các bước thực hiện:**
  ```bash
  # Chạy tải giả lập 500 Virtual Users trong 3 phút vào Backend /api/v1/dashboard
  kubectl run load-generator -n flood-portal --image=busybox --rm -it --restart=Never -- /bin/sh -c "
    while true; do
      wget -q -O- http://hcm-flood-backend:8000/api/v1/dashboard > /dev/null
    done
  "

  # Mở terminal theo dõi HPA:
  kubectl get hpa -n flood-portal -w
  ```
- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - CPU vượt quá 70%, HPA kích hoạt tăng số lượng replica từ 2 lên 4 hoặc 6 pod.
  - Sau khi ngừng tải, HPA duy trì cooldown window (scale down dần về 2 pods).
- **Evidence lưu trữ:** Log sự kiện scale của HPA (`kubectl describe hpa`).
- **Cleanup & Rollback:** Dừng process tải.

---

#### TC-GTO-06: GitOps Promotion & Zero-Downtime Rollback
- **Mục tiêu:** Xác minh tính toàn vẹn của quy trình GitOps, phát hiện cấu hình trôi dạt (drift) và khả năng rollback tức thì khi image mới có lỗi.
- **Tiền đề:** Ứng dụng quản lý bởi Devtron/ArgoCD.
- **Môi trường & Phạm vi:** CI/CD & Production cluster.
- **Phân loại:** Deployment verification.
- **Các bước thực hiện:**
  ```bash
  # 1. Ghi nhận revision hiện tại của Deployment
  kubectl rollout history deployment/hcm-flood-backend -n flood-portal

  # 2. Giả lập tình huống phiên bản mới gặp sự cố -> Thực hiện rollback tức thời:
  kubectl rollout undo deployment/hcm-flood-backend -n flood-portal

  # 3. Xác nhận trạng thái rollout:
  kubectl rollout status deployment/hcm-flood-backend -n flood-portal
  ```
- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - Quá trình rollback hoàn tất trong < 30 giây, không gây gián đoạn kết nối tới người dùng cuối.
- **Evidence lưu trữ:** History revision và log rollout status.

---

#### TC-OBS-07: Observability Pipeline, S3 Log Shipping & Alert Rules Verification
- **Mục tiêu:** Kiểm tra luồng đẩy log container lên CMC S3 qua Loki, thu thập Prometheus metrics và kiểm tra tính hợp lệ của các cảnh báo định nghĩa trong `helm/observability/files/notification-rules.yaml`.
- **Tiền đề:** Cụm observability đang hoạt động trong `cmc-monitoring`.
- **Môi trường & Phạm vi:** `cmc-monitoring`, `thingsboard`, `flood-portal`.
- **Phân loại:** Kiểm tra chỉ đọc & Alert evaluation.
- **Các bước thực hiện:**
  ```bash
  # 1. Kiểm tra Promtail thu gom log và đẩy về Loki S3:
  kubectl logs -n cmc-monitoring -l app.kubernetes.io/name=promtail --tail=30
  kubectl logs -n cmc-monitoring -l app.kubernetes.io/name=loki --tail=30 | grep -E "s3|upload|flush"

  # 2. Kiểm tra Prometheus đang cào metrics từ các node và pod:
  kubectl exec -n cmc-monitoring deploy/observability-grafana -- wget -qO- http://prometheus-server.cmc-monitoring:80/api/v1/targets | grep -E "health|up"

  # 3. Kiểm tra danh sách Alert Rules đang active trong cụm:
  kubectl get prometheusrule -A
  ```
- **Kết quả mong đợi & Tiêu chí PASS/FAIL:**
  - Promtail không có lỗi `connection refused` khi đẩy log sang Loki.
  - Loki flush log chunks thành công lên CMC S3 bucket `hcm-flood-logs`.
  - Các alert rules `HcmNodeCpuHigh`, `HcmPodCpuAboveRequests`, `HcmPodMemoryNearLimit` được nạp đầy đủ vào Prometheus engine.
- **Evidence lưu trữ:** Log upload S3 và danh sách targets của Prometheus.

---

## 4. ĐỀ XUẤT 5 CẢI TIẾN HẠ TẦNG VÀ WORKLOADS (Focus: CMC Cloud)

### Đề Xuất 1: Kích Hoạt Tính Bền Vững (Persistence) Cho Kafka & ZooKeeper Bằng Cinder CSI
- **Vấn đề cụ thể & Bằng chứng:**
  Trong file cấu hình sản xuất [helm/thingsboard/environments/prod/values.yaml:L184-L185](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/environments/prod/values.yaml#L184-L185), Kafka và ZooKeeper đang đặt `persistence.enabled: false`. Dữ liệu hàng đợi telemetry chạy trên `emptyDir`. Khi worker node reboot hoặc pod bị reschedule, toàn bộ dữ liệu cảm biến đang xếp hàng sẽ bị mất trắng.
- **Người hưởng lợi:** Đội ngũ Vận hành IoT và Hệ thống Cảnh báo ngập (không bị mất bản ghi sự kiện khi sự cố xảy ra).
- **Phạm vi MVP nhỏ nhất:**
  Chuyển `persistence.enabled: true`, gán `storageClass: cinder-csi` (hoặc storage class chuẩn của CMC Cloud), dung lượng 20GB cho Kafka và 10GB cho ZooKeeper.
- **Thành phần thay đổi:**
  File `helm/thingsboard/environments/prod/values.yaml` và `Chart.yaml`.
- **Khả năng hỗ trợ của CMC Cloud:**
  Cluster đã cài sẵn `csi-cinder-nodeplugin`, hỗ trợ đầy đủ OpenStack Cinder Block Storage.
- **Acceptance Criteria & Test chứng minh:**
  Gửi 100 message vào Kafka -> Delete Pod Kafka -> Pod mount lại đúng volume cũ và đọc tiếp 100 message không thiếu sót.
- **Độ phức tạp / Chi phí / Ưu tiên:** Độ phức tạp: Thấp | Chi phí: Rất thấp (30GB Cinder Block) | **ƯU TIÊN 1 (Cần làm ngay)**.

---

### Đề Xuất 2: Nâng Cấp ThingsBoard Core (`tb-node`) Từ Single-Pod Lên High Availability (HA Active-Active)
- **Vấn đề cụ thể & Bằng chứng:**
  `tb-node` hiện đang cấu hình StatefulSet với `replicaCount: 1` ([helm/thingsboard/environments/prod/values.yaml:L267](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/helm/thingsboard/environments/prod/values.yaml#L267)). Đây là Single Point of Failure (SPOF). Khi pod này restart (mất 2-4 phút khởi động Java Spring Boot), toàn bộ API và luồng xử lý cảnh báo ngập bị gián đoạn hoàn toàn.
- **Người hưởng lợi:** Toàn bộ người dùng Cổng thông tin và các đội cứu hộ khẩn cấp.
- **Phạm vi MVP nhỏ nhất:**
  Tăng `replicaCount: 2` cho `tb-node`, cấu hình `podAntiAffinity` để 2 pod nằm trên 2 Worker Node vật lý khác nhau. Mạng cluster RPC qua cổng `9001` đã được mở sẵn trong NetworkPolicy.
- **Thành phần thay đổi:**
  `helm/thingsboard/environments/prod/values.yaml` (mục `node.replicaCount` và `node.affinity`).
- **Khả năng hỗ trợ của CMC Cloud:**
  Cụm có sẵn 2 Worker Nodes thuộc `Workload NodeGroup`, đủ tài nguyên CPU/RAM cho 2 replica.
- **Acceptance Criteria & Test chứng minh:**
  Kill pod `iot-thingsboard-node-0`, traffic API vẫn được pod `iot-thingsboard-node-1` xử lý liên tục với 0 downtime.
- **Độ phức tạp / Chi phí / Ưu tiên:** Độ phức tạp: Trung bình | Chi phí: Cần cấp phát thêm 2 vCPU / 4GB RAM | **ƯU TIÊN 2 (Cần làm ngay)**.

---

### Đề Xuất 3: Bổ Sung Endpoint Prometheus Metrics & Tracing Cho Backend FastAPI
- **Vấn đề cụ thể & Bằng chứng:**
  File [backend/app/main.py](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/backend/app/main.py) hiện chỉ có endpoint `/healthz`, hoàn toàn thiếu `/metrics`. Cụm Prometheus trong namespace `cmc-monitoring` không thể thu thập số liệu RED (Rate, Errors, Duration) hay số lượng kết nối WebSocket đang hoạt động.
- **Người hưởng lợi:** SRE / DevOps engineer theo dõi hiệu năng hệ thống.
- **Phạm vi MVP nhỏ nhất:**
  Thêm thư viện `prometheus-fastapi-instrumentator` vào `backend/requirements.txt`, expose `/metrics`, và thêm cấu hình ServiceMonitor hoặc annotation scrape vào `helm/hcm-flood-backend`.
- **Thành phần thay đổi:**
  `backend/requirements.txt`, `backend/app/main.py`, `helm/hcm-flood-backend/templates/deployment.yaml`.
- **Khả năng hỗ trợ của CMC Cloud:**
  Hệ thống `cmc-monitoring` đã có sẵn Prometheus Server.
- **Acceptance Criteria & Test chứng minh:**
  Prometheus server truy cập `http://hcm-flood-backend:8000/metrics` cào được dữ liệu `http_requests_total` và `websocket_active_connections`.
- **Độ phức tạp / Chi phí / Ưu tiên:** Độ phức tạp: Rất thấp | Chi phí: 0 đồng | **ƯU TIÊN 3 (Nên làm sớm)**.

---

### Đề Xuất 4: Tối Ưu Hóa WebSocket Streaming & Rate-Limiting Tại Ingress NGINX
- **Vấn đề cụ thể & Bằng chứng:**
  Backend hiện tại có endpoint `/ws/live` chạy vòng lặp vô tận `while True: build_dashboard_data(); asyncio.sleep(1.0)`. Mỗi 1 giây, backend lại truy vấn lại dữ liệu và sinh JSON gửi về client. Nếu có 1000 người dân cùng mở web khi mưa ngập, backend sẽ bị nghẽn CPU và quá tải mạng.
- **Người hưởng lợi:** Người dùng truy cập web (tốc độ tải mượt mà, không bị sập kết nối).
- **Phạm vi MVP nhỏ nhất:**
  1. Cấu hình NGINX Ingress Controller annotations: `nginx.ingress.kubernetes.io/limit-connections: "20"`, `nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"`.
  2. Bổ sung cơ chế in-memory caching 3-5 giây cho `build_dashboard_data()` trong backend để tránh tính toán trùng lặp cho nhiều client kết nối đồng thời.
- **Thành phần thay đổi:**
  `helm/hcm-flood-backend/values.yaml` (ingress annotations) và `backend/app/main.py`.
- **Khả năng hỗ trợ của CMC Cloud:**
  NGINX Ingress Controller trên CMC Cloud hỗ trợ đầy đủ các module rate-limiting và connection-limiting.
- **Acceptance Criteria & Test chứng minh:**
  Chạy load test 200 client WebSocket đồng thời, CPU backend không vượt quá 60% và không có client nào bị rớt kết nối.
- **Độ phức tạp / Chi phí / Ưu tiên:** Độ phức tạp: Trung bình | Chi phí: 0 đồng | **ƯU TIÊN 4**.

---

### Đề Xuất 5: Đồng Bộ Hóa Toàn Diện Tài Liệu Kiến Trúc Mạng Với Thực Tế Hạ Tầng CMC Cloud
- **Vấn đề cụ thể & Bằng chứng:**
  Tài liệu [docs/SYSTEM_TRAFFIC_ARCHITECTURE.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/docs/SYSTEM_TRAFFIC_ARCHITECTURE.md) và [AI_LAB_INSTRUCTIONS.md](file:///d:/workspace/projects/iot-thingsboard/thingsboard-ce-k8s/AI_LAB_INSTRUCTIONS.md) ghi thông tin subnet không khớp với thực tế IP của CMC DBaaS (`10.0.4.x` thay vì `10.0.5.0/24`). Điều này gây nhầm lẫn lớn khi bàn giao vận hành và cấu hình firewall.
- **Người hưởng lợi:** Toàn bộ kỹ sư vận hành, bảo mật và đối tác hạ tầng.
- **Phạm vi MVP nhỏ nhất:**
  Cập nhật sơ đồ Mermaid, ma trận định tuyến và bảng phân bổ IP trong `SYSTEM_TRAFFIC_ARCHITECTURE.md` phản ánh chính xác CIDR `10.0.4.0/24` cho cả Node và DBaaS, cùng cấu hình Calico NetworkPolicies thực tế.
- **Thành phần thay đổi:**
  `docs/SYSTEM_TRAFFIC_ARCHITECTURE.md`.
- **Khả năng hỗ trợ của CMC Cloud:**
  Không phụ thuộc hệ thống.
- **Acceptance Criteria & Test chứng minh:**
  Tài liệu kiến trúc phản ánh chính xác 100% các IP, Port và NetworkPolicies đang chạy live trên cụm.
- **Độ phức tạp / Chi phí / Ưu tiên:** Độ phức tạp: Rất thấp | Chi phí: 0 đồng | **ƯU TIÊN 5**.

---

## 5. THỨ TỰ THỰC HIỆN KHUYẾN NGHỊ (Implementation Roadmap)

| Giai đoạn | Hạng mục thực hiện | Mục tiêu cốt lõi | Rủi ro tác động | Ước lượng công sức |
| :--- | :--- | :--- | :--- | :--- |
| **Giai đoạn 1 (Ngay lập tức)** | **Kích hoạt Persistent Volume cho Kafka** (Đề xuất 1) | Chống mất mát dữ liệu telemetry khi pod restart | Rất thấp (chỉ cần tạo PVC mới) | 0.5 ngày công |
| **Giai đoạn 2 (Ngắn hạn)** | **Nâng cấp `tb-node` lên HA 2 Replicas** (Đề xuất 2) | Xóa bỏ điểm sập duy nhất (SPOF) cho hệ thống IoT | Thấp (StatefulSet scale up bình thường) | 0.5 ngày công |
| **Giai đoạn 3 (Trung hạn)** | **Bổ sung Prometheus Metrics cho Backend** (Đề xuất 3) | Giám sát độ trễ và tỷ lệ lỗi thời gian thực | Rất thấp (thêm endpoint không ảnh hưởng logic) | 1 ngày công |
| **Giai đoạn 4 (Hoàn thiện)** | **Rate-limiting & Tối ưu WebSocket Ingress** (Đề xuất 4) | Bảo vệ hệ thống trước bão truy cập mùa mưa lũ | Trung bình (cần kiểm thử tải kỹ lưỡng) | 1 ngày công |
| **Giai đoạn 5 (Tài liệu)** | **Chuẩn hóa tài liệu kiến trúc & CIDR** (Đề xuất 5) | Đảm bảo tính nhất quán giữa tài liệu và hạ tầng | Không có | 0.5 ngày công |
