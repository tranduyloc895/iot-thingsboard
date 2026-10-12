import time
import json
import random
import os
import socket
import hashlib
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
        "base_water": 20.8
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
        "base_water": 39.0
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
        "base_water": 52.0
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
        "base_water": 41.6
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
        "base_water": 23.4
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
        "base_water": 20.0
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
        "base_water": 37.5
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
        "base_water": 50.0
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
        "base_water": 40.0
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
        "base_water": 22.5
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
        "base_water": 22.4
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
        "base_water": 42.0
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
        "base_water": 56.0
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
        "base_water": 44.8
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
        "base_water": 25.2
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
        "base_water": 21.2
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
        "base_water": 39.8
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
        "base_water": 53.0
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
        "base_water": 42.4
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
        "base_water": 23.9
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
        "base_water": 18.4
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
        "base_water": 34.5
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
        "base_water": 46.0
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
        "base_water": 36.8
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
        "base_water": 20.7
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
        "base_water": 17.6
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
        "base_water": 33.0
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
        "base_water": 44.0
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
        "base_water": 35.2
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
        "base_water": 19.8
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
        "base_water": 20.0
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
        "base_water": 38.0
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
        "base_water": 54.0
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
        "base_water": 45.0
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
        "base_water": 32.0
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
        "base_water": 26.0
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
        "base_water": 48.0
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
        "base_water": 60.0
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
        "base_water": 42.0
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
        "base_water": 22.0
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
        "base_water": 20.0
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
        "base_water": 36.0
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
        "base_water": 52.0
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
        "base_water": 42.0
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
        "base_water": 24.0
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
        "base_water": 28.0
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
        "base_water": 44.0
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
        "base_water": 55.0
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
        "base_water": 40.0
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
        "base_water": 22.0
    }
]

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
    station_idx = int(os.getenv("NODE_INDEX")) % len(ALL_50_STATIONS)
else:
    seed_val = int(hashlib.md5(HOSTNAME.encode()).hexdigest(), 16)
    station_idx = seed_val % len(ALL_50_STATIONS)

assigned_station = ALL_50_STATIONS[station_idx]
DEVICE_NAME = os.getenv("DEVICE_NAME", f"HCM_Vehicle_{CONTAINER_ID}_{assigned_station['node_num']:02d}")

# Tọa độ cố định tại trạm giao thông / rốn ngập
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
          f"{assigned_station['station_node']} ({assigned_station['parent_type']}: {assigned_station['parent_name']}, {assigned_station['district']})")

    while True:
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
