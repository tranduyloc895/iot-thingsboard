import React, { useState, useEffect } from 'react';
import FloodMap from './components/FloodMap';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';

// Dữ liệu baseline ban đầu phòng trường hợp backend chưa kịp khởi động
const INITIAL_DATA = {
  timestamp: new Date().toISOString(),
  summary: {
    safe_count: 14,
    alert_count: 4,
    critical_count: 2,
    avg_water_level_cm: 22.4,
    total_active_devices: 20
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
      name: 'NHA BE',
      current_level: 1.28,
      trend: 'UP',
      status: 'STABLE',
      peak_level: 1.42,
      peak_hour: 10,
      hourly_data: Array.from({ length: 25 }, (_, h) => ({
        hour: h,
        level: Number((0.85 + 0.48 * Math.sin((h - 4.5) * Math.PI / 6) + 0.08 * Math.sin((h - 1.5) * Math.PI / 3)).toFixed(2))
      }))
    }
  ],
  severe_locations: [
    {
      id: 'loc-1',
      name: 'Huynh Tan Phat',
      district: 'District 7',
      water_level_m: 1.68,
      severity: 'CRITICAL',
      minutes_ago: 10,
      latitude: 10.7412,
      longitude: 106.7285
    },
    {
      id: 'loc-2',
      name: 'Thao Dien',
      district: 'District 2',
      water_level_m: 1.35,
      severity: 'WARNING',
      minutes_ago: 8,
      latitude: 10.8035,
      longitude: 106.7321
    },
    {
      id: 'loc-3',
      name: 'Bui Vien St.',
      district: 'District 1',
      water_level_m: 1.10,
      severity: 'ALERT',
      minutes_ago: 15,
      latitude: 10.7670,
      longitude: 106.6925
    }
  ],
  devices: [
    { device_id: 'VN-HCM-001', name: 'Sensor Car D7-01', latitude: 10.7412, longitude: 106.7285, water_level_cm: 48.5, rainfall_mm: 32.0, temperature_c: 30.1, status: 'CRITICAL', updated_at: '22:45:00' },
    { device_id: 'VN-HCM-002', name: 'Sensor Car D7-02', latitude: 10.7550, longitude: 106.7120, water_level_cm: 42.0, rainfall_mm: 28.0, temperature_c: 30.5, status: 'CRITICAL', updated_at: '22:45:02' },
    { device_id: 'VN-HCM-003', name: 'Sensor Car D2-01', latitude: 10.8035, longitude: 106.7321, water_level_cm: 38.0, rainfall_mm: 25.5, temperature_c: 29.8, status: 'ALERT', updated_at: '22:45:01' },
    { device_id: 'VN-HCM-004', name: 'Sensor Car D2-02', latitude: 10.8090, longitude: 106.7380, water_level_cm: 45.2, rainfall_mm: 34.0, temperature_c: 30.0, status: 'CRITICAL', updated_at: '22:45:03' },
    { device_id: 'VN-HCM-005', name: 'Sensor Car D1-01', latitude: 10.7670, longitude: 106.6925, water_level_cm: 24.5, rainfall_mm: 18.0, temperature_c: 31.0, status: 'ALERT', updated_at: '22:45:05' },
    { device_id: 'VN-HCM-006', name: 'Sensor Car D1-02', latitude: 10.7715, longitude: 106.7020, water_level_cm: 12.0, rainfall_mm: 12.0, temperature_c: 31.2, status: 'SAFE', updated_at: '22:45:00' },
    { device_id: 'VN-HCM-007', name: 'Sensor Car BT-01', latitude: 10.7950, longitude: 106.7150, water_level_cm: 36.8, rainfall_mm: 24.0, temperature_c: 30.2, status: 'ALERT', updated_at: '22:45:02' },
    { device_id: 'VN-HCM-008', name: 'Sensor Car BT-02', latitude: 10.8120, longitude: 106.7110, water_level_cm: 22.0, rainfall_mm: 15.0, temperature_c: 30.5, status: 'SAFE', updated_at: '22:45:04' },
    { device_id: 'VN-HCM-009', name: 'Sensor Car D8-01', latitude: 10.7380, longitude: 106.6710, water_level_cm: 39.5, rainfall_mm: 29.0, temperature_c: 29.5, status: 'ALERT', updated_at: '22:45:01' },
    { device_id: 'VN-HCM-010', name: 'Sensor Car D4-01', latitude: 10.7600, longitude: 106.7050, water_level_cm: 18.0, rainfall_mm: 14.0, temperature_c: 30.8, status: 'SAFE', updated_at: '22:45:05' },
    { device_id: 'VN-HCM-011', name: 'Sensor Car D5-01', latitude: 10.7540, longitude: 106.6630, water_level_cm: 14.5, rainfall_mm: 11.0, temperature_c: 31.0, status: 'SAFE', updated_at: '22:45:03' },
    { device_id: 'VN-HCM-012', name: 'Sensor Car D3-01', latitude: 10.7810, longitude: 106.6850, water_level_cm: 10.0, rainfall_mm: 8.0, temperature_c: 31.5, status: 'SAFE', updated_at: '22:45:02' },
    { device_id: 'VN-HCM-013', name: 'Sensor Car TB-01', latitude: 10.7980, longitude: 106.6540, water_level_cm: 16.0, rainfall_mm: 14.0, temperature_c: 30.7, status: 'SAFE', updated_at: '22:45:00' },
    { device_id: 'VN-HCM-014', name: 'Sensor Car PN-01', latitude: 10.7990, longitude: 106.6820, water_level_cm: 11.5, rainfall_mm: 10.0, temperature_c: 31.0, status: 'SAFE', updated_at: '22:45:04' },
    { device_id: 'VN-HCM-015', name: 'Sensor Car GV-01', latitude: 10.8350, longitude: 106.6720, water_level_cm: 29.0, rainfall_mm: 20.0, temperature_c: 30.0, status: 'ALERT', updated_at: '22:45:02' },
    { device_id: 'VN-HCM-016', name: 'Sensor Car TD-01', latitude: 10.8520, longitude: 106.7550, water_level_cm: 15.0, rainfall_mm: 13.0, temperature_c: 30.4, status: 'SAFE', updated_at: '22:45:01' },
    { device_id: 'VN-HCM-017', name: 'Sensor Car BCh-01', latitude: 10.7020, longitude: 106.6020, water_level_cm: 31.0, rainfall_mm: 22.0, temperature_c: 29.8, status: 'ALERT', updated_at: '22:45:05' },
    { device_id: 'VN-HCM-018', name: 'Sensor Car D12-01', latitude: 10.8650, longitude: 106.6430, water_level_cm: 19.5, rainfall_mm: 16.0, temperature_c: 30.2, status: 'SAFE', updated_at: '22:45:03' },
    { device_id: 'VN-HCM-019', name: 'Sensor Car D6-01', latitude: 10.7480, longitude: 106.6420, water_level_cm: 28.0, rainfall_mm: 19.0, temperature_c: 30.1, status: 'ALERT', updated_at: '22:45:04' },
    { device_id: 'VN-HCM-020', name: 'Sensor Car D10-01', latitude: 10.7720, longitude: 106.6680, water_level_cm: 13.0, rainfall_mm: 10.0, temperature_c: 31.0, status: 'SAFE', updated_at: '22:45:02' }
  ]
};

export default function App() {
  const [data, setData] = useState(INITIAL_DATA);
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    // Xác định URL WebSocket phù hợp (môi trường dev port 8000 hoặc K8s ingress)
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
