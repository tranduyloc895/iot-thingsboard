import React, { useState, useEffect } from 'react';
import FloodMap from './components/FloodMap';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import { ROADS_INITIAL, ZONES_INITIAL } from './data/floodData';

// 10 TRẠM THỦY VĂN TƯƠNG ỨNG 6 TUYẾN ĐƯỜNG & 4 KHU VỰC TRỌNG ĐIỂM
const TIDES_INITIAL = [
  {
    station_id: 'saigon_phan_huy_ich',
    name: 'Phan Huy Ích (Kênh Hy Vọng - Gò Vấp)',
    current_level: 1.58,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.65,
    peak_hour: 10,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.95 + 0.62 * Math.sin((h - 4.5) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'tham_luong_nguyen_van_qua',
    name: 'Nguyễn Văn Quá (Kênh Tham Lương - Q.12)',
    current_level: 1.52,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.60,
    peak_hour: 10,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.90 + 0.60 * Math.sin((h - 4.8) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'saigon_huynh_tan_phat',
    name: 'Huỳnh Tấn Phát (Sông Sài Gòn - Q.7)',
    current_level: 1.68,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.74,
    peak_hour: 11,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((1.02 + 0.68 * Math.sin((h - 5) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'kenh_te_tran_xuan_soan',
    name: 'Trần Xuân Soạn (Kênh Tẻ - Q.7)',
    current_level: 1.62,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.68,
    peak_hour: 11,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.98 + 0.64 * Math.sin((h - 4.8) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'van_thanh_nguyen_huu_canh',
    name: 'Nguyễn Hữu Cảnh (Rạch Văn Thánh - Bình Thạnh)',
    current_level: 1.45,
    trend: 'UP',
    status: 'HIGH',
    peak_level: 1.50,
    peak_hour: 11,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.88 + 0.55 * Math.sin((h - 5.2) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'saigon_ung_van_khiem',
    name: 'Ung Văn Khiêm (Sông Sài Gòn - Bình Thạnh)',
    current_level: 1.40,
    trend: 'UP',
    status: 'WARNING',
    peak_level: 1.46,
    peak_hour: 10,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.85 + 0.52 * Math.sin((h - 4.7) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'saigon_thao_dien',
    name: 'Bán đảo Thảo Điền (Sông Sài Gòn - Thủ Đức)',
    current_level: 1.65,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.70,
    peak_hour: 10,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((1.0 + 0.65 * Math.sin((h - 4.5) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'rach_ngang_cho_thu_duc',
    name: 'Chợ Thủ Đức (Lưu vực Rạch Cầu Ngang)',
    current_level: 1.75,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.80,
    peak_hour: 9,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((1.05 + 0.72 * Math.sin((h - 4) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'lang_hoa_cay_tram',
    name: 'Cây Trâm - Làng Hoa (Lưu vực Gò Vấp)',
    current_level: 1.48,
    trend: 'UP',
    status: 'HIGH',
    peak_level: 1.54,
    peak_hour: 10,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.92 + 0.56 * Math.sin((h - 4.6) * Math.PI / 6)).toFixed(2))
    }))
  },
  {
    station_id: 'kenh_doi_ben_me_coc',
    name: 'Bến Mễ Cốc - Hồ Học Lãm (Kênh Đôi - Bình Tân)',
    current_level: 1.56,
    trend: 'UP',
    status: 'CRITICAL',
    peak_level: 1.62,
    peak_hour: 11,
    hourly_data: Array.from({ length: 25 }, (_, h) => ({
      hour: h,
      level: Number((0.96 + 0.60 * Math.sin((h - 5.0) * Math.PI / 6)).toFixed(2))
    }))
  }
];

const INITIAL_DATA = {
  timestamp: new Date().toISOString(),
  summary: {
    safe_count: 12,
    alert_count: 16,
    critical_count: 22,
    avg_water_level_cm: 36.4,
    total_active_devices: 50
  },
  tides: TIDES_INITIAL,
  severe_locations: [
    ...(ROADS_INITIAL || []).map((r, i) => {
      const centerNode = (r.nodes && r.nodes[2]) || (r.nodes && r.nodes[0]) || {};
      const lat = centerNode.latitude ?? centerNode.lat ?? (r.coordinates && r.coordinates[0] && r.coordinates[0][0]) ?? 10.7769;
      const lon = centerNode.longitude ?? centerNode.lon ?? (r.coordinates && r.coordinates[0] && r.coordinates[0][1]) ?? 106.7009;
      const maxW = r.max_water_cm ?? r.base_water ?? 50.0;
      return {
        id: r.id || `road-${i + 1}`,
        name: r.name || 'Tuyến đường',
        district: r.district || 'TP.HCM',
        water_level_m: Number((maxW / 100).toFixed(2)),
        severity: r.severity || 'CRITICAL',
        minutes_ago: 3,
        latitude: lat,
        longitude: lon
      };
    }),
    ...(ZONES_INITIAL || []).map((z, i) => {
      const lat = (z.center && z.center[0]) ?? 10.7769;
      const lon = (z.center && z.center[1]) ?? 106.7009;
      const maxW = z.max_water_cm ?? z.base_water ?? 55.0;
      return {
        id: z.id || `zone-${i + 1}`,
        name: z.name || 'Khu vực ngập',
        district: z.district || 'TP.HCM',
        water_level_m: Number((maxW / 100).toFixed(2)),
        severity: z.severity || 'CRITICAL',
        minutes_ago: 3,
        latitude: lat,
        longitude: lon
      };
    })
  ],
  devices: [],
  roads: ROADS_INITIAL || [],
  zones: ZONES_INITIAL || [],
  weather: null
};

export default function App() {
  const [data, setData] = useState(INITIAL_DATA);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [wsStatus, setWsStatus] = useState('CONNECTING'); // 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED'
  const [lastSyncTime, setLastSyncTime] = useState(null);
  const [packetCount, setPacketCount] = useState(0);
  const [isPinging, setIsPinging] = useState(false);

  useEffect(() => {
    const host = window.location.hostname || 'localhost';
    const isLocalDev = window.location.port === '5173' || window.location.port === '3000';
    const wsUrl = isLocalDev 
      ? `ws://${host}:8000/ws/live` 
      : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/live`;

    let ws = null;
    let reconnectTimeout = null;
    let pingTimeout = null;

    const connectWS = () => {
      try {
        setWsStatus('CONNECTING');
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          setWsStatus('CONNECTED');
        };

        ws.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed && (parsed.devices || parsed.roads || parsed.zones || parsed.summary)) {
              setData(prev => ({
                ...prev,
                ...parsed,
                roads: parsed.roads && parsed.roads.length > 0 ? parsed.roads : prev.roads,
                zones: parsed.zones && parsed.zones.length > 0 ? parsed.zones : prev.zones,
                weather: parsed.weather ?? prev.weather,
                summary: parsed.summary ?? prev.summary
              }));

              if (parsed.timestamp) {
                setLastSyncTime(parsed.timestamp);
              } else {
                setLastSyncTime(new Date().toLocaleTimeString('vi-VN'));
              }

              setPacketCount(c => c + 1);
              setIsPinging(true);
              if (pingTimeout) clearTimeout(pingTimeout);
              pingTimeout = setTimeout(() => setIsPinging(false), 500);
            }
          } catch (e) {
            console.error('Failed to parse WS data:', e);
          }
        };

        ws.onerror = () => {
          setWsStatus('DISCONNECTED');
          ws?.close();
        };

        ws.onclose = () => {
          setWsStatus('DISCONNECTED');
          reconnectTimeout = setTimeout(connectWS, 4000);
        };
      } catch (e) {
        setWsStatus('DISCONNECTED');
        reconnectTimeout = setTimeout(connectWS, 4000);
      }
    };

    connectWS();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (pingTimeout) clearTimeout(pingTimeout);
    };
  }, []);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Fullscreen Map (Chỉ hiển thị TP.HCM, phân loại Đường vs Khu vực ngập) */}
      <FloodMap 
        devices={data.devices} 
        severeLocations={data.severe_locations} 
        roads={data.roads || []}
        zones={data.zones || []}
        selectedLocation={selectedLocation}
      />

      {/* Floating Glassmorphism Sidebar (Dự báo Triều cường + Cảnh báo Đường/Khu vực + IoT Realtime Summary) */}
      <Sidebar 
        tides={data.tides} 
        severeLocations={data.severe_locations} 
        roads={data.roads || []}
        zones={data.zones || []}
        summary={data.summary}
        weather={data.weather}
        isPinging={isPinging}
        wsStatus={wsStatus}
        onSelectLocation={(loc) => setSelectedLocation(loc)}
      />

      {/* Floating Top Bar (Mực nước TB, Thời tiết & Clock) */}
      <TopBar 
        weather={data.weather} 
        isPinging={isPinging}
        avgWater={data.summary?.avg_water_level_cm}
      />
    </div>
  );
}
