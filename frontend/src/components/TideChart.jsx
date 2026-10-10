import React from 'react';

export default function TideChart({ station }) {
  if (!station || !station.hourly_data) return null;

  const data = station.hourly_data;
  const maxLevel = Math.max(...data.map(d => d.level), 2.0);
  const minLevel = 0.0;
  
  // Kích thước SVG
  const width = 310;
  const height = 110;
  const paddingX = 25;
  const paddingY = 15;

  const getX = (hour) => paddingX + (hour / 24) * (width - 2 * paddingX);
  const getY = (level) => height - paddingY - ((level - minLevel) / (maxLevel - minLevel)) * (height - 2 * paddingY);

  // Tạo đường cong mượt (Smooth Bezier Spline)
  let pathD = `M ${getX(data[0].hour)} ${getY(data[0].level)}`;
  for (let i = 0; i < data.length - 1; i++) {
    const x0 = getX(data[i].hour);
    const y0 = getY(data[i].level);
    const x1 = getX(data[i + 1].hour);
    const y1 = getY(data[i + 1].level);
    const cpX1 = x0 + (x1 - x0) / 2;
    const cpX2 = x1 - (x1 - x0) / 2;
    pathD += ` C ${cpX1} ${y0}, ${cpX2} ${y1}, ${x1} ${y1}`;
  }

  // Khép kín vùng để tô Gradient
  const areaD = `${pathD} L ${getX(data[data.length - 1].hour)} ${height - paddingY} L ${getX(data[0].hour)} ${height - paddingY} Z`;

  // Tìm điểm đỉnh (Peak point)
  const peakHour = station.peak_hour ?? 11;
  const peakLevel = station.peak_level ?? 1.5;
  const peakX = getX(peakHour);
  const peakY = getY(peakLevel);

  const isHigh = station.status === 'HIGH' || station.status === 'CRITICAL';
  const gradId = `tide-grad-${station.station_id}`;

  return (
    <div style={{
      background: 'rgba(18, 22, 31, 0.7)',
      borderRadius: '16px',
      padding: '14px 16px',
      border: '1px solid rgba(255, 255, 255, 0.05)',
      marginBottom: '12px'
    }}>
      {/* Header của Trạm */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '12px', opacity: 0.7 }}>📍</span>
            <span style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.5px', color: '#e2e8f0' }}>
              {station.name}
            </span>
          </div>
          <div style={{ fontSize: '12px', marginTop: '3px' }}>
            <span style={{ color: '#94a3b8' }}>Current: </span>
            <span style={{ 
              fontWeight: 700, 
              color: isHigh ? '#f43f5e' : '#10b981', 
              fontFamily: 'Space Grotesk' 
            }}>
              {station.current_level}m {station.trend === 'UP' ? '↑' : '↓'}
            </span>
          </div>
        </div>

        <span style={{
          fontSize: '11px',
          fontWeight: 700,
          padding: '3px 8px',
          borderRadius: '6px',
          letterSpacing: '0.5px',
          backgroundColor: isHigh ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
          color: isHigh ? '#f43f5e' : '#10b981',
          border: `1px solid ${isHigh ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
        }}>
          {station.status}
        </span>
      </div>

      {/* SVG Chart */}
      <div style={{ position: 'relative', width: '100%', height: `${height}px` }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: '100%', overflow: 'visible' }}>
          <defs>
            <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isHigh ? '#f43f5e' : '#10b981'} stopOpacity="0.45" />
              <stop offset="50%" stopColor={isHigh ? '#fb7185' : '#34d399'} stopOpacity="0.15" />
              <stop offset="100%" stopColor="#090a0f" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines mờ */}
          <line x1={paddingX} y1={getY(1.5)} x2={width - paddingX} y2={getY(1.5)} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
          <line x1={paddingX} y1={getY(0.8)} x2={width - paddingX} y2={getY(0.8)} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />

          {/* Area Gradient Fill */}
          <path d={areaD} fill={`url(#${gradId})`} />

          {/* Đường cong Spline chính */}
          <path 
            d={pathD} 
            fill="none" 
            stroke={isHigh ? '#f43f5e' : '#10b981'} 
            strokeWidth="2.5" 
            strokeLinecap="round" 
          />

          {/* Đường gióng xuống từ Peak */}
          <line 
            x1={peakX} 
            y1={peakY} 
            x2={peakX} 
            y2={height - paddingY} 
            stroke="rgba(255,255,255,0.25)" 
            strokeDasharray="2 2" 
          />

          {/* Chấm tròn Peak */}
          <circle cx={peakX} cy={peakY} r="4" fill="#ffffff" stroke={isHigh ? '#f43f5e' : '#10b981'} strokeWidth="2.5" />

          {/* Badge nhãn Peak */}
          <g transform={`translate(${peakX - 16}, ${peakY - 18})`}>
            <rect width="32" height="14" rx="4" fill="rgba(0,0,0,0.7)" stroke="rgba(255,255,255,0.15)" />
            <text x="16" y="10" textAnchor="middle" fill="#ffffff" fontSize="9" fontWeight="600" fontFamily="Space Grotesk">
              Peak
            </text>
          </g>

          {/* Trục hoành giờ */}
          {[0, 6, 12, 18, 24].map((hr) => (
            <text 
              key={hr} 
              x={getX(hr)} 
              y={height - 2} 
              textAnchor="middle" 
              fill="#64748b" 
              fontSize="9" 
              fontFamily="Space Grotesk"
            >
              {hr}
            </text>
          ))}
        </svg>
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2px' }}>
        <span style={{ fontSize: '9px', color: '#64748b', fontFamily: 'Space Grotesk' }}>Hours (24h Forecast)</span>
      </div>
    </div>
  );
}
