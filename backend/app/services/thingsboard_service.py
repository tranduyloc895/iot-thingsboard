import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings
from ..models.schemas import DeviceTelemetry, SevereLocation, CitySummary

# 10 ĐIỂM NGẬP TRỌNG ĐIỂM TP.HCM (KHỚP HOÀN TOÀN VỚI SIMULATOR)
HOTSPOTS_DATA = [
    {
        "id": "loc-1",
        "name": "Huỳnh Tấn Phát",
        "district": "Quận 7",
        "lat": 10.7412,
        "lon": 106.7285,
        "water_level_m": 1.68,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-2",
        "name": "Trần Xuân Soạn",
        "district": "Quận 7",
        "lat": 10.7550,
        "lon": 106.7120,
        "water_level_m": 1.52,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-3",
        "name": "Quốc Hương - Thảo Điền",
        "district": "TP. Thủ Đức",
        "lat": 10.8035,
        "lon": 106.7321,
        "water_level_m": 1.58,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-4",
        "name": "Chợ Thủ Đức (Đặng Thị Rành)",
        "district": "TP. Thủ Đức",
        "lat": 10.8525,
        "lon": 106.7582,
        "water_level_m": 1.75,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-5",
        "name": "Nguyễn Hữu Cảnh",
        "district": "Bình Thạnh",
        "lat": 10.7950,
        "lon": 106.7150,
        "water_level_m": 1.45,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-6",
        "name": "Ung Văn Khiêm - Đinh Bộ Lĩnh",
        "district": "Bình Thạnh",
        "lat": 10.8120,
        "lon": 106.7110,
        "water_level_m": 1.32,
        "severity": "WARNING"
    },
    {
        "id": "loc-7",
        "name": "Lê Đức Thọ - Nguyễn Văn Khối",
        "district": "Gò Vấp",
        "lat": 10.8350,
        "lon": 106.6720,
        "water_level_m": 1.48,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-8",
        "name": "Phan Huy Ích - Phạm Văn Chiêu",
        "district": "Gò Vấp",
        "lat": 10.8285,
        "lon": 106.6390,
        "water_level_m": 1.38,
        "severity": "WARNING"
    },
    {
        "id": "loc-9",
        "name": "Nguyễn Văn Quá - Song hành QL22",
        "district": "Quận 12",
        "lat": 10.8465,
        "lon": 106.6210,
        "water_level_m": 1.42,
        "severity": "CRITICAL"
    },
    {
        "id": "loc-10",
        "name": "Hồ Học Lãm - An Dương Vương",
        "district": "Bình Tân",
        "lat": 10.7180,
        "lon": 106.6185,
        "water_level_m": 1.46,
        "severity": "CRITICAL"
    }
]

class ThingsBoardService:
    def __init__(self):
        self.jwt_token: Optional[str] = None
        self.token_expiry: float = 0
        self.tb_client = httpx.AsyncClient(timeout=4.0)
        self.fallback_vehicles = self._generate_50_patrol_vehicles()

    def _generate_50_patrol_vehicles(self) -> List[Dict[str, Any]]:
        vehicles = []
        for i in range(50):
            hs = HOTSPOTS_DATA[i % len(HOTSPOTS_DATA)]
            vehicles.append({
                "device_id": f"VN-HCM-{i+1:03d}",
                "name": f"Sensor Car {hs['district'][:3].strip()}-{i//10 + 1:02d}",
                "lat": hs["lat"] + (random.random() - 0.5) * 0.005,
                "lon": hs["lon"] + (random.random() - 0.5) * 0.005,
                "base_water": hs["water_level_m"] * 28.0,
                "hotspot": hs
            })
        return vehicles

    async def _get_auth_token(self) -> Optional[str]:
        if self.jwt_token and time.time() < self.token_expiry:
            return self.jwt_token

        urls_to_try = [
            settings.THINGSBOARD_URL,
            "http://thingsboard-node.thingsboard.svc.cluster.local:8080",
            "http://10.0.0.225:8080"
        ]

        for base_url in urls_to_try:
            try:
                login_url = f"{base_url.rstrip('/')}/api/auth/login"
                resp = await self.tb_client.post(login_url, json={
                    "username": settings.THINGSBOARD_USERNAME,
                    "password": settings.THINGSBOARD_PASSWORD
                })
                if resp.status_code == 200:
                    data = resp.json()
                    self.jwt_token = data.get("token")
                    self.token_expiry = time.time() + 3600
                    return self.jwt_token
            except Exception:
                continue

        return None

    async def _fetch_devices_from_tb(self) -> Optional[List[DeviceTelemetry]]:
        token = await self._get_auth_token()
        if not token:
            return None

        headers = {"X-Authorization": f"Bearer {token}"}
        base_url = settings.THINGSBOARD_URL.rstrip('/')

        try:
            resp = await self.tb_client.get(
                f"{base_url}/api/tenant/devices?pageSize=100&page=0",
                headers=headers
            )
            if resp.status_code != 200:
                return None

            device_list = resp.json().get("data", [])
            if not device_list:
                return None

            results: List[DeviceTelemetry] = []
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for dev in device_list:
                dev_id = dev["id"]["id"]
                dev_name = dev["name"]

                # Lấy telemetry mới nhất
                telemetry_resp = await self.tb_client.get(
                    f"{base_url}/api/plugins/telemetry/DEVICE/{dev_id}/values/timeseries",
                    headers=headers
                )
                
                lat, lon, water, rain, temp, status = 10.7725, 106.6980, 20.0, 15.0, 30.0, "SAFE"
                if telemetry_resp.status_code == 200:
                    t_data = telemetry_resp.json()
                    if "latitude" in t_data:
                        lat = float(t_data["latitude"][0]["value"])
                    if "longitude" in t_data:
                        lon = float(t_data["longitude"][0]["value"])
                    if "water_level_cm" in t_data:
                        water = float(t_data["water_level_cm"][0]["value"])
                    if "rainfall_mm" in t_data:
                        rain = float(t_data["rainfall_mm"][0]["value"])
                    if "temperature_c" in t_data:
                        temp = float(t_data["temperature_c"][0]["value"])
                    if "status" in t_data:
                        status = str(t_data["status"][0]["value"]).upper()
                    else:
                        status = "CRITICAL" if water >= 40.0 else ("ALERT" if water >= 25.0 else "SAFE")

                results.append(DeviceTelemetry(
                    device_id=dev_id,
                    name=dev_name,
                    latitude=lat,
                    longitude=lon,
                    water_level_cm=round(water, 1),
                    rainfall_mm=round(rain, 1),
                    temperature_c=round(temp, 1),
                    status=status,
                    updated_at=now_str
                ))

            if results:
                return results
        except Exception:
            pass

        return None

    async def get_live_devices(self) -> List[DeviceTelemetry]:
        # 1. Thử lấy từ ThingsBoard REST API
        real_devices = await self._fetch_devices_from_tb()
        if real_devices and len(real_devices) > 0:
            return real_devices

        # 2. Fallback: 50 xe mô phỏng tuần tra 10 điểm ngập
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_list = []

        for v in self.fallback_vehicles:
            v["lat"] += (random.random() - 0.5) * 0.0003
            v["lon"] += (random.random() - 0.5) * 0.0003
            
            water_val = round(max(5.0, v["base_water"] + (random.random() - 0.5) * 3.5), 1)
            status = "CRITICAL" if water_val >= 40.0 else ("ALERT" if water_val >= 25.0 else "SAFE")

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
        # Trả về toàn bộ 10 điểm ngập nóng thực tế của TP.HCM
        return [
            SevereLocation(
                id=hs["id"],
                name=hs["name"],
                district=hs["district"],
                water_level_m=hs["water_level_m"],
                severity=hs["severity"],
                minutes_ago=random.randint(2, 12),
                latitude=hs["lat"],
                longitude=hs["lon"]
            )
            for hs in HOTSPOTS_DATA
        ]

tb_service = ThingsBoardService()
