import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { Navigation, Plus, Minus, Layers, Waves } from 'lucide-react';

export default function FloodMap({ devices, severeLocations, selectedLocation }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersLayerRef = useRef(null);
  const severeLayerRef = useRef(null);
  const floodZonesLayerRef = useRef(null);
  const streamlinesLayerRef = useRef(null);

  const [showFloodZones, setShowFloodZones] = useState(true);
  const [showStreamlines, setShowStreamlines] = useState(true);

  // Khởi tạo Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [10.7850, 106.7050],
      zoom: 12,
      zoomControl: false,
      attributionControl: false
    });

    // OpenStreetMap Tiles nền tối cao cấp
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Thứ tự hiển thị: Vùng ngập -> Luồng nước -> Điểm thủy chí -> Xe IoT
    floodZonesLayerRef.current = L.layerGroup().addTo(map);
    streamlinesLayerRef.current = L.layerGroup().addTo(map);
    severeLayerRef.current = L.layerGroup().addTo(map);
    markersLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Cập nhật Vùng nước ngập lan tỏa & Luồng nước động (Water Inundation & Flow Streamlines)
  useEffect(() => {
    if (!mapRef.current || !floodZonesLayerRef.current || !streamlinesLayerRef.current) return;

    floodZonesLayerRef.current.clearLayers();
    streamlinesLayerRef.current.clearLayers();

    if (!showFloodZones || !severeLocations) return;

    severeLocations.forEach(loc => {
      const isCrit = loc.severity === 'CRITICAL';
      const color = isCrit ? '#f43f5e' : (loc.severity === 'WARNING' ? '#f59e0b' : '#38bdf8');
      
      // Bán kính vùng ngập theo mực nước thực tế (600m - 1000m)
      const radius = Math.round(Math.min(1000, Math.max(550, loc.water_level_m * 460)));

      // 1. Sóng nước dâng đa tầng (Concentric Expanding Water Wave Currents)
      // Vòng ngoài cùng: Sóng nước loang rộng mờ ảo
      const outerWave = L.circle([loc.latitude, loc.longitude], {
        radius: radius,
        color: color,
        fillColor: color,
        fillOpacity: 0.10,
        weight: 1.5,
        className: 'water-ripple-wave'
      });

      // Vòng giữa: Vùng ngập trung gian
      const midWave = L.circle([loc.latitude, loc.longitude], {
        radius: Math.round(radius * 0.62),
        color: color,
        fillColor: color,
        fillOpacity: 0.20,
        weight: 2,
        dashArray: '5, 5',
        className: 'flood-pulse-zone'
      });

      // Vòng lõi: Rốn trũng ngập sâu nhất
      const coreInundation = L.circle([loc.latitude, loc.longitude], {
        radius: Math.round(radius * 0.32),
        color: color,
        fillColor: color,
        fillOpacity: 0.38,
        weight: 2.5,
        className: 'flood-core-zone'
      });

      const popupContent = `
        <div style="padding: 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
          <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
            <span style="font-size: 16px;">🌊</span>
            <span style="font-weight: 800; font-size: 14px; color: #f8fafc;">VÙNG NGẬP LƯU VỰC</span>
          </div>
          <div style="font-size: 13px; font-weight: 700; color: ${color}; margin-bottom: 8px;">
            ${loc.name} (${loc.district})
          </div>
          <div style="background: rgba(255,255,255,0.06); padding: 8px; border-radius: 8px; font-size: 12px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #94a3b8;">Mực nước đỉnh triều:</span>
              <span style="font-weight: 800; color: ${color}; font-family: 'Space Grotesk';">↑ ${loc.water_level_m} m</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: #94a3b8;">Bán kính ảnh hưởng:</span>
              <span style="font-weight: 700; color: #38bdf8; font-family: 'Space Grotesk';">~${radius} m</span>
            </div>
          </div>
          <div style="font-size: 11px; color: #fca5a5; background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.2); padding: 6px; border-radius: 6px;">
            ⚠️ Luồng nước dâng cao, khuyến cáo phương tiện tránh lưu thông qua khu vực.
          </div>
        </div>
      `;

      outerWave.bindPopup(popupContent);
      midWave.bindPopup(popupContent);
      coreInundation.bindPopup(popupContent);

      floodZonesLayerRef.current.addLayer(outerWave);
      floodZonesLayerRef.current.addLayer(midWave);
      floodZonesLayerRef.current.addLayer(coreInundation);

      // 2. Các luồng nước chảy động (Directional Water Flow Streamlines)
      if (showStreamlines) {
        // Sinh 3 nhánh luồng nước đổ về tâm ngập
        const angles = [0.4, 2.2, 4.3];
        angles.forEach(ang => {
          const streamLength = radius * 0.000014;
          const startLat = loc.latitude + Math.sin(ang) * streamLength;
          const startLon = loc.longitude + Math.cos(ang) * streamLength;
          const midLat = loc.latitude + Math.sin(ang + 0.3) * (streamLength * 0.5);
          const midLon = loc.longitude + Math.cos(ang + 0.3) * (streamLength * 0.5);

          const streamline = L.polyline([
            [startLat, startLon],
            [midLat, midLon],
            [loc.latitude, loc.longitude]
          ], {
            color: color,
            weight: 3,
            opacity: 0.85,
            className: 'flow-streamline'
          });

          streamlinesLayerRef.current.addLayer(streamline);
        });
      }
    });
  }, [showFloodZones, showStreamlines, severeLocations]);

  // Cập nhật Cột Thủy chí đo nước kỹ thuật số (Digital Water Depth Gauge Beacons) tại 10 điểm ngập
  useEffect(() => {
    if (!mapRef.current || !severeLayerRef.current || !severeLocations) return;

    severeLayerRef.current.clearLayers();

    severeLocations.forEach(loc => {
      const isCrit = loc.severity === 'CRITICAL';
      const color = isCrit ? '#f43f5e' : (loc.severity === 'WARNING' ? '#f59e0b' : '#38bdf8');

      const gaugeHtml = `
        <div style="position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer;">
          <!-- Sóng âm tỏa ra từ cột đo -->
          <div style="position: absolute; width: 44px; height: 44px; border-radius: 50%; background: ${color}; opacity: 0.25; animation: radar-ping 1.8s infinite;"></div>
          <div style="position: absolute; width: 26px; height: 26px; border-radius: 50%; background: ${color}; opacity: 0.45;"></div>
          
          <!-- Thước đo thủy chí hiển thị trực quan -->
          <div style="
            position: absolute; 
            left: 18px; 
            top: -16px; 
            white-space: nowrap; 
            background: rgba(14, 17, 23, 0.92); 
            backdrop-filter: blur(12px); 
            border: 1px solid ${color}66; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 10px ${color}44;
            border-radius: 8px; 
            padding: 4px 10px; 
            display: flex; 
            align-items: center; 
            gap: 6px; 
            z-index: 10;
          ">
            <span style="font-size: 13px;">🌊</span>
            <div style="display: flex; flex-direction: column;">
              <span style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">${loc.district}</span>
              <span style="font-size: 12px; font-weight: 800; color: ${color}; font-family: 'Space Grotesk';">
                ↑ ${loc.water_level_m}m
              </span>
            </div>
          </div>
          
          <!-- Chấm tâm cột thủy chí -->
          <div style="width: 14px; height: 14px; border-radius: 50%; background: ${color}; border: 2px solid #ffffff; box-shadow: 0 0 15px ${color}; z-index: 5;"></div>
        </div>
      `;

      const gaugeIcon = L.divIcon({
        html: gaugeHtml,
        className: 'custom-gauge-beacon',
        iconSize: [44, 44],
        iconAnchor: [22, 22]
      });

      const marker = L.marker([loc.latitude, loc.longitude], { icon: gaugeIcon });
      severeLayerRef.current.addLayer(marker);
    });
  }, [severeLocations]);

  // Cập nhật Markers 50 Xe IoT (Tản đều, KHÔNG vẽ vòng tròn con đè lên nhau nữa)
  useEffect(() => {
    if (!mapRef.current || !markersLayerRef.current || !devices) return;

    markersLayerRef.current.clearLayers();

    devices.forEach(device => {
      let color = '#10b981'; // SAFE
      let label = 'An toàn';
      if (device.status === 'CRITICAL') {
        color = '#f43f5e';
        label = 'Ngập sâu';
      } else if (device.status === 'ALERT') {
        color = '#f59e0b';
        label = 'Cảnh báo ngập';
      }

      // Marker gọn gàng, có radar quét nhẹ, không gây nùi bản đồ
      const iconHtml = `
        <div class="radar-marker" style="color: ${color}">
          <div class="radar-wave" style="animation-duration: 2.4s;"></div>
          <div class="radar-core" style="background-color: ${color}; width: 10px; height: 10px;"></div>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-radar-icon',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      const popupContent = `
        <div style="padding: 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 13px; color: #f8fafc;">${device.name}</span>
            <span style="font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: ${color}22; color: ${color}; border: 1px solid ${color}44;">
              ${device.status}
            </span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
            ID: <span style="font-family: 'Space Grotesk'; color: #e2e8f0;">${device.device_id}</span>
          </div>
          <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
              <span style="color: #94a3b8;">Mực nước đo được:</span>
              <span style="font-weight: 800; font-family: 'Space Grotesk'; color: ${color};">${device.water_level_cm} cm</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
              <span style="color: #94a3b8;">Lượng mưa:</span>
              <span style="font-family: 'Space Grotesk'; color: #38bdf8;">${device.rainfall_mm} mm</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px;">
              <span style="color: #94a3b8;">Nhiệt độ:</span>
              <span style="font-family: 'Space Grotesk'; color: #cbd5e1;">${device.temperature_c} °C</span>
            </div>
          </div>
          <div style="font-size: 10px; color: #64748b; text-align: right;">
            Cập nhật: ${device.updated_at}
          </div>
        </div>
      `;

      const marker = L.marker([device.latitude, device.longitude], { icon: customIcon });
      marker.bindPopup(popupContent);
      markersLayerRef.current.addLayer(marker);
    });
  }, [devices]);

  // Fly to khi user click vào một điểm ngập ở Sidebar
  useEffect(() => {
    if (!mapRef.current || !selectedLocation) return;
    mapRef.current.flyTo([selectedLocation.latitude, selectedLocation.longitude], 14, {
      duration: 1.2
    });
  }, [selectedLocation]);

  const handleZoomIn = () => mapRef.current?.zoomIn();
  const handleZoomOut = () => mapRef.current?.zoomOut();
  const handleRecenter = () => mapRef.current?.flyTo([10.7850, 106.7050], 12);

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

        {/* Nút bật tắt Vùng ngập */}
        <button 
          onClick={() => setShowFloodZones(!showFloodZones)}
          title={showFloodZones ? "Tắt vùng ngập lan tỏa" : "Bật vùng ngập lan tỏa"}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: showFloodZones ? 'rgba(2, 132, 199, 0.45)' : 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: showFloodZones ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: showFloodZones ? '#38bdf8' : '#f8fafc',
            cursor: 'pointer',
            boxShadow: showFloodZones ? '0 0 15px rgba(56, 189, 248, 0.4)' : '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Layers size={18} />
        </button>

        {/* Nút bật tắt Luồng nước chảy */}
        <button 
          onClick={() => setShowStreamlines(!showStreamlines)}
          title={showStreamlines ? "Tắt mô phỏng luồng nước" : "Bật mô phỏng luồng nước"}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: showStreamlines ? 'rgba(16, 185, 129, 0.35)' : 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: showStreamlines ? '1px solid #10b981' : '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: showStreamlines ? '#10b981' : '#f8fafc',
            cursor: 'pointer',
            boxShadow: showStreamlines ? '0 0 15px rgba(16, 185, 129, 0.4)' : '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Waves size={18} />
        </button>
      </div>

      {/* Floating Legend / Status Badge for Water Currents */}
      <div style={{
        position: 'absolute',
        bottom: '24px',
        left: '24px',
        zIndex: 1000,
        background: 'rgba(14, 17, 23, 0.90)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: '14px',
        padding: '12px 18px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        boxShadow: '0 12px 35px rgba(0,0,0,0.6)',
        pointerEvents: 'none'
      }}>
        <div style={{
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          background: '#06b6d4',
          boxShadow: '0 0 12px #06b6d4',
          animation: 'radar-ping 2s infinite'
        }} />
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, color: '#f8fafc', letterSpacing: '0.6px' }}>
            HỆ THỐNG GIÁM SÁT THỦY VĂN & LUỒNG NƯỚC THỜI GIAN THỰC
          </span>
          <span style={{ fontSize: '10px', color: '#94a3b8' }}>
            10 Điểm nóng • Sóng nước dâng & Luồng chảy động • 50 Cảm biến IoT
          </span>
        </div>
      </div>
    </div>
  );
}
