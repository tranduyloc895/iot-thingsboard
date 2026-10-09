import time
import json
import random
import os
import paho.mqtt.client as mqtt

# ==========================================
# CẤU HÌNH BIẾN MÔI TRƯỜNG
# ==========================================
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "10.0.0.225")
PORT = int(os.getenv("PORT", "1883"))
PROVISION_KEY = os.getenv("PROVISION_KEY", "")
PROVISION_SECRET = os.getenv("PROVISION_SECRET", "")
DEVICE_NAME = os.getenv("DEVICE_NAME", f"HCM_Vehicle_{random.randint(1000,9999)}")

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
        temperature = random.uniform(28.0, 35.0)
        
        payload = {
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "speed": round(speed, 1),
            "temperature": round(temperature, 1),
            "status": "Moving" if speed > 30 else "Slow"
        }
        
        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"[{DEVICE_NAME}] Đã gửi tọa độ: {payload['latitude']}, {payload['longitude']}")
        
        time.sleep(random.uniform(3, 5))

if __name__ == "__main__":
    if not PROVISION_KEY or not PROVISION_SECRET:
        print("LỖI: Chưa cung cấp PROVISION_KEY và PROVISION_SECRET")
        exit(1)
        
    # 1. Đăng ký lấy token
    token = provision_device()
    
    if token:
        # 2. Bắt đầu gửi data
        run_simulation(token)
    else:
        print(f"[{DEVICE_NAME}] Dừng mô phỏng do không lấy được token.")
