import React, { useState, useEffect } from 'react';
import { User, LayoutGrid, Activity, Radio, Wifi, WifiOff } from 'lucide-react';

// Mô tả mưa theo mm/h
function getRainLabel(mm) {
  if (mm >= 50) return { label: 'Mưa rất to', color: '#f43f5e', icon: '⛈️' };
  if (mm >= 25) return { label: 'Mưa to', color: '#fb923c', icon: '🌧️' };
  if (mm >= 10) return { label: 'Mưa vừa', color: '#facc15', icon: '🌦️' };
  if (mm >= 2) return { label: 'Mưa nhỏ', color: '#4ade80', icon: '🌂' };
  return { label: 'Không mưa', color: '#94a3b8', icon: '🌤️' };
}

export default function TopBar({ 
  weather, 
  wsStatus = 'CONNECTED', 
  lastSyncTime, 
  packetCount = 0, 
  isPinging = false 
}) {
  const [timeStr, setTimeStr] = useState('');
  const [dateStr, setDateStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('vi-VN'));
      const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
      setDateStr(`${now.getDate()}/${months[now.getMonth()]}/${now.getFullYear()}`);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // Lấy dữ liệu thời tiết hoặc dùng fallback
  const rain = weather?.rainfall_mm ?? 18.5;
  const temp = weather?.temperature_c ?? 31.0;
  const hum = weather?.humidity_percent ?? 80;
  const { label: rainLabel, color: rainColor, icon: rainIcon } = getRainLabel(rain);

  const cardStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '5px 11px',
    borderRadius: '10px',
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
  };

  const isConnected = wsStatus === 'CONNECTED';
  const isConnecting = wsStatus === 'CONNECTING';

  // Format sync timestamp
  const displaySync = lastSyncTime 
    ? (lastSyncTime.includes(' ') ? lastSyncTime.split(' ')[1] : lastSyncTime)
    : '--:--:--';

  return (
    <div style={{
      position: 'absolute',
      top: '14px',
      right: '20px',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      background: 'rgba(9, 10, 15, 0.88)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      padding: '7px 14px',
      borderRadius: '18px',
      border: '1px solid rgba(255, 255, 255, 0.09)',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.6)',
      flexWrap: 'wrap',
    }}>

      {/* ─── LIVE REALTIME indicator (Gắn với WebSocket thật) ─── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '5px 10px',
        background: isConnected 
          ? (isPinging ? 'rgba(16, 185, 129, 0.24)' : 'rgba(16, 185, 129, 0.12)')
          : isConnecting 
            ? 'rgba(245, 158, 11, 0.14)' 
            : 'rgba(244, 63, 94, 0.16)',
        borderRadius: '10px',
        border: `1px solid ${isConnected 
          ? (isPinging ? 'rgba(52, 211, 153, 0.7)' : 'rgba(16, 185, 129, 0.35)') 
          : isConnecting 
            ? 'rgba(245, 158, 11, 0.4)' 
            : 'rgba(244, 63, 94, 0.5)'}`,
        transition: 'all 0.25s ease-in-out',
        cursor: 'default'
      }}>
        {/* Beacon Dot */}
        <span 
          className={isConnected ? 'beacon-pulse' : ''}
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isConnected ? '#10b981' : isConnecting ? '#f59e0b' : '#f43f5e',
            boxShadow: isConnected 
              ? (isPinging ? '0 0 12px #34d399' : '0 0 6px #10b981') 
              : 'none',
            transition: 'box-shadow 0.2s ease, transform 0.2s ease',
            transform: isPinging ? 'scale(1.25)' : 'scale(1)',
          }} 
        />
        
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ 
              fontSize: '10.5px', 
              fontWeight: 800, 
              letterSpacing: '1px', 
              color: isConnected ? '#10b981' : isConnecting ? '#f59e0b' : '#f43f5e' 
            }}>
              {isConnected ? 'REALTIME' : isConnecting ? 'CONNECTING' : 'OFFLINE'}
            </span>
            {isConnected && (
              <span style={{
                fontSize: '8.5px',
                fontWeight: 700,
                color: '#34d399',
                background: 'rgba(16, 185, 129, 0.2)',
                padding: '1px 4px',
                borderRadius: '4px'
              }}>
                1s
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ─── Server Sync Time Pill ─── */}
      <div style={{
        ...cardStyle,
        border: isPinging ? '1px solid rgba(56, 189, 248, 0.4)' : cardStyle.border,
        transition: 'border-color 0.25s ease'
      }}>
        <Activity size={13} color="#38bdf8" />
        <div>
          <div style={{ 
            fontSize: '11px', 
            fontWeight: 800, 
            color: '#38bdf8', 
            fontFamily: 'Space Grotesk', 
            lineHeight: 1,
            fontVariantNumeric: 'tabular-nums'
          }}>
            {displaySync}
          </div>
          <div style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600, marginTop: '1px' }}>
            Đồng bộ server
          </div>
        </div>
      </div>

      {/* ─── Divider ─── */}
      <span style={{ width: '1px', height: '22px', background: 'rgba(255,255,255,0.1)' }} />

      {/* ─── 🌧 Lượng mưa ─── */}
      <div style={{ ...cardStyle, border: `1px solid ${rainColor}30` }}>
        <span style={{ fontSize: '14px' }}>{rainIcon}</span>
        <div>
          <div style={{ 
            fontSize: '11px', 
            fontWeight: 800, 
            color: rainColor, 
            fontFamily: 'Space Grotesk', 
            lineHeight: 1,
            fontVariantNumeric: 'tabular-nums'
          }}>
            {rain.toFixed(1)} mm/h
          </div>
          <div style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600, marginTop: '1px' }}>{rainLabel}</div>
        </div>
      </div>

      {/* ─── 🌡 Nhiệt độ ─── */}
      <div style={cardStyle}>
        <span style={{ fontSize: '13px' }}>🌡️</span>
        <div>
          <div style={{ 
            fontSize: '11px', 
            fontWeight: 800, 
            color: '#fbbf24', 
            fontFamily: 'Space Grotesk', 
            lineHeight: 1,
            fontVariantNumeric: 'tabular-nums'
          }}>
            {temp.toFixed(1)}°C
          </div>
          <div style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600, marginTop: '1px' }}>Nhiệt độ</div>
        </div>
      </div>

      {/* ─── 💧 Độ ẩm ─── */}
      <div style={cardStyle}>
        <span style={{ fontSize: '13px' }}>💧</span>
        <div>
          <div style={{ 
            fontSize: '11px', 
            fontWeight: 800, 
            color: '#38bdf8', 
            fontFamily: 'Space Grotesk', 
            lineHeight: 1,
            fontVariantNumeric: 'tabular-nums'
          }}>
            {hum.toFixed(0)}%
          </div>
          <div style={{ fontSize: '9px', color: '#94a3b8', fontWeight: 600, marginTop: '1px' }}>Độ ẩm</div>
        </div>
      </div>

      {/* ─── Divider ─── */}
      <span style={{ width: '1px', height: '22px', background: 'rgba(255,255,255,0.1)' }} />

      {/* ─── Clock ─── */}
      <div style={{ textAlign: 'center', minWidth: '82px' }}>
        <div style={{ 
          fontSize: '13px', 
          fontWeight: 700, 
          fontFamily: 'Space Grotesk', 
          color: '#ffffff', 
          letterSpacing: '0.5px',
          fontVariantNumeric: 'tabular-nums'
        }}>
          {timeStr}
        </div>
        <div style={{ fontSize: '9px', fontWeight: 600, letterSpacing: '0.3px', color: '#94a3b8', marginTop: '1px' }}>
          {dateStr}
        </div>
      </div>

      {/* ─── Divider ─── */}
      <span style={{ width: '1px', height: '22px', background: 'rgba(255,255,255,0.1)' }} />

      {/* ─── Admin ─── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#cbd5e1', fontSize: '11px', fontWeight: 600 }}>
          <User size={14} color="#94a3b8" />
          <span>admin</span>
        </div>
        <LayoutGrid size={14} color="#64748b" style={{ cursor: 'pointer' }} />
      </div>
    </div>
  );
}

