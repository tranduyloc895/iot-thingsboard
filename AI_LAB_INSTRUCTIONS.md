# CONTEXT & GOAL
Chúng ta đang thực hiện bài LAB "Hệ thống cảnh báo ngập và thời tiết TP.HCM" bằng cách triển khai ThingsBoard CE lên nền tảng CMC Cloud Kubernetes.
Mục tiêu: Đạt điểm tối đa về thiết kế tự động hóa GitOps, phân bổ tài nguyên hợp lý và bảo mật.

# TECH STACK & INFRASTRUCTURE
- Cloud Provider: CMC Cloud.
- K8s Cluster: CMC Kubernetes Engine (CKE) với 2 NodeGroups (System và Workload).
- CI/CD & GitOps: Devtron (dùng lõi ArgoCD App of Apps).
- Database: CMC DBaaS (PostgreSQL) - External DB.
- Object Storage: CMC S3-compatible.

# STRICT RULES FOR AGENT
1. KHÔNG VIẾT LẠI YAML TỪ ĐẦU: Chỉ tập trung chỉnh sửa các file `values.yaml` của Helm Chart ThingsBoard có sẵn trong repo.
2. KHÔNG CÀI DB NỘI BỘ: Phải vô hiệu hóa PostgreSQL đi kèm Chart, trỏ toàn bộ về DBaaS CMC.
3. INGRESS: Sử dụng NGINX Ingress Controller (port 80/443 cho Web UI, 1883 cho MQTT).
4. QUY HOẠCH NODE (NODE AFFINITY): Bắt buộc dùng `nodeSelector` hoặc `tolerations` để ép ThingsBoard chạy trên Workload NodeGroup, không được tràn sang System NodeGroup.

# ROADMAP (STEP-BY-STEP INSTRUCTIONS FOR AGENT)
Agent phải hỏi và hướng dẫn User thực hiện TỪNG BƯỚC một. Đợi User xác nhận làm xong Phase hiện tại mới được chuyển sang Phase tiếp theo.

### Phase 0: Khởi tạo Hạ tầng & Sizing (Thao tác tay trên CMC)
- Yêu cầu User xác nhận đã tạo mạng lưới VPC và Subnet:
  + VPC CIDR: `10.0.0.0/16`
  + Public Subnet: `10.0.1.0/24` (Dành cho Load Balancer)
  + Private Subnet: `10.0.2.0/24` (Dành cho K8s Worker Nodes và DBaaS)
- Yêu cầu User xác nhận đã cấp phát đúng cấu hình (BOM) sau để đủ chạy LAB:
  + System NodeGroup (K8s): 2 Nodes (Cấu hình: 4 vCPU, 8GB RAM).
  + Workload NodeGroup (K8s): 2 Nodes (Cấu hình: 4 vCPU, 8GB RAM).
  + CMC DBaaS PostgreSQL: 2 vCPU, 4GB RAM, Storage 50GB.
- Nhắc User cấu hình Security Group: Mở Port `5432` cho DBaaS (chỉ nhận IP từ Private Subnet `10.0.2.0/24`). Load Balancer mở Port `80/443` và `1883` ra public (0.0.0.0/0).
- Yêu cầu User cung cấp thông tin cho Agent: `DB_HOST`, `DB_USER`, `DB_PASSWORD` và tên của `StorageClass` mặc định trên CMC K8s.

### Phase 1: Tinh chỉnh cấu hình Database & Storage (File values.yaml)
- Agent tìm file `values.yaml` chính của ThingsBoard trong repo.
- Hướng dẫn User sửa file để TẮT DB nội bộ (`postgresql.enabled: false`).
- Thêm block cấu hình trỏ tới External PostgreSQL của CMC bằng các thông tin User cung cấp ở Phase 0.
- Quan trọng: Chỉnh cấu hình `database.ts.type` thành `sql` (để dùng luôn Postgres lưu trữ telemetry, không cần cài thêm Cassandra cho bài LAB này nhằm tiết kiệm RAM).
- Cập nhật biến `storageClass` cho Kafka, Redis, Zookeeper khớp với tên StorageClass của CMC.

### Phase 2: Sizing & Quy hoạch NodeGroup (Tối ưu tài nguyên)
- Hướng dẫn User khai báo giới hạn tài nguyên (BOM/Sizing) trong `values.yaml`.
- Đặt `resources.requests` và `resources.limits` (CPU/RAM) chi tiết cho:
  + `kafka` và `zookeeper`.
  + `redis`.
  + Các vi dịch vụ Java lõi: `tb-core`, `tb-rule-engine`, `tb-mqtt-transport`. Cần chú ý set thêm các biến môi trường Java Heap Size (`JAVA_OPTS`: `-Xms` và `-Xmx`) phù hợp với Node 8GB RAM để tránh lỗi OOMKilled.
- Bổ sung cấu hình `nodeSelector` (ví dụ: `nodegroup: workload`) vào tất cả các Deployment/StatefulSet trong `values.yaml` để ép app chạy đúng Node.

### Phase 3: Kịch bản mô phỏng IoT (Tạo file mqtt_simulator.py)
- Agent viết một file mã nguồn Python độc lập: `scripts/mqtt_simulator.py`.
- Sử dụng thư viện `paho-mqtt`.
- Payload JSON gửi lên phải đúng ngữ cảnh bài toán: `{"water_level_cm": 45, "rainfall_mm": 12, "temperature_c": 31, "status": "warning"}`.
- Cấu hình file script có các biến dễ chỉnh sửa: `THINGSBOARD_HOST` (IP Public của Load Balancer K8s) và `ACCESS_TOKEN`.
- Viết vòng lặp `while True` push data mỗi 3 giây. Hướng dẫn User cách cài thư viện và chạy file này.

### Phase 4: Thiết lập GitOps qua nền tảng Devtron (UI)
- LƯU Ý: Tuyệt đối không tạo file `argocd-app.yaml`. Agent phải hướng dẫn User thao tác trực tiếp trên giao diện web của Devtron.
- Bước 4.1 - Kết nối Git: Hướng dẫn User vào mục `Global Configurations -> Git Repositories` trên Devtron để add kho GitHub chứa mã nguồn ThingsBoard (vừa được tinh chỉnh ở Phase 1 & 2).
- Bước 4.2 - Tạo Ứng dụng: Hướng dẫn User tạo một `Helm App` hoặc `Custom App` mới trên Devtron. Đặt tên là `iot-thingsboard`, chọn Namespace là `thingsboard`.
- Bước 4.3 - Cấu hình Môi trường: Hướng dẫn User chọn nguồn là Git Repo vừa add, trỏ đúng vào thư mục chứa Helm Chart của ThingsBoard. 
- Bước 4.4 - Áp dụng Values: Hướng dẫn User copy/paste hoặc link trực tiếp file `values.yaml` đã cấu hình hoàn chỉnh vào ô "Values" trên giao diện Devtron.
- Bước 4.5 - Triển khai: Hướng dẫn User bật tính năng Auto-Sync (GitOps) và bấm Deploy để Devtron ngầm điều khiển ArgoCD kéo hệ thống xuống cụm CMC.