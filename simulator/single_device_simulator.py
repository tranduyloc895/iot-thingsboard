import time
import json
import random
import os
import socket
import hashlib
import paho.mqtt.client as mqtt

# ==========================================
# 10 ĐIỂM NGẬP TRỌNG ĐIỂM TP.HCM (THEO SỞ XÂY DỰNG & BÁO CHÍ)
# ==========================================
HOTSPOTS = [
    {
        "id": "HS-01",
        "name": "Huỳnh Tấn Phát",
        "district": "Quận 7",
        "lat": 10.7412,
        "lon": 106.7285,
        "base_water": 52.0,
        "base_rain": 35.0,
        "desc": "Trục ngập triều cường sát sông Sài Gòn & Kênh Tẻ"
    },
    {
        "id": "HS-02",
        "name": "Trần Xuân Soạn",
        "district": "Quận 7",
        "lat": 10.7550,
        "lon": 106.7120,
        "base_water": 45.0,
        "base_rain": 32.0,
        "desc": "Bờ kè kênh Tẻ ngập sâu khi triều cường dâng"
    },
    {
        "id": "HS-03",
        "name": "Quốc Hương - Thảo Điền",
        "district": "TP. Thủ Đức",
        "lat": 10.8035,
        "lon": 106.7321,
        "base_water": 48.0,
        "base_rain": 40.0,
        "desc": "Rốn ngập Thảo Điền ven sông Sài Gòn"
    },
    {
        "id": "HS-04",
        "name": "Chợ Thủ Đức (Đặng Thị Rành - Kha Vạn Cân)",
        "district": "TP. Thủ Đức",
        "lat": 10.8525,
        "lon": 106.7582,
        "base_water": 55.0,
        "base_rain": 45.0,
        "desc": "Thung lũng trũng dốc nước đổ dồn về chợ"
    },
    {
        "id": "HS-05",
        "name": "Nguyễn Hữu Cảnh",
        "district": "Bình Thạnh",
        "lat": 10.7950,
        "lon": 106.7150,
        "base_water": 42.0,
        "base_rain": 36.0,
        "desc": "Điểm trũng lưu vực rạch Văn Thánh"
    },
    {
        "id": "HS-06",
        "name": "Ung Văn Khiêm - Đinh Bộ Lĩnh",
        "district": "Bình Thạnh",
        "lat": 10.8120,
        "lon": 106.7110,
        "base_water": 38.0,
        "base_rain": 30.0,
        "desc": "Khu vực Bến xe Miền Đông cũ sát sông Sài Gòn"
    },
    {
        "id": "HS-07",
        "name": "Lê Đức Thọ - Nguyễn Văn Khối (Cây Trâm)",
        "district": "Gò Vấp",
        "lat": 10.8350,
        "lon": 106.6720,
        "base_water": 46.0,
        "base_rain": 38.0,
        "desc": "Rốn ngập lớn nhất quận Gò Vấp"
    },
    {
        "id": "HS-08",
        "name": "Phan Huy Ích - Phạm Văn Chiêu",
        "district": "Gò Vấp",
        "lat": 10.8285,
        "lon": 106.6390,
        "base_water": 40.0,
        "base_rain": 34.0,
        "desc": "Lưu vực thoát nước Kênh Hy Vọng"
    },
    {
        "id": "HS-09",
        "name": "Nguyễn Văn Quá - Song hành QL22",
        "district": "Quận 12",
        "lat": 10.8465,
        "lon": 106.6210,
        "base_water": 44.0,
        "base_rain": 35.0,
        "desc": "Tuyến ngập sâu kinh điển mùa mưa Quận 12"
    },
    {
        "id": "HS-10",
        "name": "Hồ Học Lãm - An Dương Vương",
        "district": "Bình Tân",
        "lat": 10.7180,
        "lon": 106.6185,
        "base_water": 43.0,
        "base_rain": 28.0,
        "desc": "Điểm trũng Kênh Đôi ngập do triều cường Tây Nam"
    }
]

# ==========================================
# CẤU HÌNH BIẾN MÔI TRƯỜNG
# ==========================================
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "10.0.0.225")
PORT = int(os.getenv("PORT", "1883"))
PROVISION_KEY = os.getenv("PROVISION_KEY", "")
PROVISION_SECRET = os.getenv("PROVISION_SECRET", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

# Lấy container ID để đảm bảo định danh riêng biệt
CONTAINER_ID = socket.gethostname()[-6:] if len(socket.gethostname()) >= 6 else socket.gethostname()
DEVICE_NAME = os.getenv("DEVICE_NAME", f"HCM_Vehicle_{CONTAINER_ID}_{random.randint(100, 999)}")

# Phân bổ đều các xe vào 10 điểm ngập (khoảng 5 xe / điểm ngập khi scale 50 xe)
seed_val = int(hashlib.md5(DEVICE_NAME.encode()).hexdigest(), 16)
assigned_hotspot = HOTSPOTS[seed_val % len(HOTSPOTS)]

# Khởi tạo tọa độ tuần tra tản đều quanh điểm ngập (bán kính thực tế ~600m - 1.2km)
lat = assigned_hotspot["lat"] + random.uniform(-0.008, 0.008)
lon = assigned_hotspot["lon"] + random.uniform(-0.008, 0.008)


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
        # Chờ tối đa 15 giây để nhận token
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

    global lat, lon
    print(f"[{DEVICE_NAME}] Bắt đầu tuần tra tại [{assigned_hotspot['name']} - {assigned_hotspot['district']}]...")

    while True:
        # Xe di chuyển thực tế dọc các tuyến đường quanh điểm ngập
        lat += random.uniform(-0.0003, 0.0003)
        lon += random.uniform(-0.0003, 0.0003)

        # Tính khoảng cách tới tâm ngập để suy ra mức độ ngập
        dist_deg = ((lat - assigned_hotspot["lat"]) ** 2 + (lon - assigned_hotspot["lon"]) ** 2) ** 0.5
        proximity_factor = max(0.55, 1.0 - (dist_deg / 0.008))

        # Mực nước biến động thực tế quanh mức ngập cơ sở
        water_level = round(assigned_hotspot["base_water"] * proximity_factor + random.uniform(-3.5, 4.0), 1)
        water_level = max(5.0, water_level)

        rainfall = round(assigned_hotspot["base_rain"] + random.uniform(-4.0, 6.0), 1)
        temperature = round(random.uniform(28.0, 32.5), 1)
        speed = round(random.uniform(15.0, 45.0) if water_level < 35 else random.uniform(5.0, 18.0), 1)

        if water_level >= 40.0:
            status = "CRITICAL"
        elif water_level >= 25.0:
            status = "ALERT"
        else:
            status = "SAFE"

        payload = {
            "device_name": DEVICE_NAME,
            "hotspot": assigned_hotspot["name"],
            "district": assigned_hotspot["district"],
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "speed": speed,
            "temperature_c": temperature,
            "water_level_cm": water_level,
            "rainfall_mm": rainfall,
            "status": status
        }

        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"[{DEVICE_NAME}] {assigned_hotspot['name']} ({assigned_hotspot['district']}) -> Nước: {water_level}cm [{status}] | Mưa: {rainfall}mm | ({payload['latitude']}, {payload['longitude']})")

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
