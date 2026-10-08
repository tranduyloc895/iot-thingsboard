import time
import json
import random
import paho.mqtt.client as mqtt

# ==========================================
# CẤU HÌNH THINGSBOARD (Vui lòng thay đổi)
# ==========================================
THINGSBOARD_HOST = "IP_LOAD_BALANCER_CUA_BAN"
ACCESS_TOKEN = "ACCESS_TOKEN_CUA_DEVICE"
PORT = 1883

# ==========================================
# KHỞI TẠO MQTT CLIENT
# ==========================================
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# Kết nối đến ThingsBoard
try:
    print(f"Đang kết nối đến ThingsBoard tại {THINGSBOARD_HOST}:{PORT}...")
    client.connect(THINGSBOARD_HOST, PORT, 60)
    print("Kết nối thành công!")
except Exception as e:
    print(f"Lỗi kết nối: {e}")
    exit(1)

client.loop_start()

# ==========================================
# VÒNG LẶP GỬI DỮ LIỆU
# ==========================================
try:
    while True:
        # Giả lập dữ liệu thời tiết và ngập lụt
        water_level = random.uniform(20.0, 60.0) # Mực nước (cm)
        rainfall = random.uniform(0.0, 30.0)     # Lượng mưa (mm)
        temperature = random.uniform(28.0, 35.0) # Nhiệt độ (độ C)
        
        # Xác định trạng thái cảnh báo
        status = "normal"
        if water_level > 50 or rainfall > 20:
            status = "warning"
            
        payload = {
            "water_level_cm": round(water_level, 2),
            "rainfall_mm": round(rainfall, 2),
            "temperature_c": round(temperature, 2),
            "status": status
        }
        
        # Gửi dữ liệu telemetry lên ThingsBoard
        client.publish("v1/devices/me/telemetry", json.dumps(payload))
        print(f"Đã gửi: {payload}")
        
        # Chờ 3 giây trước khi gửi tiếp
        time.sleep(3)
        
except KeyboardInterrupt:
    print("\nĐã dừng mô phỏng.")
    client.loop_stop()
    client.disconnect()
