import React, { useState } from 'react';
import TideChart from './TideChart';
import { Droplets, AlertTriangle, ChevronRight, Activity, Flame, ChevronDown, ChevronUp, MapPin, Waves, Navigation } from 'lucide-react';

const SEVERITY_COLORS = {
  SAFE: {
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.16)',
    border: 'rgba(6, 182, 212, 0.35)',
    label: 'SAFE'
  },
  ALERT: {
    color: '#facc15',
    bg: 'rgba(250, 204, 21, 0.16)',
    border: 'rgba(250, 204, 21, 0.35)',
    label: 'ALERT'
  },
  WARNING: {
    color: '#ff7b00',
    bg: 'rgba(255, 123, 0, 0.20)',
    border: 'rgba(255, 123, 0, 0.4)',
    label: 'WARNING'
  },
  CRITICAL: {
    color: '#ff0055',
    bg: 'rgba(255, 0, 85, 0.24)',
    border: 'rgba(255, 0, 85, 0.5)',
    label: 'CRITICAL'
  }
};

export default function Sidebar({ tides = [], severeLocations = [], roads = [], zones = [], summary, weather, onSelectLocation }) {
  const [selectedStationIdx, setSelectedStationIdx] = useState(0);
  const [showAllCharts, setShowAllCharts] = useState(false);
  const [activeTab, setActiveTab] = useState('ALL'); // 'ALL', 'ROADS', 'ZONES'

  // Hợp nhất danh sách 10 điểm (6 đường + 4 khu vực)
  const allItems = [
    ...roads.map(r => ({ ...r, category: 'ROAD' })),
    ...zones.map(z => ({ ...z, category: 'ZONE' }))
  ];

  const displayedItems = activeTab === 'ROADS' 
    ? allItems.filter(i => i.category === 'ROAD')
    : activeTab === 'ZONES' 
      ? allItems.filter(i => i.category === 'ZONE')
      : allItems;

  const handleSelectItem = (item, idx) => {
    setSelectedStationIdx(idx);
    if (onSelectLocation) {
      onSelectLocation(item);
    }
  };

  const activeStation = tides && tides.length > 0 ? (tides[selectedStationIdx] || tides[0]) : null;

  // Tóm tắt triều cường toàn thành phố
  const maxTide = tides.length > 0 ? Math.max(...tides.map(t => t.current_level)) : 0;
  const maxTideStation = tides.find(t => t.current_level === maxTide) || null;
  const cityTideAlert = maxTide >= 1.7
    ? { label: 'BĐ III + Xả lũ', color: '#ff0055', bg: 'rgba(255,0,85,0.18)' }
    : maxTide >= 1.5
      ? { label: 'Báo động III', color: '#f43f5e', bg: 'rgba(244,63,94,0.15)' }
      : maxTide >= 1.35
        ? { label: 'Báo động II', color: '#fb923c', bg: 'rgba(251,146,60,0.14)' }
        : maxTide >= 1.1
          ? { label: 'Báo động I', color: '#facc15', bg: 'rgba(250,204,21,0.13)' }
          : { label: 'Bình thường', color: '#10b981', bg: 'rgba(16,185,129,0.12)' };
  const rainfall_mm = weather?.rainfall_mm ?? null;

  return (
    <aside style={{
      position: 'absolute',
      top: '16px',
      left: '16px',
      bottom: '16px',
      width: '410px',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      borderRadius: '24px',
      padding: '20px 18px',
      overflowY: 'auto',
      pointerEvents: 'auto'
    }} className="glass-sidebar">
      
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div style={{
          width: '40px',
          height: '40px',
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
          <h1 style={{ fontSize: '16px', fontWeight: 800, letterSpacing: '-0.3px', color: '#ffffff' }}>
            HCM Flood Warning
          </h1>
          <p style={{ fontSize: '10px', fontWeight: 600, letterSpacing: '0.8px', color: '#94a3b8', textTransform: 'uppercase' }}>
            Smart City Hydrology Network
          </p>
        </div>
      </div>

      {/* Section: Dự báo Triều cường */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} color="#38bdf8" />
            <h2 style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
              Dự báo Triều cường TP.HCM
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

        {/* ── City Tide Summary Card ── */}
        {tides.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '6px',
            marginBottom: '10px',
            padding: '10px 12px',
            background: `${cityTideAlert.color}10`,
            border: `1px solid ${cityTideAlert.color}30`,
            borderRadius: '12px'
          }}>
            {/* Mực triều cao nhất */}
            <div>
              <div style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>
                🌊 Mực triều cao nhất
              </div>
              <div style={{ fontSize: '18px', fontWeight: 800, color: cityTideAlert.color, fontFamily: 'Space Grotesk', lineHeight: 1 }}>
                {maxTide.toFixed(2)}m
              </div>
              <div style={{ fontSize: '9px', color: '#94a3b8', marginTop: '2px' }}>
                {maxTideStation?.name?.split('(')[0]?.trim()}
              </div>
            </div>

            {/* Cấp báo động */}
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
                Cấp độ
              </div>
              <span style={{
                display: 'inline-block',
                fontSize: '10.5px', fontWeight: 700,
                padding: '3px 9px', borderRadius: '8px',
                background: cityTideAlert.bg,
                color: cityTideAlert.color,
                border: `1px solid ${cityTideAlert.color}40`
              }}>
                {cityTideAlert.label}
              </span>
              <div style={{ fontSize: '9px', color: '#94a3b8', marginTop: '4px' }}>
                Đỉnh lúc {maxTideStation?.peak_hour}h00 • {maxTideStation?.trend === 'UP' ? '↑ Đang dâng' : '↓ Đang rút'}
              </div>
            </div>

            {/* Mưa hiện tại */}
            {rainfall_mm != null && (
              <div style={{ gridColumn: '1 / -1', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '6px', marginTop: '2px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600 }}>🌧️ Lượng mưa hiện tại</span>
                  <span style={{
                    fontSize: '10px', fontWeight: 700,
                    color: rainfall_mm >= 25 ? '#fb923c' : rainfall_mm >= 10 ? '#facc15' : '#10b981'
                  }}>
                    {rainfall_mm.toFixed(1)} mm/h
                    {rainfall_mm >= 25 && <span style={{ marginLeft: '4px', fontSize: '9px', color: '#fb923c' }}>(Mưa to → Nguy cơ ngập cao)</span>}
                    {rainfall_mm >= 10 && rainfall_mm < 25 && <span style={{ marginLeft: '4px', fontSize: '9px', color: '#facc15' }}>(Mưa vừa)</span>}
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Thanh cuộn chọn nhanh trạm */}
        {tides && tides.length > 0 && (
          <div style={{
            display: 'flex',
            gap: '6px',
            overflowX: 'auto',
            paddingBottom: '6px',
            marginBottom: '8px',
            scrollbarWidth: 'none'
          }}>
            {tides.map((st, i) => {
              const isSelected = i === selectedStationIdx;
              return (
                <button
                  key={st.station_id}
                  onClick={() => {
                    setSelectedStationIdx(i);
                    if (allItems[i]) {
                      handleSelectItem(allItems[i], i);
                    }
                  }}
                  style={{
                    padding: '3px 9px',
                    borderRadius: '7px',
                    fontSize: '10px',
                    fontWeight: 600,
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    background: isSelected ? 'rgba(2, 132, 199, 0.45)' : 'rgba(255, 255, 255, 0.05)',
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

        {/* Biểu đồ */}
        {tides && tides.length > 0 ? (
          showAllCharts ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '320px', overflowY: 'auto' }}>
              {tides.map((station) => (
                <TideChart key={station.station_id} station={station} rainfall_mm={rainfall_mm} />
              ))}
            </div>
          ) : (
            activeStation && <TideChart station={activeStation} rainfall_mm={rainfall_mm} />
          )
        ) : (
          <div style={{ padding: '14px', textAlign: 'center', color: '#64748b', fontSize: '11px' }}>
            Đang đồng bộ dữ liệu thủy văn...
          </div>
        )}
      </div>

      {/* Section: Sơ đồ Cảnh báo & Phân loại Tuyến đường vs Khu vực ngập */}
      <div style={{ marginBottom: '14px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={14} color="#facc15" />
            <h2 style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
              Điểm ngập cảnh báo ({allItems.length || 10})
            </h2>
          </div>
          <span style={{ fontSize: '10px', color: '#94a3b8' }}>
            50 Trạm IoT
          </span>
        </div>

        {/* Tabs phân loại: Tất cả / Tuyến đường / Khu vực */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '6px',
          marginBottom: '10px',
          background: 'rgba(255, 255, 255, 0.04)',
          padding: '3px',
          borderRadius: '10px'
        }}>
          <button
            onClick={() => setActiveTab('ALL')}
            style={{
              padding: '5px 0',
              borderRadius: '7px',
              fontSize: '11px',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              background: activeTab === 'ALL' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
              color: activeTab === 'ALL' ? '#38bdf8' : '#94a3b8',
              transition: 'all 0.2s'
            }}
          >
            Tất cả ({allItems.length})
          </button>
          <button
            onClick={() => setActiveTab('ROADS')}
            style={{
              padding: '5px 0',
              borderRadius: '7px',
              fontSize: '11px',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              background: activeTab === 'ROADS' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
              color: activeTab === 'ROADS' ? '#38bdf8' : '#94a3b8',
              transition: 'all 0.2s'
            }}
          >
            Đường ({roads.length})
          </button>
          <button
            onClick={() => setActiveTab('ZONES')}
            style={{
              padding: '5px 0',
              borderRadius: '7px',
              fontSize: '11px',
              fontWeight: 700,
              border: 'none',
              cursor: 'pointer',
              background: activeTab === 'ZONES' ? 'rgba(244, 63, 94, 0.2)' : 'transparent',
              color: activeTab === 'ZONES' ? '#f43f5e' : '#94a3b8',
              transition: 'all 0.2s'
            }}
          >
            Khu vực ({zones.length})
          </button>
        </div>

        {/* Danh sách các tuyến đường & khu vực ngập */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', overflowY: 'auto' }}>
          {displayedItems.map((item, idx) => {
            const isRoad = item.category === 'ROAD';
            const severityKey = item.severity || 'SAFE';
            const styleCfg = SEVERITY_COLORS[severityKey] || SEVERITY_COLORS.SAFE;
            const isSelected = idx === selectedStationIdx;

            const name = item.name;
            const district = item.district;
            const maxWater = `${item.max_water_cm}cm`;
            const dimension = isRoad ? `${item.length_km} km` : `~${item.area_km2} km²`;

            return (
              <div 
                key={item.id || idx} 
                onClick={() => handleSelectItem(item, idx)}
                className="glass-card"
                style={{
                  padding: '10px 12px',
                  borderRadius: '12px',
                  cursor: 'pointer',
                  border: isSelected ? `1px solid ${styleCfg.color}99` : undefined,
                  background: isSelected ? `${styleCfg.color}15` : undefined
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '13px' }}>{isRoad ? '🛣️' : '🌊'}</span>
                      <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#f1f5f9' }}>
                        {name}
                      </span>
                      <span style={{ fontSize: '10.5px', color: '#94a3b8' }}>
                        ({district})
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ 
                        fontWeight: 800, 
                        fontFamily: 'Space Grotesk', 
                        color: styleCfg.color,
                        fontSize: '12.5px'
                      }}>
                        ↑ {maxWater}
                      </span>
                      <span style={{ color: '#64748b' }}>•</span>
                      <span style={{ color: '#94a3b8' }}>
                        {dimension} • 5 trạm IoT
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{
                      fontSize: '9.5px',
                      fontWeight: 700,
                      letterSpacing: '0.4px',
                      padding: '2px 6px',
                      borderRadius: '5px',
                      backgroundColor: styleCfg.bg,
                      color: styleCfg.color,
                      border: `1px solid ${styleCfg.border}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px'
                    }}>
                      {severityKey === 'CRITICAL' ? <Flame size={10} /> : <AlertTriangle size={10} />}
                      {severityKey}
                    </span>
                    <ChevronRight size={13} color="#64748b" />
                  </div>
                </div>

                {/* Khuyến cáo lộ trình ngắn gọn */}
                {item.avoid_advice && (
                  <div style={{
                    marginTop: '6px',
                    paddingTop: '6px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                    fontSize: '10.5px',
                    color: '#cbd5e1',
                    lineHeight: '1.3'
                  }}>
                    <span style={{ color: styleCfg.color, fontWeight: 700 }}>💡 Lộ trình: </span>
                    {item.avoid_advice}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Status Legend (Phân loại Neon chuẩn) */}
      <div style={{
        paddingTop: '10px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '4px',
        fontSize: '9.5px',
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
