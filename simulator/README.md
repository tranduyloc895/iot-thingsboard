# Luồng dữ liệu thật và simulator

Dashboard chỉ lấy telemetry từ ThingsBoard; không tự sinh phép đo. Simulator là nguồn thử nghiệm MQTT có chủ đích, gửi `source=simulator`; không phải fallback trong backend/UI. Không có nguồn quan trắc triều cường được cấu hình nên mục này hiển thị thông báo chưa có nguồn, không vẽ đường cong giả.

## Danh tính và chạy fleet

Mỗi station có NODE_INDEX cố định (0..49), DEVICE_NAME `VN-HCM-001`..`VN-HCM-050`. Token được lưu trong volume `simulator-state`; `compose down` không xóa volume. Không dùng `down -v` nếu cần giữ credentials. Không scale một service dùng cùng NODE_INDEX.

Tại máy simulator, cập nhật source rồi chạy:

```bash
cd simulator
python3 generate_compose.py
docker compose -f compose.fleet.yml build station-001
docker compose -f compose.fleet.yml up -d --no-build
```

Từ subnet simulator (10.0.1.0/24), endpoint MQTT là firewall `10.0.1.200:1883`, NAT tới ILB `10.0.0.225:1883`. Không gọi thẳng ILB từ untrust subnet. Kết nối nc tới firewall chỉ kiểm tra TCP; xác nhận thêm MQTT CONNACK/PUBACK và timestamp telemetry trong ThingsBoard.

Cung cấp THINGSBOARD_HOST/PORT và provisioning credentials của profile từ nguồn quản lý credentials. Không commit credentials. Các device tên ngẫu nhiên cũ không bị xóa tự động. Backend phân trang toàn bộ device và chọn telemetry mới nhất theo station; thiết bị không ánh xạ được không bị gán tùy tiện theo thứ tự.

MQTT dùng QoS 1 và chỉ báo publish sau PUBACK. Lỗi provisioning/MQTT được ghi log và retry có backoff. Token đã lưu được dùng lại khi recreate container. Nếu token bị thu hồi và profile cấm provision device đã có, cần khôi phục token chính xác từ ThingsBoard vào credential store; không xóa thiết bị để né lỗi.

## Backend và Argo CD

Production trên cluster CMC: `THINGSBOARD_URL=http://iot-thingsboard-node.thingsboard.svc.cluster.local:8080`.
Dev trên cluster CMC: `THINGSBOARD_URL=http://thingsboard-node.flood-portal-dev.svc.cluster.local:8080`.

Backend lấy THINGSBOARD_USERNAME/THINGSBOARD_PASSWORD qua Secret `thingsboard-api-credentials` trong namespace tương ứng. Phải dùng tenant account của đúng ThingsBoard. Bỏ override URL sai và `envFrom: []` trong Argo CD Application; valuesObject có ưu tiên cao hơn values file. NetworkPolicy egress phải chọn namespace và nhãn node thực tế; không mở toàn bộ mạng để sửa lỗi.

## Kiểm tra sau rollout

- `/api/v1/dashboard` và `/ws/live`: `errors` nêu lỗi từng nguồn, `weather.error` nêu lỗi weather, từng device/node offline có `error`.
- Không có dữ liệu hoặc quá 60 giây: status OFFLINE, phép đo null, không hiện 0cm như một phép đo thật.
- Tắt nguồn telemetry: UI báo offline. Dừng backend: UI bỏ dữ liệu cũ và thông báo mất WS. Khôi phục nguồn: tự kết nối và cập nhật lại.
- Open-Meteo lỗi: ba phép đo thời tiết null và thông báo lỗi ngay phần thời tiết, không trả baseline.

## Kiểm thử và rollback

```bash
cd backend && python3 -m unittest discover -s tests -v
cd ../simulator && python3 -m unittest discover -s tests -v
cd ../frontend && npm ci && npm run lint && npm run build
```

Rollout dev trước, xác minh đúng image digest rồi promote cùng digest lên prod. Rollback bằng cách khôi phục image digest và cấu hình Application đã lưu trong GitOps; Argo CD sync lại. Giữ volume credentials. Không xóa device, database, hoặc tắt NetworkPolicy.
