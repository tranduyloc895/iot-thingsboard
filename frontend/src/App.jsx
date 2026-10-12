import React, { useState, useEffect } from 'react';
import FloodMap from './components/FloodMap';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';

// 10 TUYẾN ĐƯỜNG NGẬP TRỌNG ĐIỂM TP.HCM
const ROADS_INITIAL = [
  {
    id: 'road-01',
    name: 'Huỳnh Tấn Phát',
    district: 'Quận 7',
    length_km: 4.8,
    severity: 'CRITICAL',
    avg_water_cm: 35.2,
    max_water_cm: 56.0,
    coordinates: [[10.7610, 106.7195], [10.7485, 106.7240], [10.7412, 106.7285], [10.7335, 106.7330], [10.7220, 106.7380]],
    nodes: [
      { id: 'node-01', name: 'Cầu Tân Thuận', latitude: 10.7610, longitude: 106.7195, water_level_cm: 18.0, status: 'SAFE' },
      { id: 'node-02', name: 'Ngã tư Nguyễn Thị Thập', latitude: 10.7485, longitude: 106.7240, water_level_cm: 38.0, status: 'WARNING' },
      { id: 'node-03', name: 'Rốn ngập Trần Trọng Cung', latitude: 10.7412, longitude: 106.7285, water_level_cm: 56.0, status: 'CRITICAL' },
      { id: 'node-04', name: 'Chân cầu Phú Mỹ', latitude: 10.7335, longitude: 106.7330, water_level_cm: 42.0, status: 'WARNING' },
      { id: 'node-05', name: 'Cầu Phú Xuân', latitude: 10.7220, longitude: 106.7380, water_level_cm: 22.0, status: 'ALERT' }
    ]
  },
  {
    id: 'road-02',
    name: 'Trần Xuân Soạn',
    district: 'Quận 7',
    length_km: 3.6,
    severity: 'CRITICAL',
    avg_water_cm: 33.6,
    max_water_cm: 52.0,
    coordinates: [[10.7605, 106.7170], [10.7570, 106.7145], [10.7550, 106.7120], [10.7515, 106.7020], [10.7490, 106.6920]],
    nodes: [
      { id: 'node-06', name: 'Chân cầu Tân Thuận 2', latitude: 10.7605, longitude: 106.7170, water_level_cm: 20.0, status: 'ALERT' },
      { id: 'node-07', name: 'Bờ kè Lâm Văn Bền', latitude: 10.7570, longitude: 106.7145, water_level_cm: 44.0, status: 'WARNING' },
      { id: 'node-08', name: 'Rốn ngập Cầu Kênh Tẻ', latitude: 10.7550, longitude: 106.7120, water_level_cm: 52.0, status: 'CRITICAL' },
      { id: 'node-09', name: 'Cầu Rạch Ông', latitude: 10.7515, longitude: 106.7020, water_level_cm: 36.0, status: 'WARNING' },
      { id: 'node-10', name: 'Chân cầu Chữ Y', latitude: 10.7490, longitude: 106.6920, water_level_cm: 16.0, status: 'SAFE' }
    ]
  },
  {
    id: 'road-03',
    name: 'Quốc Hương - Xuân Thủy',
    district: 'TP. Thủ Đức',
    length_km: 2.9,
    severity: 'CRITICAL',
    avg_water_cm: 33.0,
    max_water_cm: 54.0,
    coordinates: [[10.8015, 106.7380], [10.8030, 106.7345], [10.8035, 106.7321], [10.8075, 106.7300], [10.8120, 106.7280]],
    nodes: [
      { id: 'node-11', name: 'Ngã ba Xa Lộ Hà Nội', latitude: 10.8015, longitude: 106.7380, water_level_cm: 15.0, status: 'SAFE' },
      { id: 'node-12', name: 'Ngã tư Xuân Thủy', latitude: 10.8030, longitude: 106.7345, water_level_cm: 32.0, status: 'ALERT' },
      { id: 'node-13', name: 'Rốn ngập Quốc Hương', latitude: 10.8035, longitude: 106.7321, water_level_cm: 54.0, status: 'CRITICAL' },
      { id: 'node-14', name: 'Trường Quốc tế BIS', latitude: 10.8075, longitude: 106.7300, water_level_cm: 40.0, status: 'WARNING' },
      { id: 'node-15', name: 'Ngã ba Nguyễn Văn Hưởng', latitude: 10.8120, longitude: 106.7280, water_level_cm: 24.0, status: 'ALERT' }
    ]
  },
  {
    id: 'road-04',
    name: 'Kha Vạn Cân - Đặng Thị Rành',
    district: 'TP. Thủ Đức',
    length_km: 2.4,
    severity: 'CRITICAL',
    avg_water_cm: 36.6,
    max_water_cm: 60.0,
    coordinates: [[10.8495, 106.7625], [10.8510, 106.7600], [10.8525, 106.7582], [10.8535, 106.7565], [10.8550, 106.7535]],
    nodes: [
      { id: 'node-16', name: 'Ngã 5 Thủ Đức', latitude: 10.8495, longitude: 106.7625, water_level_cm: 22.0, status: 'ALERT' },
      { id: 'node-17', name: 'Kha Vạn Cân - Dương Văn Cam', latitude: 10.8510, longitude: 106.7600, water_level_cm: 45.0, status: 'WARNING' },
      { id: 'node-18', name: 'Rốn trũng Chợ Thủ Đức', latitude: 10.8525, longitude: 106.7582, water_level_cm: 60.0, status: 'CRITICAL' },
      { id: 'node-19', name: 'Đặng Thị Rành - Tô Ngọc Vân', latitude: 10.8535, longitude: 106.7565, water_level_cm: 38.0, status: 'WARNING' },
      { id: 'node-20', name: 'Cầu Ngang - Võ Văn Ngân', latitude: 10.8550, longitude: 106.7535, water_level_cm: 18.0, status: 'SAFE' }
    ]
  },
  {
    id: 'road-05',
    name: 'Nguyễn Hữu Cảnh',
    district: 'Bình Thạnh',
    length_km: 3.2,
    severity: 'WARNING',
    avg_water_cm: 30.0,
    max_water_cm: 48.0,
    coordinates: [[10.7990, 106.7220], [10.7970, 106.7185], [10.7950, 106.7150], [10.7915, 106.7115], [10.7875, 106.7080]],
    nodes: [
      { id: 'node-21', name: 'Chân Cầu Sài Gòn', latitude: 10.7990, longitude: 106.7220, water_level_cm: 14.0, status: 'SAFE' },
      { id: 'node-22', name: 'The Manor - Landmark 81', latitude: 10.7970, longitude: 106.7185, water_level_cm: 30.0, status: 'ALERT' },
      { id: 'node-23', name: 'Rốn ngập Ung Văn Khiêm', latitude: 10.7950, longitude: 106.7150, water_level_cm: 48.0, status: 'WARNING' },
      { id: 'node-24', name: 'Hầm chui Nguyễn Hữu Cảnh', latitude: 10.7915, longitude: 106.7115, water_level_cm: 42.0, status: 'WARNING' },
      { id: 'node-25', name: 'Chân Cầu Thủ Thiêm 1', latitude: 10.7875, longitude: 106.7080, water_level_cm: 16.0, status: 'SAFE' }
    ]
  },
  {
    id: 'road-06',
    name: 'Ung Văn Khiêm - Đinh Bộ Lĩnh',
    district: 'Bình Thạnh',
    length_km: 2.8,
    severity: 'WARNING',
    avg_water_cm: 29.0,
    max_water_cm: 46.0,
    coordinates: [[10.8010, 106.7115], [10.8080, 106.7110], [10.8120, 106.7110], [10.8145, 106.7125], [10.8120, 106.7160]],
    nodes: [
      { id: 'node-26', name: 'Ngã tư Hàng Xanh', latitude: 10.8010, longitude: 106.7115, water_level_cm: 15.0, status: 'SAFE' },
      { id: 'node-27', name: 'Đinh Bộ Lĩnh - Chu Văn An', latitude: 10.8080, longitude: 106.7110, water_level_cm: 32.0, status: 'ALERT' },
      { id: 'node-28', name: 'Trước Bến xe Miền Đông', latitude: 10.8120, longitude: 106.7110, water_level_cm: 46.0, status: 'WARNING' },
      { id: 'node-29', name: 'Cầu Bình Triệu', latitude: 10.8145, longitude: 106.7125, water_level_cm: 34.0, status: 'ALERT' },
      { id: 'node-30', name: 'Đường D2 (Nguyễn Gia Trí)', latitude: 10.8120, longitude: 106.7160, water_level_cm: 18.0, status: 'SAFE' }
    ]
  },
  {
    id: 'road-07',
    name: 'Lê Đức Thọ - Nguyễn Văn Khối',
    district: 'Gò Vấp',
    length_km: 3.5,
    severity: 'CRITICAL',
    avg_water_cm: 32.6,
    max_water_cm: 54.0,
    coordinates: [[10.8440, 106.6790], [10.8400, 106.6750], [10.8350, 106.6720], [10.8385, 106.6660], [10.8410, 106.6610]],
    nodes: [
      { id: 'node-31', name: 'Ngã 3 Nguyễn Oanh', latitude: 10.8440, longitude: 106.6790, water_level_cm: 16.0, status: 'SAFE' },
      { id: 'node-32', name: 'Lê Đức Thọ - Thống Nhất', latitude: 10.8400, longitude: 106.6750, water_level_cm: 36.0, status: 'WARNING' },
      { id: 'node-33', name: 'Rốn ngập Cây Trâm', latitude: 10.8350, longitude: 106.6720, water_level_cm: 54.0, status: 'CRITICAL' },
      { id: 'node-34', name: 'Công viên Làng Hoa', latitude: 10.8385, longitude: 106.6660, water_level_cm: 38.0, status: 'WARNING' },
      { id: 'node-35', name: 'Nguyễn Văn Khối - Lê Văn Thọ', latitude: 10.8410, longitude: 106.6610, water_level_cm: 19.0, status: 'SAFE' }
    ]
  },
  {
    id: 'road-08',
    name: 'Phan Huy Ích - Phạm Văn Chiêu',
    district: 'Gò Vấp',
    length_km: 3.8,
    severity: 'WARNING',
    avg_water_cm: 30.0,
    max_water_cm: 49.0,
    coordinates: [[10.8380, 106.6510], [10.8335, 106.6450], [10.8285, 106.6390], [10.8250, 106.6320], [10.8210, 106.6265]],
    nodes: [
      { id: 'node-36', name: 'Ngã 3 Quang Trung', latitude: 10.8380, longitude: 106.6510, water_level_cm: 15.0, status: 'SAFE' },
      { id: 'node-37', name: 'Phạm Văn Chiêu - Huỳnh Văn Nghệ', latitude: 10.8335, longitude: 106.6450, water_level_cm: 32.0, status: 'ALERT' },
      { id: 'node-38', name: 'Rốn ngập Cầu Hy Vọng', latitude: 10.8285, longitude: 106.6390, water_level_cm: 49.0, status: 'WARNING' },
      { id: 'node-39', name: 'Cầu Tham Lương', latitude: 10.8250, longitude: 106.6320, water_level_cm: 36.0, status: 'WARNING' },
      { id: 'node-40', name: 'Ngã 3 Trường Chinh', latitude: 10.8210, longitude: 106.6265, water_level_cm: 18.0, status: 'SAFE' }
    ]
  },
  {
    id: 'road-09',
    name: 'Nguyễn Văn Quá',
    district: 'Quận 12',
    length_km: 4.1,
    severity: 'CRITICAL',
    avg_water_cm: 32.4,
    max_water_cm: 53.0,
    coordinates: [[10.8360, 106.6270], [10.8420, 106.6235], [10.8465, 106.6210], [10.8520, 106.6180], [10.8580, 106.6150]],
    nodes: [
      { id: 'node-41', name: 'Cầu Tham Lương - Trường Chinh', latitude: 10.8360, longitude: 106.6270, water_level_cm: 17.0, status: 'SAFE' },
      { id: 'node-42', name: 'Đông Hưng Thuận', latitude: 10.8420, longitude: 106.6235, water_level_cm: 35.0, status: 'WARNING' },
      { id: 'node-43', name: 'Rốn ngập Chợ Cầu', latitude: 10.8465, longitude: 106.6210, water_level_cm: 53.0, status: 'CRITICAL' },
      { id: 'node-44', name: 'Ngã 3 Tô Ký', latitude: 10.8520, longitude: 106.6180, water_level_cm: 37.0, status: 'WARNING' },
      { id: 'node-45', name: 'Ngã ba QL1A Tân Thới Hiệp', latitude: 10.8580, longitude: 106.6150, water_level_cm: 20.0, status: 'ALERT' }
    ]
  },
  {
    id: 'road-10',
    name: 'Hồ Học Lãm - An Dương Vương',
    district: 'Bình Tân',
    length_km: 4.6,
    severity: 'CRITICAL',
    avg_water_cm: 34.8,
    max_water_cm: 55.0,
    coordinates: [[10.7100, 106.6280], [10.7140, 106.6230], [10.7180, 106.6185], [10.7230, 106.6150], [10.7310, 106.6110]],
    nodes: [
      { id: 'node-46', name: 'Bến Phú Định', latitude: 10.7100, longitude: 106.6280, water_level_cm: 22.0, status: 'ALERT' },
      { id: 'node-47', name: 'Cầu Mỹ Thuận', latitude: 10.7140, longitude: 106.6230, water_level_cm: 40.0, status: 'WARNING' },
      { id: 'node-48', name: 'Rốn ngập Hồ Học Lãm', latitude: 10.7180, longitude: 106.6185, water_level_cm: 55.0, status: 'CRITICAL' },
      { id: 'node-49', name: 'Đại lộ Võ Văn Kiệt', latitude: 10.7230, longitude: 106.6150, water_level_cm: 39.0, status: 'WARNING' },
      { id: 'node-50', name: 'Kinh Dương Vương (Vòng xoay An Lạc)', latitude: 10.7310, longitude: 106.6110, water_level_cm: 18.0, status: 'SAFE' }
    ]
  }
];

const INITIAL_DATA = {
  timestamp: new Date().toISOString(),
  summary: {
    safe_count: 14,
    alert_count: 15,
    critical_count: 21,
    avg_water_level_cm: 32.5,
    total_active_devices: 50
  },
  tides: [
    {
      station_id: 'saigon_huynhtanphat',
      name: 'Huỳnh Tấn Phát (Sông Sài Gòn - Q.7)',
      current_level: 1.68,
      trend: 'UP',
      status: 'CRITICAL',
      peak_level: 1.72,
      peak_hour: 11,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((1.0 + 0.65 * Math.sin((h - 5) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'kenhte_tranxuansoan',
      name: 'Trần Xuân Soạn (Kênh Tẻ - Q.7)',
      current_level: 1.52,
      trend: 'UP',
      status: 'CRITICAL',
      peak_level: 1.58,
      peak_hour: 11,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.95 + 0.58 * Math.sin((h - 4.8) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'saigon_thaodien',
      name: 'Thảo Điền (Bán đảo Sài Gòn - Thủ Đức)',
      current_level: 1.58,
      trend: 'UP',
      status: 'CRITICAL',
      peak_level: 1.62,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.98 + 0.60 * Math.sin((h - 4.5) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'rachchot_chothuduc',
      name: 'Chợ Thủ Đức (Lưu vực Rạch Cầu Ngang)',
      current_level: 1.75,
      trend: 'UP',
      status: 'CRITICAL',
      peak_level: 1.78,
      peak_hour: 9,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((1.05 + 0.70 * Math.sin((h - 4) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'vanthanh_nguyenhuucanh',
      name: 'Nguyễn Hữu Cảnh (Rạch Văn Thánh - Bình Thạnh)',
      current_level: 1.45,
      trend: 'UP',
      status: 'HIGH',
      peak_level: 1.50,
      peak_hour: 11,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.90 + 0.55 * Math.sin((h - 5.2) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'saigon_ungvankhiem',
      name: 'Ung Văn Khiêm (Sông Sài Gòn - Bình Thạnh)',
      current_level: 1.32,
      trend: 'UP',
      status: 'WARNING',
      peak_level: 1.38,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.82 + 0.50 * Math.sin((h - 4.7) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'vancot_leductho',
      name: 'Lê Đức Thọ (Lưu vực Tham Lương - Gò Vấp)',
      current_level: 1.48,
      trend: 'UP',
      status: 'HIGH',
      peak_level: 1.52,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.92 + 0.56 * Math.sin((h - 4.6) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'hyvong_phanhuyich',
      name: 'Phan Huy Ích (Kênh Hy Vọng - Tân Bình)',
      current_level: 1.38,
      trend: 'UP',
      status: 'WARNING',
      peak_level: 1.44,
      peak_hour: 9,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.85 + 0.52 * Math.sin((h - 4.2) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'thamluong_nguyenvanqua',
      name: 'Nguyễn Văn Quá (Kênh Tham Lương - Q.12)',
      current_level: 1.42,
      trend: 'UP',
      status: 'HIGH',
      peak_level: 1.46,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.88 + 0.54 * Math.sin((h - 4.5) * Math.PI / 6)).toFixed(2))
      }))
    },
    {
      station_id: 'kenhdoi_hohoclam',
      name: 'Hồ Học Lãm (Kênh Đôi - Bình Tân)',
      current_level: 1.46,
      trend: 'UP',
      status: 'HIGH',
      peak_level: 1.50,
      peak_hour: 11,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.90 + 0.55 * Math.sin((h - 5.0) * Math.PI / 6)).toFixed(2))
      }))
    }
  ],
  severe_locations: ROADS_INITIAL.map((r, i) => ({
    id: `loc-${i + 1}`,
    name: r.name,
    district: r.district,
    water_level_m: Number((r.max_water_cm / 100).toFixed(2)),
    severity: r.severity,
    minutes_ago: 3,
    latitude: r.nodes[2].latitude,
    longitude: r.nodes[2].longitude
  })),
  devices: [],
  roads: ROADS_INITIAL
};

export default function App() {
  const [data, setData] = useState(INITIAL_DATA);
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    const host = window.location.hostname || 'localhost';
    const isLocalDev = window.location.port === '5173' || window.location.port === '3000';
    const wsUrl = isLocalDev 
      ? `ws://${host}:8000/ws/live` 
      : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/live`;

    let ws = null;
    let reconnectTimeout = null;

    const connectWS = () => {
      try {
        ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed && (parsed.devices || parsed.roads)) {
              setData(parsed);
            }
          } catch (e) {
            console.error('Failed to parse WS data:', e);
          }
        };

        ws.onerror = () => {
          ws?.close();
        };

        ws.onclose = () => {
          reconnectTimeout = setTimeout(connectWS, 4000);
        };
      } catch (e) {
        reconnectTimeout = setTimeout(connectWS, 4000);
      }
    };

    connectWS();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Fullscreen High-Contrast Neon Map */}
      <FloodMap 
        devices={data.devices} 
        severeLocations={data.severe_locations} 
        roads={data.roads || []}
        selectedLocation={selectedLocation}
      />

      {/* Floating Glassmorphism Sidebar (10 Charts & 10 Roads) */}
      <Sidebar 
        tides={data.tides} 
        severeLocations={data.severe_locations} 
        roads={data.roads || []}
        summary={data.summary}
        onSelectLocation={(loc) => setSelectedLocation(loc)}
      />

      {/* Floating Top Bar (Live Status & Clock) */}
      <TopBar />
    </div>
  );
}
