import React from 'react';
import TideChart from './TideChart';
import { Droplets, AlertTriangle, ChevronRight, SlidersHorizontal, ShieldCheck, Flame } from 'lucide-react';

export default function Sidebar({ tides, severeLocations, summary, onSelectLocation }) {
  return (
    <aside style={{
      position: 'absolute',
      top: '16px',
      left: '16px',
      bottom: '16px',
      width: '380px',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      borderRadius: '24px',
      padding: '24px 20px',
      overflowY: 'auto',
      pointerEvents: 'auto'
    }} className="glass-sidebar">
      
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
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
          <h1 style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '-0.3px', color: '#ffffff' }}>
            HCM Flood Tracker
          </h1>
          <p style={{ fontSize: '10px', fontWeight: 600, letterSpacing: '1px', color: '#94a3b8', textTransform: 'uppercase' }}>
            Real-Time City Monitoring
          </p>
        </div>
      </div>

      {/* Section: Real-time Tide Charts */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
            Real-Time Tide Charts
          </h2>
          <span style={{ fontSize: '14px', color: '#64748b', cursor: 'pointer' }}>•••</span>
        </div>

        {tides && tides.length > 0 ? (
          tides.map(station => (
            <TideChart key={station.station_id} station={station} />
          ))
        ) : (
          <div style={{ padding: '16px', textAlign: 'center', color: '#64748b', fontSize: '12px' }}>
            Đang tải dữ liệu thủy triều...
          </div>
        )}
      </div>

      {/* Section: Severe Flood Locations */}
      <div style={{ marginBottom: '16px', flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.8px', color: '#cbd5e1', textTransform: 'uppercase' }}>
            Severe Flood Locations
          </h2>
          <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 600, cursor: 'pointer' }}>
            {severeLocations?.length || 0} Hotspots
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {severeLocations?.map(loc => {
            const isCrit = loc.severity === 'CRITICAL';
            const isWarn = loc.severity === 'WARNING';
            const badgeColor = isCrit ? '#f43f5e' : (isWarn ? '#f59e0b' : '#38bdf8');
            const badgeBg = isCrit ? 'rgba(244, 63, 94, 0.15)' : (isWarn ? 'rgba(245, 158, 11, 0.15)' : 'rgba(56, 189, 248, 0.15)');

            return (
              <div 
                key={loc.id} 
                onClick={() => onSelectLocation(loc)}
                className="glass-card"
                style={{
                  padding: '12px 14px',
                  borderRadius: '14px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ color: badgeColor, fontSize: '12px' }}>📍</span>
                    <span style={{ fontSize: '13px', fontWeight: 600, color: '#f1f5f9' }}>
                      {loc.district} <span style={{ color: '#94a3b8', fontWeight: 400 }}>({loc.name})</span>
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ 
                      fontWeight: 700, 
                      fontFamily: 'Space Grotesk', 
                      color: badgeColor,
                      fontSize: '13px'
                    }}>
                      {loc.water_level_m}m
                    </span>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>•</span>
                    <span style={{ fontSize: '11px', color: '#64748b' }}>
                      {loc.minutes_ago} min ago
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    letterSpacing: '0.4px',
                    padding: '3px 8px',
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
        paddingTop: '14px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '11px',
        fontWeight: 600
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#10b981' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px #10b981' }} />
          <span>SAFE</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#f59e0b' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 6px #f59e0b' }} />
          <span>ALERT</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#f43f5e' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f43f5e', boxShadow: '0 0 6px #f43f5e' }} />
          <span>CRITICAL</span>
        </div>
      </div>

    </aside>
  );
}
