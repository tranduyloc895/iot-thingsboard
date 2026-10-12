import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { Navigation, Plus, Minus, Layers, Radio, ShieldAlert } from 'lucide-react';

// Bảng màu Neon độ tương phản cao cho bản đồ nền tối (High-Contrast Neon Palette)
const SEVERITY_COLORS = {
  SAFE: {
    hex: '#06b6d4',      // Cyan Neon
    bg: 'rgba(6, 182, 212, 0.15)',
    border: 'rgba(6, 182, 212, 0.4)',
    glow: '0 0 16px rgba(6, 182, 212, 0.7)',
    label: 'An toàn (<20cm)',
    advisory: 'Mực nước an toàn. Các phương tiện di chuyển bình thường.'
  },
  ALERT: {
    hex: '#facc15',      // Amber Gold Neon
    bg: 'rgba(250, 204, 21, 0.15)',
    border: 'rgba(250, 204, 21, 0.4)',
    glow: '0 0 16px rgba(250, 204, 21, 0.7)',
    label: 'Cảnh báo (20–35cm)',
    advisory: 'Đường ngập nhẹ. Lưu thông chậm, cẩn trọng vùng trũng sát mép đường.'
  },
  WARNING: {
    hex: '#ff7b00',      // Vivid Orange Neon
    bg: 'rgba(255, 123, 0, 0.18)',
    border: 'rgba(255, 123, 0, 0.45)',
    glow: '0 0 20px rgba(255, 123, 0, 0.8)',
    label: 'Nguy cơ cao (35–50cm)',
    advisory: 'Ngập sâu vừa. Xe máy gầm thấp có nguy cơ chết máy, nên chọn lộ trình tránh.'
  },
  CRITICAL: {
    hex: '#ff0055',      // Crimson Neon (Glow rực rỡ)
    bg: 'rgba(255, 0, 85, 0.22)',
    border: 'rgba(255, 0, 85, 0.55)',
    glow: '0 0 24px rgba(255, 0, 85, 0.9)',
    label: 'Ngập cực sâu (>50cm)',
    advisory: '⛔ NGUY HIỂM: Cấm phương tiện gầm thấp & xe máy lưu thông. Đang điều phối phân luồng.'
  }
};

export default function FloodMap({ devices, severeLocations, selectedLocation, roads = [] }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const roadsLayerRef = useRef(null);
  const nodesLayerRef = useRef(null);
  const beaconsLayerRef = useRef(null);

  const [showRoads, setShowRoads] = useState(true);
  const [showSensorNodes, setShowSensorNodes] = useState(true);

  // 1. Khởi tạo Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [10.7880, 106.7050],
      zoom: 12,
      zoomControl: false,
      attributionControl: false
    });

    // Dark-mode Map Tile
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    roadsLayerRef.current = L.layerGroup().addTo(map);
    nodesLayerRef.current = L.layerGroup().addTo(map);
    beaconsLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // 2. Vẽ 10 Tuyến đường ngập dạng Polyline phát sáng Neon & 50 Trạm quan trắc IoT cố định
  useEffect(() => {
    if (!mapRef.current || !roadsLayerRef.current || !nodesLayerRef.current) return;

    roadsLayerRef.current.clearLayers();
    nodesLayerRef.current.clearLayers();

    if (!roads || roads.length === 0) return;

    roads.forEach(road => {
      const styleCfg = SEVERITY_COLORS[road.severity] || SEVERITY_COLORS.SAFE;
      const color = styleCfg.hex;

      if (showRoads && road.coordinates && road.coordinates.length > 1) {
        // Lớp 1: Vầng sáng Neon phát quang bên dưới (Glow halo line)
        const glowLine = L.polyline(road.coordinates, {
          color: color,
          weight: 15,
          opacity: 0.28,
          lineCap: 'round',
          lineJoin: 'round',
          className: 'neon-road-halo'
        });

        // Lớp 2: Đường chỉ thị ngập chính (Main vibrant polyline)
        const mainLine = L.polyline(road.coordinates, {
          color: color,
          weight: 7,
          opacity: 0.95,
          lineCap: 'round',
          lineJoin: 'round',
          className: `neon-road-line ${road.severity === 'CRITICAL' ? 'neon-road-pulse' : ''}`
        });

        const popupContent = `
          <div style="padding: 12px; font-family: 'Plus Jakarta Sans', sans-serif; min-width: 250px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-weight: 800; font-size: 15px; color: #f8fafc;">${road.name}</span>
              <span style="font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 6px; background: ${styleCfg.bg}; color: ${color}; border: 1px solid ${styleCfg.border};">
                ${road.severity}
              </span>
            </div>
            
            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 10px;">
              Khu vực: <span style="color: #cbd5e1; font-weight: 600;">${road.district}</span> • Tuyến dài: <span style="font-family: 'Space Grotesk'; color: #38bdf8;">${road.length_km} km</span>
            </div>

            <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.08);">
              <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px;">
                <span style="color: #94a3b8;">Độ sâu cao nhất:</span>
                <span style="font-weight: 800; font-family: 'Space Grotesk'; color: ${color}; font-size: 14px;">
                  ${road.max_water_cm} cm
                </span>
              </div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px;">
                <span style="color: #94a3b8;">Mực nước trung bình:</span>
                <span style="font-weight: 700; font-family: 'Space Grotesk'; color: #e2e8f0;">
                  ${road.avg_water_cm} cm
                </span>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 12px;">
                <span style="color: #94a3b8;">Trạm quan trắc:</span>
                <span style="font-weight: 700; color: #38bdf8;">5 / 5 trạm Online</span>
              </div>
            </div>

            <div style="font-size: 11px; line-height: 1.4; color: ${road.severity === 'CRITICAL' ? '#fca5a5' : '#e2e8f0'}; background: ${styleCfg.bg}; border: 1px solid ${styleCfg.border}; padding: 8px; border-radius: 8px;">
              ${styleCfg.advisory}
            </div>
          </div>
        `;

        mainLine.bindPopup(popupContent);
        glowLine.bindPopup(popupContent);

        roadsLayerRef.current.addLayer(glowLine);
        roadsLayerRef.current.addLayer(mainLine);
      }

      // 3. Vẽ 5 trạm/nút giao (Road Nodes) trên từng tuyến
      if (showSensorNodes && road.nodes) {
        road.nodes.forEach((node, nodeIdx) => {
          const nodeStyle = SEVERITY_COLORS[node.status] || SEVERITY_COLORS.SAFE;
          const nodeColor = nodeStyle.hex;

          const nodeHtml = `
            <div style="position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer;">
              <!-- Radar ping nhẹ quanh node -->
              <div style="position: absolute; width: 22px; height: 22px; border-radius: 50%; background: ${nodeColor}; opacity: 0.35; animation: radar-ping 2.2s infinite;"></div>
              
              <!-- Chấm trạm IoT trung tâm -->
              <div style="
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                background: ${nodeColor}; 
                border: 2px solid #ffffff; 
                box-shadow: 0 0 10px ${nodeColor}, 0 0 20px ${nodeColor};
                z-index: 5;
              "></div>
            </div>
          `;

          const nodeIcon = L.divIcon({
            html: nodeHtml,
            className: 'custom-road-node-icon',
            iconSize: [22, 22],
            iconAnchor: [11, 11]
          });

          const nodeMarker = L.marker([node.latitude, node.longitude], { icon: nodeIcon });

          const nodePopup = `
            <div style="padding: 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
              <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="font-size: 12px; color: ${nodeColor};">📡</span>
                <span style="font-weight: 800; font-size: 13px; color: #f8fafc;">${node.name}</span>
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
                Tuyến: <span style="color: #e2e8f0; font-weight: 600;">${road.name}</span> (Node ${nodeIdx + 1}/5)
              </div>
              <div style="background: rgba(255,255,255,0.06); padding: 8px; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 11px; color: #94a3b8;">Mực nước thực tế:</span>
                  <span style="font-size: 14px; font-weight: 800; font-family: 'Space Grotesk'; color: ${nodeColor};">
                    ${node.water_level_cm} cm
                  </span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                  <span style="font-size: 11px; color: #94a3b8;">Trạng thái:</span>
                  <span style="font-size: 11px; font-weight: 700; color: ${nodeColor};">
                    ${node.status}
                  </span>
                </div>
              </div>
            </div>
          `;

          nodeMarker.bindPopup(nodePopup);
          nodesLayerRef.current.addLayer(nodeMarker);
        });
      }
    });
  }, [roads, showRoads, showSensorNodes]);

  // 4. Fly to khi user click vào một tuyến đường hoặc điểm ngập ở Sidebar
  useEffect(() => {
    if (!mapRef.current || !selectedLocation) return;
    mapRef.current.flyTo([selectedLocation.latitude, selectedLocation.longitude], 14, {
      duration: 1.2
    });
  }, [selectedLocation]);

  const handleZoomIn = () => mapRef.current?.zoomIn();
  const handleZoomOut = () => mapRef.current?.zoomOut();
  const handleRecenter = () => mapRef.current?.flyTo([10.7880, 106.7050], 12);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Khung bản đồ Leaflet */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Floating Map Controls trên góc phải */}
      <div style={{
        position: 'absolute',
        top: '90px',
        right: '20px',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <button 
          onClick={handleRecenter}
          title="Về trung tâm TP.HCM"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#f8fafc',
            cursor: 'pointer',
            boxShadow: '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Navigation size={18} />
        </button>

        <button 
          onClick={handleZoomIn}
          title="Phóng to"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#f8fafc',
            cursor: 'pointer',
            boxShadow: '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Plus size={18} />
        </button>

        <button 
          onClick={handleZoomOut}
          title="Thu nhỏ"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#f8fafc',
            cursor: 'pointer',
            boxShadow: '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Minus size={18} />
        </button>

        {/* Nút bật tắt Tuyến đường ngập (Polylines) */}
        <button 
          onClick={() => setShowRoads(!showRoads)}
          title={showRoads ? "Ẩn tuyến đường ngập" : "Hiện tuyến đường ngập"}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: showRoads ? 'rgba(2, 132, 199, 0.45)' : 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: showRoads ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: showRoads ? '#38bdf8' : '#f8fafc',
            cursor: 'pointer',
            boxShadow: showRoads ? '0 0 15px rgba(56, 189, 248, 0.4)' : '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Layers size={18} />
        </button>

        {/* Nút bật tắt Trạm cảm biến IoT (Nodes) */}
        <button 
          onClick={() => setShowSensorNodes(!showSensorNodes)}
          title={showSensorNodes ? "Ẩn 50 trạm IoT" : "Hiện 50 trạm IoT"}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: showSensorNodes ? 'rgba(16, 185, 129, 0.35)' : 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: showSensorNodes ? '1px solid #10b981' : '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: showSensorNodes ? '#10b981' : '#f8fafc',
            cursor: 'pointer',
            boxShadow: showSensorNodes ? '0 0 15px rgba(16, 185, 129, 0.4)' : '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Radio size={18} />
        </button>
      </div>

      {/* Floating High-Contrast Legend ở góc dưới bên trái */}
      <div style={{
        position: 'absolute',
        bottom: '24px',
        left: '430px',
        zIndex: 1000,
        background: 'rgba(14, 17, 23, 0.92)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: '14px',
        padding: '12px 18px',
        display: 'flex',
        alignItems: 'center',
        gap: '18px',
        boxShadow: '0 12px 35px rgba(0,0,0,0.6)',
        pointerEvents: 'none'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '4px', borderRadius: '2px', background: '#06b6d4', boxShadow: '0 0 8px #06b6d4' }} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#06b6d4' }}>&lt;20cm (An toàn)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '4px', borderRadius: '2px', background: '#facc15', boxShadow: '0 0 8px #facc15' }} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#facc15' }}>20–35cm (Cảnh báo)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '4px', borderRadius: '2px', background: '#ff7b00', boxShadow: '0 0 8px #ff7b00' }} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#ff7b00' }}>35–50cm (Nguy cơ)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '12px', height: '4px', borderRadius: '2px', background: '#ff0055', boxShadow: '0 0 10px #ff0055' }} />
          <span style={{ fontSize: '11px', fontWeight: 800, color: '#ff0055' }}>&gt;50cm (Ngập sâu)</span>
        </div>
      </div>
    </div>
  );
}
