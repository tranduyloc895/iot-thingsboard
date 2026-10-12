import React, { useState } from 'react';
import TideChart from './TideChart';
import { Droplets, AlertTriangle, ChevronRight, Activity, Flame, ChevronDown, ChevronUp, MapPin } from 'lucide-react';

const SEVERITY_COLORS = {
  SAFE: {
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.15)',
    border: 'rgba(6, 182, 212, 0.35)',
    label: 'SAFE'
  },
  ALERT: {
    color: '#facc15',
    bg: 'rgba(250, 204, 21, 0.15)',
    border: 'rgba(250, 204, 21, 0.35)',
    label: 'ALERT'
  },
  WARNING: {
    color: '#ff7b00',
    bg: 'rgba(255, 123, 0, 0.18)',
    border: 'rgba(255, 123, 0, 0.4)',
    label: 'WARNING'
  },
  CRITICAL: {
    color: '#ff0055',
    bg: 'rgba(255, 0, 85, 0.22)',
    border: 'rgba(255, 0, 85, 0.5)',
    label: 'CRITICAL'
  }
};

export default function Sidebar({ tides, severeLocations, roads = [], summary, onSelectLocation }) {
  const [selectedStationIdx, setSelectedStationIdx] = useState(0);
  const [showAllCharts, setShowAllCharts] = useState(false);

  // Khi click vào Tuyến đường ngập ở danh sách dưới, tự động nhảy trạm biểu đồ và map
  const handleSelectRoad = (road, idx) => {
    setSelectedStationIdx(idx);
    if (onSelectLocation) {
      // Tâm điểm ngập của tuyến đường (Node 3 hoặc tâm)
      const centerNode = road.nodes && road.nodes.length >= 3 ? road.nodes[2] : null;
      if (centerNode) {
        onSelectLocation({
          name: road.name,
          district: road.district,
          latitude: centerNode.latitude,
          longitude: centerNode.longitude
        });
      } else if (severeLocations && severeLocations[idx]) {
        onSelectLocation(severeLocations[idx]);
      }
    }
  };

  const activeStation = tides && tides.length > 0 ? (tides[selectedStationIdx] || tides[0]) : null;

  return (
    <aside style={{
      position: 'absolute',
      top: '16px',
      left: '16px',
      bottom: '16px',
      width: '400px',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      borderRadius: '24px',
      padding: '22px 18px',
      overflowY: 'auto',
      pointerEvents: 'auto'
    }} className="glass-sidebar">
      
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '18px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #0284c7 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(6, 182, 212, 0.45)'
        }}>
          <Droplets size={22} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '17px', fontWeight: 800, letterSpacing: '-0.3px', color: '#ffffff' }}>
            HCM Flood Tracker
          </h1>
          <p style={{ fontSize: '10px', fontWeight: 600, letterSpacing: '1px', color: '#94a3b8', textTransform: 'uppercase' }}>
            Smart City Hydrology Network
          </p>
        </div>
      </div>

      {/* Section: 10 Hydrological Charts */}
      <div style={{ marginBottom: '18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} color="#38bdf8" />
            <h2 style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
              Hydrological Charts ({tides?.length || 10})
            </h2>
          </div>
          <button 
            onClick={() => setShowAllCharts(!showAllCharts)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#38bdf8',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            {showAllCharts ? (
              <>Thu gọn <ChevronUp size={12} /></>
            ) : (
              <>Xem tất cả <ChevronDown size={12} /></>
            )}
          </button>
        </div>

        {/* Thanh cuộn chọn nhanh 10 trạm (Pills Selector) */}
        {tides && tides.length > 0 && (
          <div style={{
            display: 'flex',
            gap: '6px',
            overflowX: 'auto',
            paddingBottom: '8px',
            marginBottom: '10px',
            scrollbarWidth: 'none'
          }}>
            {tides.map((st, i) => {
              const isSelected = i === selectedStationIdx;
              return (
                <button
                  key={st.station_id}
                  onClick={() => {
                    setSelectedStationIdx(i);
                    if (roads && roads[i]) {
                      handleSelectRoad(roads[i], i);
                    } else if (severeLocations && severeLocations[i] && onSelectLocation) {
                      onSelectLocation(severeLocations[i]);
                    }
                  }}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '8px',
                    fontSize: '11px',
                    fontWeight: 600,
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    background: isSelected ? 'rgba(2, 132, 199, 0.4)' : 'rgba(255, 255, 255, 0.05)',
                    border: isSelected ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.08)',
                    color: isSelected ? '#38bdf8' : '#94a3b8'
                  }}
                >
                  #{i + 1} {st.name.split('(')[0].trim()}
                </button>
              );
            })}
          </div>
        )}

        {/* Chế độ hiển thị biểu đồ */}
        {tides && tides.length > 0 ? (
          showAllCharts ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '320px', overflowY: 'auto' }}>
              {tides.map((station) => (
                <TideChart key={station.station_id} station={station} />
              ))}
            </div>
          ) : (
            activeStation && <TideChart station={activeStation} />
          )
        ) : (
          <div style={{ padding: '16px', textAlign: 'center', color: '#64748b', fontSize: '12px' }}>
            Đang đồng bộ dữ liệu thủy văn...
          </div>
        )}
      </div>

      {/* Section: 10 Tuyến đường ngập trọng điểm */}
      <div style={{ marginBottom: '16px', flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={14} color="#facc15" />
            <h2 style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
              Tuyến đường ngập ({roads?.length || severeLocations?.length || 10})
            </h2>
          </div>
          <span style={{ fontSize: '11px', color: '#94a3b8' }}>
            50 Trạm IoT
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {(roads && roads.length > 0 ? roads : severeLocations)?.map((item, idx) => {
            const isRoad = !!item.coordinates;
            const severityKey = item.severity || 'SAFE';
            const styleCfg = SEVERITY_COLORS[severityKey] || SEVERITY_COLORS.SAFE;
            const isSelected = idx === selectedStationIdx;

            const name = item.name;
            const district = item.district;
            const maxWater = isRoad ? `${item.max_water_cm}cm` : `${(item.water_level_m * 100).toFixed(0)}cm`;
            const lengthKm = isRoad ? `${item.length_km} km` : '3.5 km';

            return (
              <div 
                key={item.id || idx} 
                onClick={() => handleSelectRoad(item, idx)}
                className="glass-card"
                style={{
                  padding: '11px 13px',
                  borderRadius: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  border: isSelected ? `1px solid ${styleCfg.color}88` : undefined,
                  background: isSelected ? `${styleCfg.color}15` : undefined
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: styleCfg.color, boxShadow: `0 0 8px ${styleCfg.color}` }} />
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9' }}>
                      {name}
                    </span>
                    <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                      ({district})
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '3px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ 
                      fontWeight: 800, 
                      fontFamily: 'Space Grotesk', 
                      color: styleCfg.color,
                      fontSize: '13px'
                    }}>
                      ↑ {maxWater}
                    </span>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>•</span>
                    <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                      {lengthKm} • 5 trạm IoT
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    letterSpacing: '0.4px',
                    padding: '3px 7px',
                    borderRadius: '6px',
                    backgroundColor: styleCfg.bg,
                    color: styleCfg.color,
                    border: `1px solid ${styleCfg.border}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {severityKey === 'CRITICAL' ? <Flame size={11} /> : <AlertTriangle size={11} />}
                    {severityKey}
                  </span>
                  <ChevronRight size={14} color="#64748b" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Status Legend (Phân loại Neon chuẩn) */}
      <div style={{
        paddingTop: '12px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '6px',
        fontSize: '10px',
        fontWeight: 600
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#06b6d4' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4', boxShadow: '0 0 6px #06b6d4' }} />
          <span>&lt;20cm (An toàn)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#facc15' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#facc15', boxShadow: '0 0 6px #facc15' }} />
          <span>20–35cm (Cảnh báo)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#ff7b00' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ff7b00', boxShadow: '0 0 6px #ff7b00' }} />
          <span>35–50cm (Nguy cơ)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#ff0055' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ff0055', boxShadow: '0 0 6px #ff0055' }} />
          <span>&gt;50cm (Ngập sâu)</span>
        </div>
      </div>

    </aside>
  );
}
