import React, { useState, useEffect } from 'react';
import FloodMap from './components/FloodMap';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';

// 10 ĐIỂM NGẬP TRỌNG ĐIỂM TP.HCM
const HOTSPOTS_INITIAL = [
  { id: 'loc-1', name: 'Huỳnh Tấn Phát', district: 'Quận 7', water_level_m: 1.68, severity: 'CRITICAL', minutes_ago: 2, latitude: 10.7412, longitude: 106.7285 },
  { id: 'loc-2', name: 'Trần Xuân Soạn', district: 'Quận 7', water_level_m: 1.52, severity: 'CRITICAL', minutes_ago: 5, latitude: 10.7550, longitude: 106.7120 },
  { id: 'loc-3', name: 'Quốc Hương - Thảo Điền', district: 'TP. Thủ Đức', water_level_m: 1.58, severity: 'CRITICAL', minutes_ago: 4, latitude: 10.8035, longitude: 106.7321 },
  { id: 'loc-4', name: 'Chợ Thủ Đức (Đặng Thị Rành)', district: 'TP. Thủ Đức', water_level_m: 1.75, severity: 'CRITICAL', minutes_ago: 3, latitude: 10.8525, longitude: 106.7582 },
  { id: 'loc-5', name: 'Nguyễn Hữu Cảnh', district: 'Bình Thạnh', water_level_m: 1.45, severity: 'CRITICAL', minutes_ago: 7, latitude: 10.7950, longitude: 106.7150 },
  { id: 'loc-6', name: 'Ung Văn Khiêm - Đinh Bộ Lĩnh', district: 'Bình Thạnh', water_level_m: 1.32, severity: 'WARNING', minutes_ago: 9, latitude: 10.8120, longitude: 106.7110 },
  { id: 'loc-7', name: 'Lê Đức Thọ - Nguyễn Văn Khối', district: 'Gò Vấp', water_level_m: 1.48, severity: 'CRITICAL', minutes_ago: 6, latitude: 10.8350, longitude: 106.6720 },
  { id: 'loc-8', name: 'Phan Huy Ích - Phạm Văn Chiêu', district: 'Gò Vấp', water_level_m: 1.38, severity: 'WARNING', minutes_ago: 8, latitude: 10.8285, longitude: 106.6390 },
  { id: 'loc-9', name: 'Nguyễn Văn Quá - QL22', district: 'Quận 12', water_level_m: 1.42, severity: 'CRITICAL', minutes_ago: 5, latitude: 10.8465, longitude: 106.6210 },
  { id: 'loc-10', name: 'Hồ Học Lãm - An Dương Vương', district: 'Bình Tân', water_level_m: 1.46, severity: 'CRITICAL', minutes_ago: 4, latitude: 10.7180, longitude: 106.6185 }
];

// 50 XE TUẦN TRA PHÂN BỔ ĐỀU 10 ĐIỂM
const DEVICES_INITIAL = Array.from({ length: 50 }, (_, i) => {
  const hs = HOTSPOTS_INITIAL[i % HOTSPOTS_INITIAL.length];
  const water = Number((hs.water_level_m * 28 + (Math.sin(i) * 6)).toFixed(1));
  const isCrit = water >= 40.0;
  const isAlert = water >= 25.0;
  return {
    device_id: `VN-HCM-${String(i + 1).padStart(3, '0')}`,
    name: `Sensor Car ${hs.district.split(' ')[0]}-${String((i % 5) + 1).padStart(2, '0')}`,
    latitude: Number((hs.latitude + Math.sin(i * 1.5) * 0.003).toFixed(5)),
    longitude: Number((hs.longitude + Math.cos(i * 1.5) * 0.003).toFixed(5)),
    water_level_cm: water,
    rainfall_mm: Number((25.0 + Math.sin(i) * 10).toFixed(1)),
    temperature_c: Number((29.5 + Math.cos(i) * 1.5).toFixed(1)),
    status: isCrit ? 'CRITICAL' : (isAlert ? 'ALERT' : 'SAFE'),
    updated_at: new Date().toLocaleTimeString()
  };
});

const INITIAL_DATA = {
  timestamp: new Date().toISOString(),
  summary: {
    safe_count: 18,
    alert_count: 17,
    critical_count: 15,
    avg_water_level_cm: 36.8,
    total_active_devices: 50
  },
  tides: [
    {
      station_id: 'saigon_port',
      name: 'SAIGON RIVER (Port)',
      current_level: 1.45,
      trend: 'UP',
      status: 'HIGH',
      peak_level: 1.55,
      peak_hour: 11,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.9 + 0.55 * Math.sin((h - 5) * Math.PI / 6) + 0.1 * Math.sin((h - 2) * Math.PI / 3)).toFixed(2))
      }))
    },
    {
      station_id: 'nha_be',
      name: 'NHA BE (Dong Dien)',
      current_level: 1.28,
      trend: 'UP',
      status: 'STABLE',
      peak_level: 1.42,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.85 + 0.48 * Math.sin((h - 4.5) * Math.PI / 6) + 0.08 * Math.sin((h - 1.5) * Math.PI / 3)).toFixed(2))
      }))
    },
    {
      station_id: 'nhieu_loc',
      name: 'NHIEU LOC - THI NGHE',
      current_level: 1.22,
      trend: 'UP',
      status: 'STABLE',
      peak_level: 1.36,
      peak_hour: 11,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.75 + 0.42 * Math.sin((h - 5.2) * Math.PI / 6) + 0.09 * Math.sin((h - 2.2) * Math.PI / 3)).toFixed(2))
      }))
    },
    {
      station_id: 'kenh_doi',
      name: 'KENH DOI - KENH TE',
      current_level: 1.38,
      trend: 'UP',
      status: 'HIGH',
      peak_level: 1.48,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.88 + 0.52 * Math.sin((h - 4.8) * Math.PI / 6) + 0.1 * Math.sin((h - 1.8) * Math.PI / 3)).toFixed(2))
      }))
    }
  ],
  severe_locations: HOTSPOTS_INITIAL,
  devices: DEVICES_INITIAL
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
            if (parsed && parsed.devices) {
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
      {/* Fullscreen Map */}
      <FloodMap 
        devices={data.devices} 
        severeLocations={data.severe_locations} 
        selectedLocation={selectedLocation}
      />

      {/* Floating Glassmorphism Sidebar */}
      <Sidebar 
        tides={data.tides} 
        severeLocations={data.severe_locations} 
        summary={data.summary}
        onSelectLocation={(loc) => setSelectedLocation(loc)}
      />

      {/* Floating Top Bar (Live Status & Clock) */}
      <TopBar />
    </div>
  );
}
