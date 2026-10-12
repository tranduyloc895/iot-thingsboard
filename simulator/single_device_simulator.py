import time
import json
import random
import os
import socket
import hashlib
import paho.mqtt.client as mqtt

# ==============================================================================
# 10 TUYẾN ĐƯỜNG NGẬP TRỌNG ĐIỂM TP.HCM (50 TRẠM QUAN TRẮC IoT CỐ ĐỊNH)
# ==============================================================================
ROADS = [
    {
        "id": "road-01",
        "name": "Huỳnh Tấn Phát",
        "district": "Quận 7",
        "nodes": [
            {"name": "Cầu Tân Thuận", "lat": 10.7610, "lon": 106.7195, "base_water": 18.0},
            {"name": "Ngã tư Nguyễn Thị Thập", "lat": 10.7485, "lon": 106.7240, "base_water": 38.0},
            {"name": "Rốn ngập Trần Trọng Cung", "lat": 10.7412, "lon": 106.7285, "base_water": 56.0},
            {"name": "Chân cầu Phú Mỹ", "lat": 10.7335, "lon": 106.7330, "base_water": 42.0},
            {"name": "Cầu Phú Xuân", "lat": 10.7220, "lon": 106.7380, "base_water": 22.0},
        ]
    },
    {
        "id": "road-02",
        "name": "Trần Xuân Soạn",
        "district": "Quận 7",
        "nodes": [
            {"name": "Chân cầu Tân Thuận 2", "lat": 10.7605, "lon": 106.7170, "base_water": 20.0},
            {"name": "Bờ kè Lâm Văn Bền", "lat": 10.7570, "lon": 106.7145, "base_water": 44.0},
            {"name": "Rốn ngập Cầu Kênh Tẻ", "lat": 10.7550, "lon": 106.7120, "base_water": 52.0},
            {"name": "Cầu Rạch Ông", "lat": 10.7515, "lon": 106.7020, "base_water": 36.0},
            {"name": "Chân cầu Chữ Y", "lat": 10.7490, "lon": 106.6920, "base_water": 16.0},
        ]
    },
    {
        "id": "road-03",
        "name": "Quốc Hương - Xuân Thủy",
        "district": "TP. Thủ Đức",
        "nodes": [
            {"name": "Ngã ba Xa Lộ Hà Nội", "lat": 10.8015, "lon": 106.7380, "base_water": 15.0},
            {"name": "Ngã tư Xuân Thủy", "lat": 10.8030, "lon": 106.7345, "base_water": 32.0},
            {"name": "Rốn ngập Quốc Hương", "lat": 10.8035, "lon": 106.7321, "base_water": 54.0},
            {"name": "Trường Quốc tế BIS", "lat": 10.8075, "lon": 106.7300, "base_water": 40.0},
            {"name": "Ngã ba Nguyễn Văn Hưởng", "lat": 10.8120, "lon": 106.7280, "base_water": 24.0},
        ]
    },
    {
        "id": "road-04",
        "name": "Kha Vạn Cân - Đặng Thị Rành",
        "district": "TP. Thủ Đức",
        "nodes": [
            {"name": "Ngã 5 Thủ Đức", "lat": 10.8495, "lon": 106.7625, "base_water": 22.0},
            {"name": "Kha Vạn Cân - Dương Văn Cam", "lat": 10.8510, "lon": 106.7600, "base_water": 45.0},
            {"name": "Rốn trũng Chợ Thủ Đức", "lat": 10.8525, "lon": 106.7582, "base_water": 60.0},
            {"name": "Đặng Thị Rành - Tô Ngọc Vân", "lat": 10.8535, "lon": 106.7565, "base_water": 38.0},
            {"name": "Cầu Ngang - Võ Văn Ngân", "lat": 10.8550, "lon": 106.7535, "base_water": 18.0},
        ]
    },
    {
        "id": "road-05",
        "name": "Nguyễn Hữu Cảnh",
        "district": "Bình Thạnh",
        "nodes": [
            {"name": "Chân Cầu Sài Gòn", "lat": 10.7990, "lon": 106.7220, "base_water": 14.0},
            {"name": "The Manor - Landmark 81", "lat": 10.7970, "lon": 106.7185, "base_water": 30.0},
            {"name": "Rốn ngập Ung Văn Khiêm", "lat": 10.7950, "lon": 106.7150, "base_water": 48.0},
            {"name": "Hầm chui Nguyễn Hữu Cảnh", "lat": 10.7915, "lon": 106.7115, "base_water": 42.0},
            {"name": "Chân Cầu Thủ Thiêm 1", "lat": 10.7875, "lon": 106.7080, "base_water": 16.0},
        ]
    },
    {
        "id": "road-06",
        "name": "Ung Văn Khiêm - Đinh Bộ Lĩnh",
        "district": "Bình Thạnh",
        "nodes": [
            {"name": "Ngã tư Hàng Xanh", "lat": 10.8010, "lon": 106.7115, "base_water": 15.0},
            {"name": "Đinh Bộ Lĩnh - Chu Văn An", "lat": 10.8080, "lon": 106.7110, "base_water": 32.0},
            {"name": "Trước Bến xe Miền Đông", "lat": 10.8120, "lon": 106.7110, "base_water": 46.0},
            {"name": "Cầu Bình Triệu", "lat": 10.8145, "lon": 106.7125, "base_water": 34.0},
            {"name": "Đường D2 (Nguyễn Gia Trí)", "lat": 10.8120, "lon": 106.7160, "base_water": 18.0},
        ]
    },
    {
        "id": "road-07",
        "name": "Lê Đức Thọ - Nguyễn Văn Khối",
        "district": "Gò Vấp",
        "nodes": [
            {"name": "Ngã 3 Nguyễn Oanh", "lat": 10.8440, "lon": 106.6790, "base_water": 16.0},
            {"name": "Lê Đức Thọ - Thống Nhất", "lat": 10.8400, "lon": 106.6750, "base_water": 36.0},
            {"name": "Rốn ngập Cây Trâm", "lat": 10.8350, "lon": 106.6720, "base_water": 54.0},
            {"name": "Công viên Làng Hoa", "lat": 10.8385, "lon": 106.6660, "base_water": 38.0},
            {"name": "Nguyễn Văn Khối - Lê Văn Thọ", "lat": 10.8410, "lon": 106.6610, "base_water": 19.0},
        ]
    },
    {
        "id": "road-08",
        "name": "Phan Huy Ích - Phạm Văn Chiêu",
        "district": "Gò Vấp",
        "nodes": [
            {"name": "Ngã 3 Quang Trung", "lat": 10.8380, "lon": 106.6510, "base_water": 15.0},
            {"name": "Phạm Văn Chiêu - Huỳnh Văn Nghệ", "lat": 10.8335, "lon": 106.6450, "base_water": 32.0},
            {"name": "Rốn ngập Cầu Hy Vọng", "lat": 10.8285, "lon": 106.6390, "base_water": 49.0},
            {"name": "Cầu Tham Lương", "lat": 10.8250, "lon": 106.6320, "base_water": 36.0},
            {"name": "Ngã 3 Trường Chinh", "lat": 10.8210, "lon": 106.6265, "base_water": 18.0},
        ]
    },
    {
        "id": "road-09",
        "name": "Nguyễn Văn Quá",
        "district": "Quận 12",
        "nodes": [
            {"name": "Cầu Tham Lương - Trường Chinh", "lat": 10.8360, "lon": 106.6270, "base_water": 17.0},
            {"name": "Đông Hưng Thuận", "lat": 10.8420, "lon": 106.6235, "base_water": 35.0},
            {"name": "Rốn ngập Chợ Cầu", "lat": 10.8465, "lon": 106.6210, "base_water": 53.0},
            {"name": "Ngã 3 Tô Ký", "lat": 10.8520, "lon": 106.6180, "base_water": 37.0},
            {"name": "Ngã ba QL1A Tân Thới Hiệp", "lat": 10.8580, "lon": 106.6150, "base_water": 20.0},
        ]
    },
    {
        "id": "road-10",
        "name": "Hồ Học Lãm - An Dương Vương",
        "district": "Bình Tân",
        "nodes": [
            {"name": "Bến Phú Định", "lat": 10.7100, "lon": 106.6280, "base_water": 22.0},
            {"name": "Cầu Mỹ Thuận", "lat": 10.7140, "lon": 106.6230, "base_water": 40.0},
            {"name": "Rốn ngập Hồ Học Lãm", "lat": 10.7180, "lon": 106.6185, "base_water": 55.0},
            {"name": "Đại lộ Võ Văn Kiệt", "lat": 10.7230, "lon": 106.6150, "base_water": 39.0},
            {"name": "Kinh Dương Vương (Vòng xoay An Lạc)", "lat": 10.7310, "lon": 106.6110, "base_water": 18.0},
        ]
    }
]

# Tạo danh sách phẳng 50 trạm IoT cố định
ALL_STATION_NODES = []
for road_idx, road in enumerate(ROADS):
    for node_idx, node in enumerate(road["nodes"]):
        node_num = road_idx * 5 + node_idx + 1
        ALL_STATION_NODES.append({
            "node_num": node_num,
            "road_id": road["id"],
            "road_name": road["name"],
            "district": road["district"],
            "station_node": node["name"],
            "segment_idx": node_idx,
            "lat": node["lat"],
            "lon": node["lon"],
            "base_water": node["base_water"]
        })

# ==========================================
# CẤU HÌNH BIẾN MÔI TRƯỜNG & KẾT NỐI
# ==========================================
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "10.0.0.225")
PORT = int(os.getenv("PORT", "1883"))
PROVISION_KEY = os.getenv("PROVISION_KEY", "")
PROVISION_SECRET = os.getenv("PROVISION_SECRET", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

# Lấy Container ID hoặc HOSTNAME để ánh xạ vào đúng trạm cố định
HOSTNAME = socket.gethostname()
CONTAINER_ID = HOSTNAME[-6:] if len(HOSTNAME) >= 6 else HOSTNAME

# Tính toán trạm cố định cho container này (0..49)
if os.getenv("NODE_INDEX"):
    station_idx = int(os.getenv("NODE_INDEX")) % len(ALL_STATION_NODES)
else:
    seed_val = int(hashlib.md5(HOSTNAME.encode()).hexdigest(), 16)
    station_idx = seed_val % len(ALL_STATION_NODES)

assigned_station = ALL_STATION_NODES[station_idx]
DEVICE_NAME = os.getenv("DEVICE_NAME", f"HCM_Vehicle_{CONTAINER_ID}_{assigned_station['node_num']:02d}")

# Tọa độ cố định tại trạm giao thông
station_lat = assigned_station["lat"]
station_lon = assigned_station["lon"]


def provision_device():
    provision_client = mqtt.Client()
    # Theo chuẩn ThingsBoard: Username kết nối BẮT BUỘC là "provision"
    provision_client.username_pw_set("provision")
    token = None
    done = False

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe("/provision/response")
            payload = {
                "deviceName": DEVICE_NAME,
                "provisionDeviceKey": PROVISION_KEY,
                "provisionDeviceSecret": PROVISION_SECRET
            }
            client.publish("/provision/request", json.dumps(payload))
        else:
            print(f"[{DEVICE_NAME}] Kết nối MQTT Provisioning bị từ chối, rc={rc}")

    def on_message(client, userdata, msg):
        nonlocal token, done
        if msg.topic == "/provision/response":
            try:
                response = json.loads(msg.payload.decode())
                if response.get("status") == "SUCCESS":
                    token = response.get("credentialsValue")
                    print(f"[{DEVICE_NAME}] Đăng ký thành công! Token: {token}")
                else:
                    print(f"[{DEVICE_NAME}] Lỗi đăng ký từ ThingsBoard: {response.get('errorMsg')}")
            except Exception as e:
                print(f"[{DEVICE_NAME}] Lỗi giải mã response: {e}")
            done = True
            client.disconnect()

    provision_client.on_connect = on_connect
    provision_client.on_message = on_message

    print(f"[{DEVICE_NAME}] Đang gửi yêu cầu Auto-Provisioning tới {THINGSBOARD_HOST}:{PORT}...")
    try:
        provision_client.connect(THINGSBOARD_HOST, PORT, 60)
        provision_client.loop_start()
        wait_seconds = 0
        while not done and wait_seconds < 15:
            time.sleep(1)
            wait_seconds += 1
        provision_client.loop_stop()
        provision_client.disconnect()
    except Exception as e:
        print(f"[{DEVICE_NAME}] Không thể kết nối tới ThingsBoard: {e}")

    return token


def run_simulation(token):
    client = mqtt.Client()
    client.username_pw_set(token)

    try:
        client.connect(THINGSBOARD_HOST, PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"[{DEVICE_NAME}] Lỗi kết nối MQTT: {e}")
        return

    print(f"[{DEVICE_NAME}] Đã kích hoạt trạm quan trắc #{assigned_station['node_num']:02d}: "
          f"{assigned_station['station_node']} (Tuyến {assigned_station['road_name']}, {assigned_station['district']})")

    while True:
        # Cảm biến cố định tại trạm, có sai số vi mô tự nhiên của GPS (+- 1~2 mét)
        curr_lat = station_lat + random.uniform(-0.00002, 0.00002)
        curr_lon = station_lon + random.uniform(-0.00002, 0.00002)

        # Mực nước biến động thực tế quanh mức đo chuẩn của trạm
        fluctuation = (random.random() - 0.5) * 5.0
        water_level = round(max(5.0, assigned_station["base_water"] + fluctuation), 1)

        rainfall = round(random.uniform(15.0, 42.0), 1)
        temperature = round(random.uniform(28.0, 31.8), 1)

        # Phân loại độ sâu chuẩn: <20cm: SAFE, 20-35cm: ALERT, 35-50cm: WARNING, >=50cm: CRITICAL
        if water_level >= 50.0:
            status = "CRITICAL"
        elif water_level >= 35.0:
            status = "WARNING"
        elif water_level >= 20.0:
            status = "ALERT"
        else:
            status = "SAFE"

        payload = {
            "device_name": DEVICE_NAME,
            "road_id": assigned_station["road_id"],
            "road_name": assigned_station["road_name"],
            "station_node": assigned_station["station_node"],
            "segment_idx": assigned_station["segment_idx"],
            "district": assigned_station["district"],
            "latitude": round(curr_lat, 5),
            "longitude": round(curr_lon, 5),
            "speed": 0.0,
            "temperature_c": temperature,
            "water_level_cm": water_level,
            "rainfall_mm": rainfall,
            "status": status
        }

        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"[{DEVICE_NAME}] Trạm #{assigned_station['node_num']:02d} [{assigned_station['station_node']}] "
              f"-> Nước: {water_level}cm [{status}] | Mưa: {rainfall}mm | ({payload['latitude']}, {payload['longitude']})")

        time.sleep(random.uniform(3, 5))


if __name__ == "__main__":
    token = None
    if ACCESS_TOKEN:
        print(f"[{DEVICE_NAME}] Sử dụng trực tiếp ACCESS_TOKEN đã cấu hình.")
        token = ACCESS_TOKEN
    elif PROVISION_KEY and PROVISION_SECRET:
        token = provision_device()
    else:
        print("LỖI: Vui lòng cung cấp ACCESS_TOKEN hoặc cả bộ (PROVISION_KEY & PROVISION_SECRET)")
        exit(1)

    if token:
        run_simulation(token)
    else:
        print(f"[{DEVICE_NAME}] Dừng mô phỏng do không lấy được token.")
