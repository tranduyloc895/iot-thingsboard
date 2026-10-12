import React, { useState } from 'react';
import TideChart from './TideChart';
import { Droplets, AlertTriangle, ChevronRight, Activity, Flame, ChevronDown, ChevronUp } from 'lucide-react';

export default function Sidebar({ tides, severeLocations, summary, onSelectLocation }) {
  const [selectedStationIdx, setSelectedStationIdx] = useState(0);
  const [showAllCharts, setShowAllCharts] = useState(false);

  // Khi click vào Hotspot ở danh sách dưới, tự động nhảy trạm biểu đồ tương ứng ở trên
  const handleSelectHotspot = (loc, idx) => {
    setSelectedStationIdx(idx);
    if (onSelectLocation) {
      onSelectLocation(loc);
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
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
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
      <div style={{ marginBottom: '20px' }}>
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
                    if (severeLocations && severeLocations[i] && onSelectLocation) {
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
            // Hiển thị tất cả 10 biểu đồ theo danh sách cuộn
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '350px', overflowY: 'auto' }}>
              {tides.map((station, i) => (
                <TideChart key={station.station_id} station={station} />
              ))}
            </div>
          ) : (
            // Hiển thị biểu đồ trạm đang chọn với độ chi tiết cao
            activeStation && <TideChart station={activeStation} />
          )
        ) : (
          <div style={{ padding: '16px', textAlign: 'center', color: '#64748b', fontSize: '12px' }}>
            Đang đồng bộ dữ liệu thủy văn...
          </div>
        )}
      </div>

      {/* Section: 10 Severe Flood Hotspots */}
      <div style={{ marginBottom: '16px', flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h2 style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
            Severe Flood Hotspots ({severeLocations?.length || 10})
          </h2>
          <span style={{ fontSize: '11px', color: '#94a3b8' }}>
            Thời gian thực
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {severeLocations?.map((loc, idx) => {
            const isCrit = loc.severity === 'CRITICAL';
            const isWarn = loc.severity === 'WARNING';
            const badgeColor = isCrit ? '#f43f5e' : (isWarn ? '#f59e0b' : '#38bdf8');
            const badgeBg = isCrit ? 'rgba(244, 63, 94, 0.15)' : (isWarn ? 'rgba(245, 158, 11, 0.15)' : 'rgba(56, 189, 248, 0.15)');
            const isSelected = idx === selectedStationIdx;

            return (
              <div 
                key={loc.id} 
                onClick={() => handleSelectHotspot(loc, idx)}
                className="glass-card"
                style={{
                  padding: '11px 13px',
                  borderRadius: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  border: isSelected ? '1px solid rgba(56, 189, 248, 0.5)' : undefined,
                  background: isSelected ? 'rgba(14, 165, 233, 0.12)' : undefined
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ color: badgeColor, fontSize: '12px' }}>📍</span>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9' }}>
                      {loc.name}
                    </span>
                    <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                      ({loc.district})
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '3px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ 
                      fontWeight: 800, 
                      fontFamily: 'Space Grotesk', 
                      color: badgeColor,
                      fontSize: '13px'
                    }}>
                      ↑ {loc.water_level_m}m
                    </span>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>•</span>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>
                      Cập nhật {loc.minutes_ago} phút trước
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
                    backgroundColor: badgeBg,
                    color: badgeColor,
                    border: `1px solid ${badgeColor}33`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {isCrit ? <Flame size={11} /> : <AlertTriangle size={11} />}
                    {loc.severity}
                  </span>
                  <ChevronRight size={14} color="#64748b" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Status Legend */}
      <div style={{
        paddingTop: '12px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '11px',
        fontWeight: 600
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#10b981' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px #10b981' }} />
          <span>SAFE (&lt;25cm)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#f59e0b' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 6px #f59e0b' }} />
          <span>ALERT (25–40cm)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#f43f5e' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f43f5e', boxShadow: '0 0 6px #f43f5e' }} />
          <span>CRITICAL (&gt;40cm)</span>
        </div>
      </div>

    </aside>
  );
}
