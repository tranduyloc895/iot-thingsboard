import time
import json
import random
import os
import socket
import paho.mqtt.client as mqtt

# ==========================================
# CẤU HÌNH BIẾN MÔI TRƯỜNG
# ==========================================
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "10.0.0.225")
PORT = int(os.getenv("PORT", "1883"))
PROVISION_KEY = os.getenv("PROVISION_KEY", "")
PROVISION_SECRET = os.getenv("PROVISION_SECRET", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
# Lấy hostname của container để đảm bảo 20 container không bị trùng tên thiết bị
CONTAINER_ID = socket.gethostname()[-6:] if len(socket.gethostname()) >= 6 else socket.gethostname()
DEVICE_NAME = os.getenv("DEVICE_NAME", f"HCM_Vehicle_{CONTAINER_ID}_{random.randint(100,999)}")

# Tọa độ trung tâm TPHCM (Chợ Bến Thành)
CENTER_LAT = 10.7725
CENTER_LON = 106.6980
# Ngẫu nhiên vị trí khởi đầu
lat = CENTER_LAT + random.uniform(-0.05, 0.05)
lon = CENTER_LON + random.uniform(-0.05, 0.05)

def provision_device():
    provision_client = mqtt.Client()
    token = None
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe("/provision/response")
            payload = {
                "deviceName": DEVICE_NAME,
                "provisionDeviceKey": PROVISION_KEY,
                "provisionDeviceSecret": PROVISION_SECRET
            }
            client.publish("/provision/request", json.dumps(payload))

    def on_message(client, userdata, msg):
        nonlocal token
        if msg.topic == "/provision/response":
            response = json.loads(msg.payload.decode())
            if response.get("status") == "SUCCESS":
                token = response.get("credentialsValue")
                print(f"[{DEVICE_NAME}] Đăng ký thành công! Token: {token}")
            else:
                print(f"[{DEVICE_NAME}] Lỗi đăng ký: {response.get('errorMsg')}")
            client.disconnect()

    provision_client.on_connect = on_connect
    provision_client.on_message = on_message
    
    print(f"[{DEVICE_NAME}] Đang gửi yêu cầu Auto-Provisioning...")
    provision_client.connect(THINGSBOARD_HOST, PORT, 60)
    provision_client.loop_forever()
    
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
    print(f"[{DEVICE_NAME}] Bắt đầu chạy vòng lặp gửi data...")
    
    while True:
        # Di chuyển ngẫu nhiên
        lat += random.uniform(-0.0005, 0.0005)
        lon += random.uniform(-0.0005, 0.0005)
        speed = random.uniform(20.0, 60.0)
        water_level = random.uniform(15.0, 75.0)
        rainfall = random.uniform(5.0, 40.0)
        temperature = random.uniform(28.0, 35.0)
        
        payload = {
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "speed": round(speed, 1),
            "temperature_c": round(temperature, 1),
            "water_level_cm": round(water_level, 1),
            "rainfall_mm": round(rainfall, 1),
            "status": "warning" if water_level > 55 else ("moving" if speed > 30 else "normal")
        }
        
        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"[{DEVICE_NAME}] Data: Nước={payload['water_level_cm']}cm | Mưa={payload['rainfall_mm']}mm | Tọa độ=({payload['latitude']}, {payload['longitude']})")
        
        time.sleep(random.uniform(3, 5))

if __name__ == "__main__":
    token = None
    if ACCESS_TOKEN:
        print(f"[{DEVICE_NAME}] Sử dụng trực tiếp ACCESS_TOKEN đã cấu hình.")
        token = ACCESS_TOKEN
    elif PROVISION_KEY and PROVISION_SECRET:
        # 1. Đăng ký qua Auto-Provisioning để lấy token
        token = provision_device()
    else:
        print("LỖI: Vui lòng cung cấp ACCESS_TOKEN hoặc cả bộ (PROVISION_KEY & PROVISION_SECRET)")
        exit(1)
        
    if token:
        # 2. Bắt đầu gửi data
        run_simulation(token)
    else:
        print(f"[{DEVICE_NAME}] Dừng mô phỏng do không lấy được token.")
