import time
import json
import random
import os
import threading
import secrets
from pathlib import Path
import paho.mqtt.client as mqtt

# ==============================================================================
# 50 TRẠM QUAN TRẮC IoT CỐ ĐỊNH (30 TRẠM TUYẾN ĐƯỜNG + 20 TRẠM KHU VỰC NGẬP)
# ==============================================================================
ALL_50_STATIONS = [
    {
        "node_num": 1,
        "device_id": "VN-HCM-001",
        "device_name": "Sensor Station 01 (Ngã ba Trường Chinh)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Ngã ba Trường Chinh",
        "segment_idx": 0,
        "lat": 10.82346,
        "lon": 106.62943,
        "latitude": 10.82346,
        "longitude": 106.62943,
        "base_water": 20.8,
        "water_level_cm": 20.8,
        "status": "ALERT"
    },
    {
        "node_num": 2,
        "device_id": "VN-HCM-002",
        "device_name": "Sensor Station 02 (Đoạn giao Tây Thạnh)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Đoạn giao Tây Thạnh",
        "segment_idx": 1,
        "lat": 10.82712,
        "lon": 106.6315,
        "latitude": 10.82712,
        "longitude": 106.6315,
        "base_water": 39.0,
        "water_level_cm": 39.0,
        "status": "WARNING"
    },
    {
        "node_num": 3,
        "device_id": "VN-HCM-003",
        "device_name": "Sensor Station 03 (Rốn ngập Cầu Hy Vọng)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Rốn ngập Cầu Hy Vọng",
        "segment_idx": 2,
        "lat": 10.83283,
        "lon": 106.63422,
        "latitude": 10.83283,
        "longitude": 106.63422,
        "base_water": 52.0,
        "water_level_cm": 52.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 4,
        "device_id": "VN-HCM-004",
        "device_name": "Sensor Station 04 (Đoạn giao Huỳnh Văn Nghệ)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Đoạn giao Huỳnh Văn Nghệ",
        "segment_idx": 3,
        "lat": 10.83905,
        "lon": 106.63708,
        "latitude": 10.83905,
        "longitude": 106.63708,
        "base_water": 41.6,
        "water_level_cm": 41.6,
        "status": "WARNING"
    },
    {
        "node_num": 5,
        "device_id": "VN-HCM-005",
        "device_name": "Sensor Station 05 (Ngã ba Quang Trung)",
        "parent_id": "road-01",
        "parent_name": "Đường Phan Huy Ích",
        "parent_type": "ROAD",
        "district": "Gò Vấp - Tân Bình",
        "station_node": "Ngã ba Quang Trung",
        "segment_idx": 4,
        "lat": 10.84429,
        "lon": 106.64011,
        "latitude": 10.84429,
        "longitude": 106.64011,
        "base_water": 23.4,
        "water_level_cm": 23.4,
        "status": "ALERT"
    },
    {
        "node_num": 6,
        "device_id": "VN-HCM-006",
        "device_name": "Sensor Station 06 (Cầu Tham Lương - Trường Chinh)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Cầu Tham Lương - Trường Chinh",
        "segment_idx": 0,
        "lat": 10.82783,
        "lon": 106.62674,
        "latitude": 10.82783,
        "longitude": 106.62674,
        "base_water": 20.0,
        "water_level_cm": 20.0,
        "status": "ALERT"
    },
    {
        "node_num": 7,
        "device_id": "VN-HCM-007",
        "device_name": "Sensor Station 07 (Giao lộ Đông Hưng Thuận)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Giao lộ Đông Hưng Thuận",
        "segment_idx": 1,
        "lat": 10.83544,
        "lon": 106.62882,
        "latitude": 10.83544,
        "longitude": 106.62882,
        "base_water": 37.5,
        "water_level_cm": 37.5,
        "status": "WARNING"
    },
    {
        "node_num": 8,
        "device_id": "VN-HCM-008",
        "device_name": "Sensor Station 08 (Rốn ngập Chợ Cầu)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Rốn ngập Chợ Cầu",
        "segment_idx": 2,
        "lat": 10.84278,
        "lon": 106.63091,
        "latitude": 10.84278,
        "longitude": 106.63091,
        "base_water": 50.0,
        "water_level_cm": 50.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 9,
        "device_id": "VN-HCM-009",
        "device_name": "Sensor Station 09 (Đoạn giao Tô Ký)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Đoạn giao Tô Ký",
        "segment_idx": 3,
        "lat": 10.84979,
        "lon": 106.63654,
        "latitude": 10.84979,
        "longitude": 106.63654,
        "base_water": 40.0,
        "water_level_cm": 40.0,
        "status": "WARNING"
    },
    {
        "node_num": 10,
        "device_id": "VN-HCM-010",
        "device_name": "Sensor Station 10 (Ngã ba QL1A Tân Thới Hiệp)",
        "parent_id": "road-02",
        "parent_name": "Đường Nguyễn Văn Quá",
        "parent_type": "ROAD",
        "district": "Quận 12",
        "station_node": "Ngã ba QL1A Tân Thới Hiệp",
        "segment_idx": 4,
        "lat": 10.85647,
        "lon": 106.63941,
        "latitude": 10.85647,
        "longitude": 106.63941,
        "base_water": 22.5,
        "water_level_cm": 22.5,
        "status": "ALERT"
    },
    {
        "node_num": 11,
        "device_id": "VN-HCM-011",
        "device_name": "Sensor Station 11 (Chân cầu Tân Thuận)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Tân Thuận",
        "segment_idx": 0,
        "lat": 10.73791,
        "lon": 106.73034,
        "latitude": 10.73791,
        "longitude": 106.73034,
        "base_water": 22.4,
        "water_level_cm": 22.4,
        "status": "ALERT"
    },
    {
        "node_num": 12,
        "device_id": "VN-HCM-012",
        "device_name": "Sensor Station 12 (Ngã tư Nguyễn Thị Thập)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Ngã tư Nguyễn Thị Thập",
        "segment_idx": 1,
        "lat": 10.74141,
        "lon": 106.7298,
        "latitude": 10.74141,
        "longitude": 106.7298,
        "base_water": 42.0,
        "water_level_cm": 42.0,
        "status": "WARNING"
    },
    {
        "node_num": 13,
        "device_id": "VN-HCM-013",
        "device_name": "Sensor Station 13 (Rốn ngập Trần Trọng Cung)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Rốn ngập Trần Trọng Cung",
        "segment_idx": 2,
        "lat": 10.74375,
        "lon": 106.72954,
        "latitude": 10.74375,
        "longitude": 106.72954,
        "base_water": 56.0,
        "water_level_cm": 56.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 14,
        "device_id": "VN-HCM-014",
        "device_name": "Sensor Station 14 (Chân cầu Phú Mỹ)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Phú Mỹ",
        "segment_idx": 3,
        "lat": 10.74832,
        "lon": 106.72887,
        "latitude": 10.74832,
        "longitude": 106.72887,
        "base_water": 44.8,
        "water_level_cm": 44.8,
        "status": "WARNING"
    },
    {
        "node_num": 15,
        "device_id": "VN-HCM-015",
        "device_name": "Sensor Station 15 (Chân cầu Phú Xuân)",
        "parent_id": "road-03",
        "parent_name": "Đường Huỳnh Tấn Phát",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Phú Xuân",
        "segment_idx": 4,
        "lat": 10.75265,
        "lon": 106.72855,
        "latitude": 10.75265,
        "longitude": 106.72855,
        "base_water": 25.2,
        "water_level_cm": 25.2,
        "status": "ALERT"
    },
    {
        "node_num": 16,
        "device_id": "VN-HCM-016",
        "device_name": "Sensor Station 16 (Chân cầu Tân Thuận 2)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Tân Thuận 2",
        "segment_idx": 0,
        "lat": 10.75101,
        "lon": 106.69107,
        "latitude": 10.75101,
        "longitude": 106.69107,
        "base_water": 21.2,
        "water_level_cm": 21.2,
        "status": "ALERT"
    },
    {
        "node_num": 17,
        "device_id": "VN-HCM-017",
        "device_name": "Sensor Station 17 (Bờ kè Lâm Văn Bền)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Bờ kè Lâm Văn Bền",
        "segment_idx": 1,
        "lat": 10.75172,
        "lon": 106.69849,
        "latitude": 10.75172,
        "longitude": 106.69849,
        "base_water": 39.8,
        "water_level_cm": 39.8,
        "status": "WARNING"
    },
    {
        "node_num": 18,
        "device_id": "VN-HCM-018",
        "device_name": "Sensor Station 18 (Rốn ngập Cầu Kênh Tẻ)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Rốn ngập Cầu Kênh Tẻ",
        "segment_idx": 2,
        "lat": 10.7518,
        "lon": 106.70669,
        "latitude": 10.7518,
        "longitude": 106.70669,
        "base_water": 53.0,
        "water_level_cm": 53.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 19,
        "device_id": "VN-HCM-019",
        "device_name": "Sensor Station 19 (Chân cầu Rạch Ông)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Rạch Ông",
        "segment_idx": 3,
        "lat": 10.75189,
        "lon": 106.71725,
        "latitude": 10.75189,
        "longitude": 106.71725,
        "base_water": 42.4,
        "water_level_cm": 42.4,
        "status": "WARNING"
    },
    {
        "node_num": 20,
        "device_id": "VN-HCM-020",
        "device_name": "Sensor Station 20 (Chân cầu Chữ Y)",
        "parent_id": "road-04",
        "parent_name": "Đường Trần Xuân Soạn",
        "parent_type": "ROAD",
        "district": "Quận 7",
        "station_node": "Chân cầu Chữ Y",
        "segment_idx": 4,
        "lat": 10.75749,
        "lon": 106.72229,
        "latitude": 10.75749,
        "longitude": 106.72229,
        "base_water": 23.9,
        "water_level_cm": 23.9,
        "status": "ALERT"
    },
    {
        "node_num": 21,
        "device_id": "VN-HCM-021",
        "device_name": "Sensor Station 21 (Chân Cầu Sài Gòn)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Chân Cầu Sài Gòn",
        "segment_idx": 0,
        "lat": 10.79802,
        "lon": 106.7245,
        "latitude": 10.79802,
        "longitude": 106.7245,
        "base_water": 18.4,
        "water_level_cm": 18.4,
        "status": "SAFE"
    },
    {
        "node_num": 22,
        "device_id": "VN-HCM-022",
        "device_name": "Sensor Station 22 (The Manor - Landmark 81)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "The Manor - Landmark 81",
        "segment_idx": 1,
        "lat": 10.78905,
        "lon": 106.71455,
        "latitude": 10.78905,
        "longitude": 106.71455,
        "base_water": 34.5,
        "water_level_cm": 34.5,
        "status": "ALERT"
    },
    {
        "node_num": 23,
        "device_id": "VN-HCM-023",
        "device_name": "Sensor Station 23 (Rốn ngập Ung Văn Khiêm nối dài)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Rốn ngập Ung Văn Khiêm nối dài",
        "segment_idx": 2,
        "lat": 10.78932,
        "lon": 106.71481,
        "latitude": 10.78932,
        "longitude": 106.71481,
        "base_water": 46.0,
        "water_level_cm": 46.0,
        "status": "WARNING"
    },
    {
        "node_num": 24,
        "device_id": "VN-HCM-024",
        "device_name": "Sensor Station 24 (Hầm chui Nguyễn Hữu Cảnh)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Hầm chui Nguyễn Hữu Cảnh",
        "segment_idx": 3,
        "lat": 10.78691,
        "lon": 106.70905,
        "latitude": 10.78691,
        "longitude": 106.70905,
        "base_water": 36.8,
        "water_level_cm": 36.8,
        "status": "WARNING"
    },
    {
        "node_num": 25,
        "device_id": "VN-HCM-025",
        "device_name": "Sensor Station 25 (Chân Cầu Thủ Thiêm 1)",
        "parent_id": "road-05",
        "parent_name": "Đường Nguyễn Hữu Cảnh",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Chân Cầu Thủ Thiêm 1",
        "segment_idx": 4,
        "lat": 10.7868,
        "lon": 106.70936,
        "latitude": 10.7868,
        "longitude": 106.70936,
        "base_water": 20.7,
        "water_level_cm": 20.7,
        "status": "ALERT"
    },
    {
        "node_num": 26,
        "device_id": "VN-HCM-026",
        "device_name": "Sensor Station 26 (Ngã tư Hàng Xanh)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Ngã tư Hàng Xanh",
        "segment_idx": 0,
        "lat": 10.80993,
        "lon": 106.71262,
        "latitude": 10.80993,
        "longitude": 106.71262,
        "base_water": 17.6,
        "water_level_cm": 17.6,
        "status": "SAFE"
    },
    {
        "node_num": 27,
        "device_id": "VN-HCM-027",
        "device_name": "Sensor Station 27 (Đoạn Chu Văn An)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Đoạn Chu Văn An",
        "segment_idx": 1,
        "lat": 10.80781,
        "lon": 106.7159,
        "latitude": 10.80781,
        "longitude": 106.7159,
        "base_water": 33.0,
        "water_level_cm": 33.0,
        "status": "ALERT"
    },
    {
        "node_num": 28,
        "device_id": "VN-HCM-028",
        "device_name": "Sensor Station 28 (Trước Bến xe Miền Đông)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Trước Bến xe Miền Đông",
        "segment_idx": 2,
        "lat": 10.8061,
        "lon": 106.7204,
        "latitude": 10.8061,
        "longitude": 106.7204,
        "base_water": 44.0,
        "water_level_cm": 44.0,
        "status": "WARNING"
    },
    {
        "node_num": 29,
        "device_id": "VN-HCM-029",
        "device_name": "Sensor Station 29 (Chân Cầu Bình Triệu)",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Chân Cầu Bình Triệu",
        "segment_idx": 3,
        "lat": 10.80209,
        "lon": 106.7226,
        "latitude": 10.80209,
        "longitude": 106.7226,
        "base_water": 35.2,
        "water_level_cm": 35.2,
        "status": "WARNING"
    },
    {
        "node_num": 30,
        "device_id": "VN-HCM-030",
        "device_name": "Sensor Station 30 (Ngã ba Đường D2 (Nguyễn Gia Trí))",
        "parent_id": "road-06",
        "parent_name": "Đường Ung Văn Khiêm",
        "parent_type": "ROAD",
        "district": "Bình Thạnh",
        "station_node": "Ngã ba Đường D2 (Nguyễn Gia Trí)",
        "segment_idx": 4,
        "lat": 10.79914,
        "lon": 106.72392,
        "latitude": 10.79914,
        "longitude": 106.72392,
        "base_water": 19.8,
        "water_level_cm": 19.8,
        "status": "SAFE"
    },
    {
        "node_num": 31,
        "device_id": "VN-HCM-031",
        "device_name": "Sensor Station 31 (Cổng vào Xa Lộ Hà Nội - Thảo Điền)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Cổng vào Xa Lộ Hà Nội - Thảo Điền",
        "segment_idx": 0,
        "lat": 10.8015,
        "lon": 106.738,
        "latitude": 10.8015,
        "longitude": 106.738,
        "base_water": 20.0,
        "water_level_cm": 20.0,
        "status": "ALERT"
    },
    {
        "node_num": 32,
        "device_id": "VN-HCM-032",
        "device_name": "Sensor Station 32 (Giao lộ Xuân Thủy - Quốc Hương)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Giao lộ Xuân Thủy - Quốc Hương",
        "segment_idx": 1,
        "lat": 10.803,
        "lon": 106.7345,
        "latitude": 10.803,
        "longitude": 106.7345,
        "base_water": 38.0,
        "water_level_cm": 38.0,
        "status": "WARNING"
    },
    {
        "node_num": 33,
        "device_id": "VN-HCM-033",
        "device_name": "Sensor Station 33 (Rốn ngập trung tâm Quốc Hương)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Rốn ngập trung tâm Quốc Hương",
        "segment_idx": 2,
        "lat": 10.8035,
        "lon": 106.7321,
        "latitude": 10.8035,
        "longitude": 106.7321,
        "base_water": 54.0,
        "water_level_cm": 54.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 34,
        "device_id": "VN-HCM-034",
        "device_name": "Sensor Station 34 (Trường Quốc tế BIS Thảo Điền)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Trường Quốc tế BIS Thảo Điền",
        "segment_idx": 3,
        "lat": 10.8075,
        "lon": 106.73,
        "latitude": 10.8075,
        "longitude": 106.73,
        "base_water": 45.0,
        "water_level_cm": 45.0,
        "status": "WARNING"
    },
    {
        "node_num": 35,
        "device_id": "VN-HCM-035",
        "device_name": "Sensor Station 35 (Bờ kè Nguyễn Văn Hưởng)",
        "parent_id": "zone-01",
        "parent_name": "Khu vực Bán đảo Thảo Điền",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Bờ kè Nguyễn Văn Hưởng",
        "segment_idx": 4,
        "lat": 10.812,
        "lon": 106.728,
        "latitude": 10.812,
        "longitude": 106.728,
        "base_water": 32.0,
        "water_level_cm": 32.0,
        "status": "ALERT"
    },
    {
        "node_num": 36,
        "device_id": "VN-HCM-036",
        "device_name": "Sensor Station 36 (Ngã 5 Thủ Đức - Kha Vạn Cân)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Ngã 5 Thủ Đức - Kha Vạn Cân",
        "segment_idx": 0,
        "lat": 10.8495,
        "lon": 106.7625,
        "latitude": 10.8495,
        "longitude": 106.7625,
        "base_water": 26.0,
        "water_level_cm": 26.0,
        "status": "ALERT"
    },
    {
        "node_num": 37,
        "device_id": "VN-HCM-037",
        "device_name": "Sensor Station 37 (Dốc Dương Văn Cam)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Dốc Dương Văn Cam",
        "segment_idx": 1,
        "lat": 10.851,
        "lon": 106.76,
        "latitude": 10.851,
        "longitude": 106.76,
        "base_water": 48.0,
        "water_level_cm": 48.0,
        "status": "WARNING"
    },
    {
        "node_num": 38,
        "device_id": "VN-HCM-038",
        "device_name": "Sensor Station 38 (Rốn trũng Chợ Thủ Đức)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Rốn trũng Chợ Thủ Đức",
        "segment_idx": 2,
        "lat": 10.8525,
        "lon": 106.7582,
        "latitude": 10.8525,
        "longitude": 106.7582,
        "base_water": 60.0,
        "water_level_cm": 60.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 39,
        "device_id": "VN-HCM-039",
        "device_name": "Sensor Station 39 (Đặng Thị Rành - Tô Ngọc Vân)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Đặng Thị Rành - Tô Ngọc Vân",
        "segment_idx": 3,
        "lat": 10.8535,
        "lon": 106.7565,
        "latitude": 10.8535,
        "longitude": 106.7565,
        "base_water": 42.0,
        "water_level_cm": 42.0,
        "status": "WARNING"
    },
    {
        "node_num": 40,
        "device_id": "VN-HCM-040",
        "device_name": "Sensor Station 40 (Cầu Ngang - Võ Văn Ngân)",
        "parent_id": "zone-02",
        "parent_name": "Khu vực Thung lũng Chợ Thủ Đức",
        "parent_type": "ZONE",
        "district": "TP. Thủ Đức",
        "station_node": "Cầu Ngang - Võ Văn Ngân",
        "segment_idx": 4,
        "lat": 10.855,
        "lon": 106.7535,
        "latitude": 10.855,
        "longitude": 106.7535,
        "base_water": 22.0,
        "water_level_cm": 22.0,
        "status": "ALERT"
    },
    {
        "node_num": 41,
        "device_id": "VN-HCM-041",
        "device_name": "Sensor Station 41 (Ngã ba Nguyễn Oanh - Lê Đức Thọ)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Ngã ba Nguyễn Oanh - Lê Đức Thọ",
        "segment_idx": 0,
        "lat": 10.844,
        "lon": 106.679,
        "latitude": 10.844,
        "longitude": 106.679,
        "base_water": 20.0,
        "water_level_cm": 20.0,
        "status": "ALERT"
    },
    {
        "node_num": 42,
        "device_id": "VN-HCM-042",
        "device_name": "Sensor Station 42 (Lê Đức Thọ - Thống Nhất)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Lê Đức Thọ - Thống Nhất",
        "segment_idx": 1,
        "lat": 10.84,
        "lon": 106.675,
        "latitude": 10.84,
        "longitude": 106.675,
        "base_water": 36.0,
        "water_level_cm": 36.0,
        "status": "WARNING"
    },
    {
        "node_num": 43,
        "device_id": "VN-HCM-043",
        "device_name": "Sensor Station 43 (Rốn ngập Cây Trâm - Nguyễn Văn Khối)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Rốn ngập Cây Trâm - Nguyễn Văn Khối",
        "segment_idx": 2,
        "lat": 10.835,
        "lon": 106.672,
        "latitude": 10.835,
        "longitude": 106.672,
        "base_water": 52.0,
        "water_level_cm": 52.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 44,
        "device_id": "VN-HCM-044",
        "device_name": "Sensor Station 44 (Khu vực Công viên Làng Hoa)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Khu vực Công viên Làng Hoa",
        "segment_idx": 3,
        "lat": 10.8385,
        "lon": 106.666,
        "latitude": 10.8385,
        "longitude": 106.666,
        "base_water": 42.0,
        "water_level_cm": 42.0,
        "status": "WARNING"
    },
    {
        "node_num": 45,
        "device_id": "VN-HCM-045",
        "device_name": "Sensor Station 45 (Nguyễn Văn Khối - Lê Văn Thọ)",
        "parent_id": "zone-03",
        "parent_name": "Khu vực Trũng thấp Cây Trâm - Làng Hoa",
        "parent_type": "ZONE",
        "district": "Gò Vấp",
        "station_node": "Nguyễn Văn Khối - Lê Văn Thọ",
        "segment_idx": 4,
        "lat": 10.841,
        "lon": 106.661,
        "latitude": 10.841,
        "longitude": 106.661,
        "base_water": 24.0,
        "water_level_cm": 24.0,
        "status": "ALERT"
    },
    {
        "node_num": 46,
        "device_id": "VN-HCM-046",
        "device_name": "Sensor Station 46 (Bờ kè Bến Phú Định)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Bờ kè Bến Phú Định",
        "segment_idx": 0,
        "lat": 10.71,
        "lon": 106.628,
        "latitude": 10.71,
        "longitude": 106.628,
        "base_water": 28.0,
        "water_level_cm": 28.0,
        "status": "ALERT"
    },
    {
        "node_num": 47,
        "device_id": "VN-HCM-047",
        "device_name": "Sensor Station 47 (Cầu Mỹ Thuận - An Dương Vương)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Cầu Mỹ Thuận - An Dương Vương",
        "segment_idx": 1,
        "lat": 10.714,
        "lon": 106.623,
        "latitude": 10.714,
        "longitude": 106.623,
        "base_water": 44.0,
        "water_level_cm": 44.0,
        "status": "WARNING"
    },
    {
        "node_num": 48,
        "device_id": "VN-HCM-048",
        "device_name": "Sensor Station 48 (Rốn ngập Hồ Học Lãm)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Rốn ngập Hồ Học Lãm",
        "segment_idx": 2,
        "lat": 10.718,
        "lon": 106.6185,
        "latitude": 10.718,
        "longitude": 106.6185,
        "base_water": 55.0,
        "water_level_cm": 55.0,
        "status": "CRITICAL"
    },
    {
        "node_num": 49,
        "device_id": "VN-HCM-049",
        "device_name": "Sensor Station 49 (Nút giao Đại lộ Võ Văn Kiệt)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Nút giao Đại lộ Võ Văn Kiệt",
        "segment_idx": 3,
        "lat": 10.723,
        "lon": 106.615,
        "latitude": 10.723,
        "longitude": 106.615,
        "base_water": 40.0,
        "water_level_cm": 40.0,
        "status": "WARNING"
    },
    {
        "node_num": 50,
        "device_id": "VN-HCM-050",
        "device_name": "Sensor Station 50 (Kinh Dương Vương - Vòng xoay An Lạc)",
        "parent_id": "zone-04",
        "parent_name": "Khu vực Lưu vực Bến Mễ Cốc - Hồ Học Lãm",
        "parent_type": "ZONE",
        "district": "Bình Tân & Q.8",
        "station_node": "Kinh Dương Vương - Vòng xoay An Lạc",
        "segment_idx": 4,
        "lat": 10.731,
        "lon": 106.611,
        "latitude": 10.731,
        "longitude": 106.611,
        "base_water": 22.0,
        "water_level_cm": 22.0,
        "status": "ALERT"
    }
]

# ==========================================
# CẤU HÌNH BIẾN MÔI TRƯỜNG & KẾT NỐI
# ==========================================
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "10.0.1.200")
PORT = int(os.getenv("PORT", "1883"))
PROVISION_KEY = os.getenv("PROVISION_KEY", "")
PROVISION_SECRET = os.getenv("PROVISION_SECRET", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

# Every replica must have an explicit logical station. No hostname hashing.
node_index = os.getenv("NODE_INDEX")
if node_index is None or not node_index.isdigit() or not 0 <= int(node_index) < len(ALL_50_STATIONS):
    raise SystemExit("NODE_INDEX phải nằm trong 0..49 và được cố định cho từng simulator.")
station_idx = int(node_index)
assigned_station = ALL_50_STATIONS[station_idx]
DEVICE_NAME = os.getenv("DEVICE_NAME", assigned_station["device_id"])
if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in DEVICE_NAME):
    raise SystemExit("DEVICE_NAME chứa ký tự không hợp lệ.")
station_lat = assigned_station["lat"]
station_lon = assigned_station["lon"]
STATE_DIR = Path(os.getenv("STATE_DIR", "/state"))
TOKEN_FILE = STATE_DIR / (DEVICE_NAME + ".json")


def load_token():
    try:
        saved = json.loads(TOKEN_FILE.read_text())
        if saved.get("host") == THINGSBOARD_HOST and saved.get("device_name") == DEVICE_NAME:
            return saved.get("token")
    except (OSError, ValueError):
        pass
    return None


def save_token(token):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    temporary = TOKEN_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps({"host": THINGSBOARD_HOST, "device_name": DEVICE_NAME, "token": token}))
    temporary.chmod(0o600)
    temporary.replace(TOKEN_FILE)


def provision_device():
    # Persist a client-chosen token before the one-shot request. If the response
    # is lost after device creation, the next attempt can authenticate with it.
    requested_token = secrets.token_urlsafe(32)
    save_token(requested_token)
    client = mqtt.Client()
    client.username_pw_set("provision")
    completed = threading.Event()
    result = {}

    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print(f"[{DEVICE_NAME}] MQTT provisioning bị từ chối rc={rc}", flush=True)
            completed.set()
        else:
            # ThingsBoard provision-only sessions can ignore SUBSCRIBE/SUBACK.
            # Queue subscribe before publish, but never wait for on_subscribe.
            client.subscribe("/provision/response", qos=1)
            client.publish("/provision/request", json.dumps({
                "deviceName": DEVICE_NAME, "provisionDeviceKey": PROVISION_KEY,
                "provisionDeviceSecret": PROVISION_SECRET,
                "credentialsType": "ACCESS_TOKEN", "token": requested_token}), qos=1)

    def on_message(client, userdata, message):
        try:
            response = json.loads(message.payload.decode())
            if response.get("status") == "SUCCESS":
                result["token"] = response.get("credentialsValue")
            else:
                print(f"[{DEVICE_NAME}] Provisioning lỗi: {response.get('status')}; {response.get('errorMsg', '')}", flush=True)
        except (ValueError, UnicodeDecodeError):
            print(f"[{DEVICE_NAME}] Provisioning response không hợp lệ", flush=True)
        completed.set()

    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(THINGSBOARD_HOST, PORT, 60)
        client.loop_start()
        if not completed.wait(20):
            print(f"[{DEVICE_NAME}] Provisioning timeout", flush=True)
    finally:
        client.disconnect()
        client.loop_stop()
    return result.get("token")


def run_simulation(token):
    client = mqtt.Client()
    client.username_pw_set(token)

    connected = threading.Event()
    auth_failed = threading.Event()
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            connected.set()
        else:
            if rc in (4, 5):
                auth_failed.set()
            print(f"[{DEVICE_NAME}] MQTT connection bị từ chối rc={rc}", flush=True)
    def on_disconnect(client, userdata, rc):
        connected.clear()
        print(f"[{DEVICE_NAME}] MQTT disconnected rc={rc}; đang kết nối lại", flush=True)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect(THINGSBOARD_HOST, PORT, 60)
    client.loop_start()
    if not connected.wait(12):
        client.disconnect()
        client.loop_stop()
        if auth_failed.is_set():
            TOKEN_FILE.unlink(missing_ok=True)
        raise RuntimeError("Không xác thực/kết nối được MQTT trong 12 giây")

    try:
        print(f"[{DEVICE_NAME}] Đã kích hoạt trạm quan trắc #{assigned_station['node_num']:02d}: "
              f"{assigned_station['station_node']} ({assigned_station['parent_type']}: {assigned_station['parent_name']}, {assigned_station['district']})")

        while True:
            if not connected.wait(30):
                client.disconnect()
                client.loop_stop()
                raise RuntimeError("Mất kết nối MQTT quá 30 giây")
            # Cảm biến cố định tại trạm, có sai số vi mô GPS (+- 1~2 mét)
            curr_lat = station_lat + random.uniform(-0.00001, 0.00001)
            curr_lon = station_lon + random.uniform(-0.00001, 0.00001)

            # Mực nước dao động nhẹ quanh mức ngập chuẩn của trạm
            fluctuation = (random.random() - 0.5) * 4.0
            water_level = round(max(5.0, assigned_station["base_water"] + fluctuation), 1)

            rainfall = round(random.uniform(15.0, 42.0), 1)
            temperature = round(random.uniform(28.0, 31.8), 1)

            if water_level >= 50.0:
                status = "CRITICAL"
            elif water_level >= 35.0:
                status = "WARNING"
            elif water_level >= 20.0:
                status = "ALERT"
            else:
                status = "SAFE"

            payload = {
                "device_id": assigned_station["device_id"],
                "source": "simulator",
                "device_name": DEVICE_NAME,
                "parent_id": assigned_station["parent_id"],
                "parent_name": assigned_station["parent_name"],
                "parent_type": assigned_station["parent_type"],
                "road_id": assigned_station["parent_id"] if assigned_station["parent_type"] == "ROAD" else None,
                "road_name": assigned_station["parent_name"] if assigned_station["parent_type"] == "ROAD" else None,
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

            published = client.publish("v1/devices/me/telemetry", json.dumps(payload), qos=1)
            if published.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT publish thất bại rc={published.rc}")
            published.wait_for_publish(timeout=10)
            if not published.is_published():
                raise RuntimeError("MQTT publish chưa nhận PUBACK")
            print(f"[{DEVICE_NAME}] Trạm #{assigned_station['node_num']:02d} [{assigned_station['station_node']}] "
                  f"-> Nước: {water_level}cm [{status}] | Mưa: {rainfall}mm | ({payload['latitude']}, {payload['longitude']})")

            time.sleep(random.uniform(3, 5))
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    delay = 3
    while True:
        try:
            token = ACCESS_TOKEN or load_token()
            if not token:
                if not PROVISION_KEY or not PROVISION_SECRET:
                    raise RuntimeError("Thiếu token đã lưu hoặc PROVISION_KEY/PROVISION_SECRET")
                token = provision_device()
                if not token:
                    raise RuntimeError("Không lấy được token; kiểm tra provisioning profile/credentials")
                save_token(token)
            run_simulation(token)
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"[{DEVICE_NAME}] ERROR: {exc}. Thử lại sau {delay}s", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 60)
