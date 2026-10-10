import random
from datetime import datetime
from typing import List, Tuple
from ..models.schemas import DeviceTelemetry, SevereLocation, CitySummary

# 20 điểm ban đầu trên địa bàn TP.HCM (Quận 1, 2/Thủ Đức, 4, 7, Bình Thạnh, 8, Phú Nhuận...)
HOTSPOTS: List[Tuple[str, str, float, float, float]] = [
    ("VN-HCM-001", "Sensor Car D7-01", 10.7412, 106.7285, 48.5),  # Huỳnh Tấn Phát, Q7 - Ngập nặng
    ("VN-HCM-002", "Sensor Car D7-02", 10.7550, 106.7120, 42.0),  # Trần Xuân Soạn, Q7
    ("VN-HCM-003", "Sensor Car D2-01", 10.8035, 106.7321, 38.0),  # Thảo Điền, TP Thủ Đức
    ("VN-HCM-004", "Sensor Car D2-02", 10.8090, 106.7380, 45.2),  # Quốc Hương, Thảo Điền
    ("VN-HCM-005", "Sensor Car D1-01", 10.7670, 106.6925, 24.5),  # Bùi Viện, Q1
    ("VN-HCM-006", "Sensor Car D1-02", 10.7715, 106.7020, 12.0),  # Hàm Nghi, Q1
    ("VN-HCM-007", "Sensor Car BT-01", 10.7950, 106.7150, 36.8),  # Nguyễn Hữu Cảnh, Bình Thạnh
    ("VN-HCM-008", "Sensor Car BT-02", 10.8120, 106.7110, 22.0),  # Ung Văn Khiêm, Bình Thạnh
    ("VN-HCM-009", "Sensor Car D8-01", 10.7380, 106.6710, 39.5),  # Phạm Thế Hiển, Q8
    ("VN-HCM-010", "Sensor Car D4-01", 10.7600, 106.7050, 18.0),  # Đoàn Văn Bơ, Q4
    ("VN-HCM-011", "Sensor Car D5-01", 10.7540, 106.6630, 14.5),  # Trần Hưng Đạo, Q5
    ("VN-HCM-012", "Sensor Car D3-01", 10.7810, 106.6850, 10.0),  # Nam Kỳ Khởi Nghĩa, Q3
    ("VN-HCM-013", "Sensor Car TB-01", 10.7980, 106.6540, 16.0),  # Cộng Hòa, Tân Bình
    ("VN-HCM-014", "Sensor Car PN-01", 10.7990, 106.6820, 11.5),  # Phan Xích Long, Phú Nhuận
    ("VN-HCM-015", "Sensor Car GV-01", 10.8350, 106.6720, 29.0),  # Lê Đức Thọ, Gò Vấp
    ("VN-HCM-016", "Sensor Car TD-01", 10.8520, 106.7550, 15.0),  # Võ Văn Ngân, Thủ Đức
    ("VN-HCM-017", "Sensor Car BCh-01", 10.7020, 106.6020, 31.0), # Quốc Lộ 1A, Bình Chánh
    ("VN-HCM-018", "Sensor Car D12-01", 10.8650, 106.6430, 19.5), # Nguyễn Văn Quá, Q12
    ("VN-HCM-019", "Sensor Car D6-01", 10.7480, 106.6420, 28.0),  # Hậu Giang, Q6
    ("VN-HCM-020", "Sensor Car D10-01", 10.7720, 106.6680, 13.0), # Ba Tháng Hai, Q10
]

class ThingsBoardService:
    def __init__(self):
        # Lưu giữ state tọa độ của 20 xe để chúng di chuyển nhẹ nhàng trên map
        self.vehicles = []
        for dev_id, name, lat, lon, base_water in HOTSPOTS:
            self.vehicles.append({
                "device_id": dev_id,
                "name": name,
                "lat": lat,
                "lon": lon,
                "base_water": base_water
            })

    def get_live_devices(self) -> List[DeviceTelemetry]:
        updated_list = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for v in self.vehicles:
            # Mô phỏng xe di chuyển ngẫu nhiên cự ly nhỏ (như đang chạy thật trên đường)
            v["lat"] += (random.random() - 0.5) * 0.0004
            v["lon"] += (random.random() - 0.5) * 0.0004
            
            # Mực nước biến động nhẹ quanh base_water
            water_val = round(max(5.0, v["base_water"] + (random.random() - 0.5) * 3.0), 1)
            
            if water_val >= 40.0:
                status = "CRITICAL"
            elif water_val >= 25.0:
                status = "ALERT"
            else:
                status = "SAFE"

            updated_list.append(DeviceTelemetry(
                device_id=v["device_id"],
                name=v["name"],
                latitude=round(v["lat"], 5),
                longitude=round(v["lon"], 5),
                water_level_cm=water_val,
                rainfall_mm=round(random.uniform(10.0, 35.0), 1),
                temperature_c=round(random.uniform(28.0, 32.0), 1),
                status=status,
                updated_at=now_str
            ))
        return updated_list

    def get_city_summary(self, devices: List[DeviceTelemetry]) -> CitySummary:
        safe_c = sum(1 for d in devices if d.status == "SAFE")
        alert_c = sum(1 for d in devices if d.status == "ALERT")
        crit_c = sum(1 for d in devices if d.status == "CRITICAL")
        avg_w = round(sum(d.water_level_cm for d in devices) / len(devices), 1) if devices else 0.0
        return CitySummary(
            safe_count=safe_c,
            alert_count=alert_c,
            critical_count=crit_c,
            avg_water_level_cm=avg_w,
            total_active_devices=len(devices)
        )

    @staticmethod
    def get_severe_locations() -> List[SevereLocation]:
        # Khớp chính xác với danh sách các điểm nóng trong bản Mockup HCM Flood Tracker
        return [
            SevereLocation(
                id="loc-1",
                name="Huynh Tan Phat",
                district="District 7",
                water_level_m=1.68,
                severity="CRITICAL",
                minutes_ago=10,
                latitude=10.7412,
                longitude=106.7285
            ),
            SevereLocation(
                id="loc-2",
                name="Thao Dien",
                district="District 2",
                water_level_m=1.35,
                severity="WARNING",
                minutes_ago=8,
                latitude=10.8035,
                longitude=106.7321
            ),
            SevereLocation(
                id="loc-3",
                name="Bui Vien St.",
                district="District 1",
                water_level_m=1.10,
                severity="ALERT",
                minutes_ago=15,
                latitude=10.7670,
                longitude=106.6925
            )
        ]

tb_service = ThingsBoardService()
