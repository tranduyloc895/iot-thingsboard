import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { Navigation, Plus, Minus, Layers } from 'lucide-react';

export default function FloodMap({ devices, severeLocations, selectedLocation }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersLayerRef = useRef(null);
  const severeLayerRef = useRef(null);
  const floodZonesLayerRef = useRef(null);

  const [showFloodZones, setShowFloodZones] = useState(true);

  // Khởi tạo Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [10.7769, 106.7009],
      zoom: 12,
      zoomControl: false,
      attributionControl: false
    });

    // OpenStreetMap Tiles
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Thứ tự layer: Vùng ngập ở dưới cùng -> Beacons ngập lớn -> Markers xe IoT
    floodZonesLayerRef.current = L.layerGroup().addTo(map);
    severeLayerRef.current = L.layerGroup().addTo(map);
    markersLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Cập nhật vùng ngập diện rộng (Dynamic Flood Buffer Zones - Cách 1)
  useEffect(() => {
    if (!mapRef.current || !floodZonesLayerRef.current) return;

    floodZonesLayerRef.current.clearLayers();

    if (!showFloodZones) return;

    // 1. Vùng ngập diện rộng từ các điểm ngập nghiêm trọng (Severe Locations)
    if (severeLocations) {
      severeLocations.forEach(loc => {
        const isCrit = loc.severity === 'CRITICAL';
        const color = isCrit ? '#f43f5e' : '#f59e0b';
        // Bán kính vùng ngập tính theo mực nước triều (500m - 1200m)
        const radius = Math.round(Math.min(1200, Math.max(500, loc.water_level_m * 450)));

        // Vòng ảnh hưởng lan tỏa bên ngoài (Outer Buffer Zone với animation sóng loang)
        const outerCircle = L.circle([loc.latitude, loc.longitude], {
          radius: radius,
          color: color,
          fillColor: color,
          fillOpacity: 0.16,
          weight: 1.5,
          dashArray: '6, 6',
          className: 'flood-pulse-zone'
        });

        // Vòng lõi ngập sâu trung tâm (Core Inundation Zone)
        const innerCircle = L.circle([loc.latitude, loc.longitude], {
          radius: Math.round(radius * 0.42),
          color: color,
          fillColor: color,
          fillOpacity: 0.38,
          weight: 2,
          className: 'flood-core-zone'
        });

        const zonePopup = `
          <div style="padding: 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
              <span style="font-size: 14px;">🌊</span>
              <span style="font-weight: 800; font-size: 14px; color: #f8fafc;">VÙNG NGẬP DIỆN RỘNG</span>
            </div>
            <div style="font-size: 13px; font-weight: 700; color: ${color}; margin-bottom: 8px;">
              ${loc.name} (${loc.district})
            </div>
            <div style="background: rgba(255,255,255,0.06); padding: 8px; border-radius: 8px; font-size: 12px; margin-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #94a3b8;">Bán kính ảnh hưởng:</span>
                <span style="font-weight: 700; color: #38bdf8; font-family: 'Space Grotesk';">~${radius} m</span>
              </div>
              <div style="display: flex; justify-content: space-between;">
                <span style="color: #94a3b8;">Mực nước đỉnh triều:</span>
                <span style="font-weight: 800; color: ${color}; font-family: 'Space Grotesk';">↑ ${loc.water_level_m} m</span>
              </div>
            </div>
            <div style="font-size: 11px; color: #fca5a5; background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.2); padding: 6px; border-radius: 6px;">
              ⚠️ Cảnh báo: Vùng trũng ngập sâu, các phương tiện gầm thấp không nên lưu thông.
            </div>
          </div>
        `;

        outerCircle.bindPopup(zonePopup);
        innerCircle.bindPopup(zonePopup);

        floodZonesLayerRef.current.addLayer(outerCircle);
        floodZonesLayerRef.current.addLayer(innerCircle);
      });
    }

    // 2. Vùng ngập cục bộ phát hiện bởi các xe IoT (khi nước >= 25cm)
    if (devices) {
      devices.forEach(device => {
        if (device.water_level_cm >= 25.0) {
          const isCrit = device.status === 'CRITICAL';
          const color = isCrit ? '#f43f5e' : '#f59e0b';
          const radius = isCrit ? 450 : 280;

          const vehicleZone = L.circle([device.latitude, device.longitude], {
            radius: radius,
            color: color,
            fillColor: color,
            fillOpacity: isCrit ? 0.22 : 0.15,
            weight: 1.2,
            dashArray: '4, 4',
            className: 'flood-pulse-zone'
          });

          vehicleZone.bindPopup(`
            <div style="padding: 8px; font-family: 'Plus Jakarta Sans', sans-serif;">
              <div style="font-weight: 700; font-size: 13px; color: ${color}; margin-bottom: 4px;">
                ⚠️ Vùng trũng ngập cục bộ
              </div>
              <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">
                Phát hiện bởi: <strong style="color: #f1f5f9;">${device.name}</strong>
              </div>
              <div style="font-size: 12px; color: #cbd5e1;">
                Mực nước đo được: <strong style="color: ${color}; font-family: 'Space Grotesk';">${device.water_level_cm} cm</strong>
              </div>
              <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                Bán kính ảnh hưởng: ~${radius}m
              </div>
            </div>
          `);

          floodZonesLayerRef.current.addLayer(vehicleZone);
        }
      });
    }
  }, [showFloodZones, severeLocations, devices]);

  // Cập nhật markers của các xe IoT khi có telemetry mới
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

  // Cập nhật các điểm ngập cảnh báo lớn (Severe locations beacons)
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
          onClick={() => setShowFloodZones(!showFloodZones)}
          title={showFloodZones ? "Tắt vùng ngập diện rộng" : "Bật vùng ngập diện rộng"}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: showFloodZones ? 'rgba(2, 132, 199, 0.4)' : 'rgba(14, 17, 23, 0.85)',
            backdropFilter: 'blur(12px)',
            border: showFloodZones ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: showFloodZones ? '#38bdf8' : '#f8fafc',
            cursor: 'pointer',
            boxShadow: showFloodZones ? '0 0 15px rgba(56, 189, 248, 0.35)' : '0 8px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.2s'
          }}
        >
          <Layers size={18} />
        </button>
      </div>

      {/* Floating Legend / Status Badge for Flood Zones */}
      {showFloodZones && (
        <div style={{
          position: 'absolute',
          bottom: '24px',
          left: '24px',
          zIndex: 1000,
          background: 'rgba(14, 17, 23, 0.88)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '10px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
          pointerEvents: 'none'
        }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            background: '#f43f5e',
            boxShadow: '0 0 10px #f43f5e',
            animation: 'radar-ping 2s infinite'
          }} />
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#f8fafc', letterSpacing: '0.5px' }}>
              VÙNG NGẬP DIỆN RỘNG (BUFFER ZONES)
            </span>
            <span style={{ fontSize: '10px', color: '#94a3b8' }}>
              Bán kính lan tỏa 300m – 1200m • Tự động quét theo độ sâu
            </span>
          </div>
        </div>
      )}

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
