import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings
from ..models.schemas import DeviceTelemetry, SevereLocation, CitySummary, RoadNode, FloodedRoad

# ==============================================================================
# 10 TUYẾN ĐƯỜNG NGẬP TRỌNG ĐIỂM TP.HCM (MỖI TUYẾN CỐ ĐỊNH 5 TRẠM QUAN TRẮC IoT = 50 TRẠM)
# ==============================================================================
ROADS_DATA = [
    {
        "id": "road-01",
        "name": "Huỳnh Tấn Phát",
        "district": "Quận 7",
        "length_km": 4.8,
        "nodes": [
            {"id": "node-01", "name": "Cầu Tân Thuận", "lat": 10.7610, "lon": 106.7195, "base_water": 18.0},
            {"id": "node-02", "name": "Ngã tư Nguyễn Thị Thập", "lat": 10.7485, "lon": 106.7240, "base_water": 38.0},
            {"id": "node-03", "name": "Rốn ngập Trần Trọng Cung", "lat": 10.7412, "lon": 106.7285, "base_water": 56.0},
            {"id": "node-04", "name": "Chân cầu Phú Mỹ", "lat": 10.7335, "lon": 106.7330, "base_water": 42.0},
            {"id": "node-05", "name": "Cầu Phú Xuân", "lat": 10.7220, "lon": 106.7380, "base_water": 22.0},
        ]
    },
    {
        "id": "road-02",
        "name": "Trần Xuân Soạn",
        "district": "Quận 7",
        "length_km": 3.6,
        "nodes": [
            {"id": "node-06", "name": "Chân cầu Tân Thuận 2", "lat": 10.7605, "lon": 106.7170, "base_water": 20.0},
            {"id": "node-07", "name": "Bờ kè Lâm Văn Bền", "lat": 10.7570, "lon": 106.7145, "base_water": 44.0},
            {"id": "node-08", "name": "Rốn ngập Cầu Kênh Tẻ", "lat": 10.7550, "lon": 106.7120, "base_water": 52.0},
            {"id": "node-09", "name": "Cầu Rạch Ông", "lat": 10.7515, "lon": 106.7020, "base_water": 36.0},
            {"id": "node-10", "name": "Chân cầu Chữ Y", "lat": 10.7490, "lon": 106.6920, "base_water": 16.0},
        ]
    },
    {
        "id": "road-03",
        "name": "Quốc Hương - Xuân Thủy",
        "district": "TP. Thủ Đức",
        "length_km": 2.9,
        "nodes": [
            {"id": "node-11", "name": "Ngã ba Xa Lộ Hà Nội", "lat": 10.8015, "lon": 106.7380, "base_water": 15.0},
            {"id": "node-12", "name": "Ngã tư Xuân Thủy", "lat": 10.8030, "lon": 106.7345, "base_water": 32.0},
            {"id": "node-13", "name": "Rốn ngập Quốc Hương", "lat": 10.8035, "lon": 106.7321, "base_water": 54.0},
            {"id": "node-14", "name": "Trường Quốc tế BIS", "lat": 10.8075, "lon": 106.7300, "base_water": 40.0},
            {"id": "node-15", "name": "Ngã ba Nguyễn Văn Hưởng", "lat": 10.8120, "lon": 106.7280, "base_water": 24.0},
        ]
    },
    {
        "id": "road-04",
        "name": "Kha Vạn Cân - Đặng Thị Rành",
        "district": "TP. Thủ Đức",
        "length_km": 2.4,
        "nodes": [
            {"id": "node-16", "name": "Ngã 5 Thủ Đức", "lat": 10.8495, "lon": 106.7625, "base_water": 22.0},
            {"id": "node-17", "name": "Kha Vạn Cân - Dương Văn Cam", "lat": 10.8510, "lon": 106.7600, "base_water": 45.0},
            {"id": "node-18", "name": "Rốn trũng Chợ Thủ Đức", "lat": 10.8525, "lon": 106.7582, "base_water": 60.0},
            {"id": "node-19", "name": "Đặng Thị Rành - Tô Ngọc Vân", "lat": 10.8535, "lon": 106.7565, "base_water": 38.0},
            {"id": "node-20", "name": "Cầu Ngang - Võ Văn Ngân", "lat": 10.8550, "lon": 106.7535, "base_water": 18.0},
        ]
    },
    {
        "id": "road-05",
        "name": "Nguyễn Hữu Cảnh",
        "district": "Bình Thạnh",
        "length_km": 3.2,
        "nodes": [
            {"id": "node-21", "name": "Chân Cầu Sài Gòn", "lat": 10.7990, "lon": 106.7220, "base_water": 14.0},
            {"id": "node-22", "name": "The Manor - Landmark 81", "lat": 10.7970, "lon": 106.7185, "base_water": 30.0},
            {"id": "node-23", "name": "Rốn ngập Ung Văn Khiêm", "lat": 10.7950, "lon": 106.7150, "base_water": 48.0},
            {"id": "node-24", "name": "Hầm chui Nguyễn Hữu Cảnh", "lat": 10.7915, "lon": 106.7115, "base_water": 42.0},
            {"id": "node-25", "name": "Chân Cầu Thủ Thiêm 1", "lat": 10.7875, "lon": 106.7080, "base_water": 16.0},
        ]
    },
    {
        "id": "road-06",
        "name": "Ung Văn Khiêm - Đinh Bộ Lĩnh",
        "district": "Bình Thạnh",
        "length_km": 2.8,
        "nodes": [
            {"id": "node-26", "name": "Ngã tư Hàng Xanh", "lat": 10.8010, "lon": 106.7115, "base_water": 15.0},
            {"id": "node-27", "name": "Đinh Bộ Lĩnh - Chu Văn An", "lat": 10.8080, "lon": 106.7110, "base_water": 32.0},
            {"id": "node-28", "name": "Trước Bến xe Miền Đông", "lat": 10.8120, "lon": 106.7110, "base_water": 46.0},
            {"id": "node-29", "name": "Cầu Bình Triệu", "lat": 10.8145, "lon": 106.7125, "base_water": 34.0},
            {"id": "node-30", "name": "Đường D2 (Nguyễn Gia Trí)", "lat": 10.8120, "lon": 106.7160, "base_water": 18.0},
        ]
    },
    {
        "id": "road-07",
        "name": "Lê Đức Thọ - Nguyễn Văn Khối",
        "district": "Gò Vấp",
        "length_km": 3.5,
        "nodes": [
            {"id": "node-31", "name": "Ngã 3 Nguyễn Oanh", "lat": 10.8440, "lon": 106.6790, "base_water": 16.0},
            {"id": "node-32", "name": "Lê Đức Thọ - Thống Nhất", "lat": 10.8400, "lon": 106.6750, "base_water": 36.0},
            {"id": "node-33", "name": "Rốn ngập Cây Trâm", "lat": 10.8350, "lon": 106.6720, "base_water": 54.0},
            {"id": "node-34", "name": "Công viên Làng Hoa", "lat": 10.8385, "lon": 106.6660, "base_water": 38.0},
            {"id": "node-35", "name": "Nguyễn Văn Khối - Lê Văn Thọ", "lat": 10.8410, "lon": 106.6610, "base_water": 19.0},
        ]
    },
    {
        "id": "road-08",
        "name": "Phan Huy Ích - Phạm Văn Chiêu",
        "district": "Gò Vấp",
        "length_km": 3.8,
        "nodes": [
            {"id": "node-36", "name": "Ngã 3 Quang Trung", "lat": 10.8380, "lon": 106.6510, "base_water": 15.0},
            {"id": "node-37", "name": "Phạm Văn Chiêu - Huỳnh Văn Nghệ", "lat": 10.8335, "lon": 106.6450, "base_water": 32.0},
            {"id": "node-38", "name": "Rốn ngập Cầu Hy Vọng", "lat": 10.8285, "lon": 106.6390, "base_water": 49.0},
            {"id": "node-39", "name": "Cầu Tham Lương", "lat": 10.8250, "lon": 106.6320, "base_water": 36.0},
            {"id": "node-40", "name": "Ngã 3 Trường Chinh", "lat": 10.8210, "lon": 106.6265, "base_water": 18.0},
        ]
    },
    {
        "id": "road-09",
        "name": "Nguyễn Văn Quá",
        "district": "Quận 12",
        "length_km": 4.1,
        "nodes": [
            {"id": "node-41", "name": "Cầu Tham Lương - Trường Chinh", "lat": 10.8360, "lon": 106.6270, "base_water": 17.0},
            {"id": "node-42", "name": "Đông Hưng Thuận", "lat": 10.8420, "lon": 106.6235, "base_water": 35.0},
            {"id": "node-43", "name": "Rốn ngập Chợ Cầu", "lat": 10.8465, "lon": 106.6210, "base_water": 53.0},
            {"id": "node-44", "name": "Ngã 3 Tô Ký", "lat": 10.8520, "lon": 106.6180, "base_water": 37.0},
            {"id": "node-45", "name": "Ngã ba QL1A Tân Thới Hiệp", "lat": 10.8580, "lon": 106.6150, "base_water": 20.0},
        ]
    },
    {
        "id": "road-10",
        "name": "Hồ Học Lãm - An Dương Vương",
        "district": "Bình Tân",
        "length_km": 4.6,
        "nodes": [
            {"id": "node-46", "name": "Bến Phú Định", "lat": 10.7100, "lon": 106.6280, "base_water": 22.0},
            {"id": "node-47", "name": "Cầu Mỹ Thuận", "lat": 10.7140, "lon": 106.6230, "base_water": 40.0},
            {"id": "node-48", "name": "Rốn ngập Hồ Học Lãm", "lat": 10.7180, "lon": 106.6185, "base_water": 55.0},
            {"id": "node-49", "name": "Đại lộ Võ Văn Kiệt", "lat": 10.7230, "lon": 106.6150, "base_water": 39.0},
            {"id": "node-50", "name": "Kinh Dương Vương (Vòng xoay An Lạc)", "lat": 10.7310, "lon": 106.6110, "base_water": 18.0},
        ]
    }
]

# Flatten danh sách 50 trạm cố định
ALL_FIXED_NODES: List[Dict[str, Any]] = []
for road_idx, road in enumerate(ROADS_DATA):
    for node_idx, node in enumerate(road["nodes"]):
        node_num = road_idx * 5 + node_idx + 1
        ALL_FIXED_NODES.append({
            "device_id": f"VN-HCM-{node_num:03d}",
            "device_name": f"Sensor Node {node_num:02d} ({node['name']})",
            "road_id": road["id"],
            "road_name": road["name"],
            "district": road["district"],
            "station_node": node["name"],
            "segment_idx": node_idx,
            "lat": node["lat"],
            "lon": node["lon"],
            "base_water": node["base_water"]
        })


class ThingsBoardService:
    def __init__(self):
        self.jwt_token: Optional[str] = None
        self.token_expiry: float = 0
        self.tb_client = httpx.AsyncClient(timeout=4.0)

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

            for idx, dev in enumerate(device_list):
                dev_id = dev["id"]["id"]
                dev_name = dev["name"]

                # Tìm node cố định tương ứng theo index hoặc tên
                matched_node = ALL_FIXED_NODES[idx % len(ALL_FIXED_NODES)]

                # Lấy telemetry mới nhất từ ThingsBoard
                lat, lon, water, rain, temp = matched_node["lat"], matched_node["lon"], matched_node["base_water"], 25.0, 30.0
                telemetry_resp = await self.tb_client.get(
                    f"{base_url}/api/plugins/telemetry/DEVICE/{dev_id}/values/timeseries",
                    headers=headers
                )
                
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

                status = "CRITICAL" if water >= 50.0 else ("WARNING" if water >= 35.0 else ("ALERT" if water >= 20.0 else "SAFE"))

                results.append(DeviceTelemetry(
                    device_id=dev_id,
                    name=dev_name,
                    latitude=round(lat, 5),
                    longitude=round(lon, 5),
                    water_level_cm=round(water, 1),
                    rainfall_mm=round(rain, 1),
                    temperature_c=round(temp, 1),
                    status=status,
                    updated_at=now_str,
                    road_id=matched_node["road_id"],
                    road_name=matched_node["road_name"],
                    station_node=matched_node["station_node"],
                    segment_idx=matched_node["segment_idx"]
                ))

            if results:
                return results
        except Exception:
            pass

        return None

    async def get_live_devices(self) -> List[DeviceTelemetry]:
        # 1. Thử lấy từ ThingsBoard REST API
        real_devices = await self._fetch_devices_from_tb()
        if real_devices and len(real_devices) >= 50:
            return real_devices

        # 2. Sinh dữ liệu thời gian thực cho chính xác 50 trạm quan trắc cố định trên 10 tuyến đường
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_list: List[DeviceTelemetry] = []

        for node_info in ALL_FIXED_NODES:
            # Dao động nhẹ mực nước theo thời gian thực (+- 2.5cm)
            fluctuation = (random.random() - 0.5) * 5.0
            water_val = round(max(5.0, node_info["base_water"] + fluctuation), 1)
            
            # Phân loại độ sâu chuẩn: <20cm: SAFE, 20-35cm: ALERT, 35-50cm: WARNING, >=50cm: CRITICAL
            status = "CRITICAL" if water_val >= 50.0 else ("WARNING" if water_val >= 35.0 else ("ALERT" if water_val >= 20.0 else "SAFE"))

            updated_list.append(DeviceTelemetry(
                device_id=node_info["device_id"],
                name=node_info["device_name"],
                latitude=round(node_info["lat"], 5),
                longitude=round(node_info["lon"], 5),
                water_level_cm=water_val,
                rainfall_mm=round(random.uniform(15.0, 45.0), 1),
                temperature_c=round(random.uniform(28.0, 31.5), 1),
                status=status,
                updated_at=now_str,
                road_id=node_info["road_id"],
                road_name=node_info["road_name"],
                station_node=node_info["station_node"],
                segment_idx=node_info["segment_idx"]
            ))

        return updated_list

    def get_city_summary(self, devices: List[DeviceTelemetry]) -> CitySummary:
        safe_c = sum(1 for d in devices if d.status == "SAFE")
        alert_c = sum(1 for d in devices if d.status in ("ALERT", "WARNING"))
        crit_c = sum(1 for d in devices if d.status == "CRITICAL")
        avg_w = round(sum(d.water_level_cm for d in devices) / len(devices), 1) if devices else 0.0
        return CitySummary(
            safe_count=safe_c,
            alert_count=alert_c,
            critical_count=crit_c,
            avg_water_level_cm=avg_w,
            total_active_devices=len(devices)
        )

    def get_flooded_roads(self, devices: List[DeviceTelemetry]) -> List[FloodedRoad]:
        """
        Tổng hợp 10 tuyến đường ngập từ 50 trạm quan trắc IoT cố định.
        Mỗi tuyến gồm 5 nodes nối thành Polyline, phân cấp độ ngập theo mực nước thực tế.
        """
        device_map = {d.device_id: d for d in devices}
        # Fallback map theo (road_id, segment_idx)
        device_by_segment = {(d.road_id, d.segment_idx): d for d in devices if d.road_id and d.segment_idx is not None}

        roads_result: List[FloodedRoad] = []

        for road in ROADS_DATA:
            road_id = road["id"]
            coordinates: List[List[float]] = []
            road_nodes: List[RoadNode] = []
            node_water_levels: List[float] = []

            for idx, n in enumerate(road["nodes"]):
                lat = n["lat"]
                lon = n["lon"]
                coordinates.append([lat, lon])

                # Tìm telemetry tương ứng
                telemetry = device_by_segment.get((road_id, idx))
                if telemetry:
                    w = telemetry.water_level_cm
                    s = telemetry.status
                else:
                    w = n["base_water"]
                    s = "CRITICAL" if w >= 50.0 else ("WARNING" if w >= 35.0 else ("ALERT" if w >= 20.0 else "SAFE"))

                node_water_levels.append(w)
                road_nodes.append(RoadNode(
                    id=n["id"],
                    name=n["name"],
                    latitude=lat,
                    longitude=lon,
                    water_level_cm=round(w, 1),
                    status=s
                ))

            avg_w = round(sum(node_water_levels) / len(node_water_levels), 1) if node_water_levels else 0.0
            max_w = round(max(node_water_levels), 1) if node_water_levels else 0.0

            # Phân cấp mức độ nguy hiểm của tuyến đường dựa vào mực nước max và avg
            if max_w >= 50.0:
                road_severity = "CRITICAL"
            elif max_w >= 35.0:
                road_severity = "WARNING"
            elif max_w >= 20.0:
                road_severity = "ALERT"
            else:
                road_severity = "SAFE"

            roads_result.append(FloodedRoad(
                id=road["id"],
                name=road["name"],
                district=road["district"],
                length_km=road["length_km"],
                severity=road_severity,
                avg_water_cm=avg_w,
                max_water_cm=max_w,
                coordinates=coordinates,
                nodes=road_nodes
            ))

        return roads_result

    @staticmethod
    def get_severe_locations() -> List[SevereLocation]:
        # Trả về 10 tâm điểm ngập tương ứng 10 tuyến đường
        return [
            SevereLocation(
                id=f"loc-{i+1}",
                name=r["name"],
                district=r["district"],
                water_level_m=round(r["nodes"][2]["base_water"] / 100.0, 2), # Node rốn ngập trung tâm
                severity="CRITICAL" if r["nodes"][2]["base_water"] >= 50.0 else "WARNING",
                minutes_ago=random.randint(1, 5),
                latitude=r["nodes"][2]["lat"],
                longitude=r["nodes"][2]["lon"]
            )
            for i, r in enumerate(ROADS_DATA)
        ]


tb_service = ThingsBoardService()
