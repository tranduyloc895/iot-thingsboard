import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Navigation, Plus, Minus, Layers, Search, Maximize2 } from 'lucide-react';

export default function FloodMap({ devices, severeLocations, selectedLocation }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersLayerRef = useRef(null);
  const severeLayerRef = useRef(null);

  // Khởi tạo Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [10.7769, 106.7009],
      zoom: 12,
      zoomControl: false,
      attributionControl: false
    });

    // Dark Matter Tiles của CartoDB (Nền tối cực sang trọng)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    severeLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Cập nhật markers của 20 xe IoT khi có telemetry mới
  useEffect(() => {
    if (!mapRef.current || !markersLayerRef.current || !devices) return;

    markersLayerRef.current.clearLayers();

    devices.forEach(device => {
      let color = '#10b981'; // SAFE
      let label = 'An toàn';
      if (device.status === 'CRITICAL') {
        color = '#f43f5e';
        label = 'Ngập nghiêm trọng';
      } else if (device.status === 'ALERT') {
        color = '#f59e0b';
        label = 'Cảnh báo ngập';
      }

      const iconHtml = `
        <div class="radar-marker" style="color: ${color}">
          <div class="radar-wave"></div>
          <div class="radar-core" style="background-color: ${color}"></div>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-radar-icon',
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      });

      const popupContent = `
        <div style="padding: 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 14px; color: #f8fafc;">${device.name}</span>
            <span style="font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: ${color}22; color: ${color}; border: 1px solid ${color}44;">
              ${device.status}
            </span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
            ID: <span style="font-family: 'Space Grotesk'; color: #e2e8f0;">${device.device_id}</span>
          </div>
          <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
              <span style="color: #94a3b8;">Mực nước ngập:</span>
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

  // Cập nhật các điểm ngập cảnh báo lớn (Severe locations)
  useEffect(() => {
    if (!mapRef.current || !severeLayerRef.current || !severeLocations) return;

    severeLayerRef.current.clearLayers();

    severeLocations.forEach(loc => {
      const isCrit = loc.severity === 'CRITICAL';
      const color = isCrit ? '#f43f5e' : '#f59e0b';

      const beaconHtml = `
        <div style="position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer;">
          <div style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: ${color}; opacity: 0.25; animation: radar-ping 1.8s infinite;"></div>
          <div style="position: absolute; width: 22px; height: 22px; border-radius: 50%; background: ${color}; opacity: 0.4;"></div>
          <div style="width: 14px; height: 14px; border-radius: 50%; background: ${color}; border: 2px solid #ffffff; box-shadow: 0 0 15px ${color}; z-index: 2;"></div>
          <div style="position: absolute; left: 24px; top: -10px; white-space: nowrap; background: rgba(14, 17, 23, 0.9); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 3px 8px; font-size: 11px; font-weight: 700; color: #ffffff; z-index: 3;">
            ${loc.district} <span style="color: ${color}; font-family: 'Space Grotesk';">↑ ${loc.water_level_m}m</span>
          </div>
        </div>
      `;

      const beaconIcon = L.divIcon({
        html: beaconHtml,
        className: 'custom-severe-beacon',
        iconSize: [36, 36],
        iconAnchor: [18, 18]
      });

      const marker = L.marker([loc.latitude, loc.longitude], { icon: beaconIcon });
      severeLayerRef.current.addLayer(marker);
    });
  }, [severeLocations]);

  // Fly to khi user click vào một điểm ngập ở Sidebar
  useEffect(() => {
    if (!mapRef.current || !selectedLocation) return;
    mapRef.current.flyTo([selectedLocation.latitude, selectedLocation.longitude], 14, {
      duration: 1.2
    });
  }, [selectedLocation]);

  const handleZoomIn = () => mapRef.current?.zoomIn();
  const handleZoomOut = () => mapRef.current?.zoomOut();
  const handleRecenter = () => mapRef.current?.flyTo([10.7769, 106.7009], 12);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Khung bản đồ */}
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

        <button 
          title="Lớp dữ liệu"
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
          <Layers size={18} />
        </button>
      </div>

      {/* Watermark trung tâm TP.HCM mờ ảo trên map giống Mockup */}
      <div style={{
        position: 'absolute',
        top: '40%',
        left: '52%',
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'none',
        zIndex: 500,
        fontSize: '20px',
        fontWeight: 800,
        letterSpacing: '3px',
        color: 'rgba(255, 255, 255, 0.25)',
        textTransform: 'uppercase',
        fontFamily: 'Space Grotesk'
      }}>
        HCMC
      </div>
    </div>
  );
}
