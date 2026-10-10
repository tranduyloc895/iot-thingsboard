import React, { useState, useEffect } from 'react';
import { User, LayoutGrid } from 'lucide-react';

export default function TopBar() {
  const [timeStr, setTimeStr] = useState('');
  const [dateStr, setDateStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-GB'));
      const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
      setDateStr(`${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{
      position: 'absolute',
      top: '20px',
      right: '20px',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      background: 'rgba(14, 17, 23, 0.85)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      padding: '8px 16px',
      borderRadius: '16px',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)'
    }}>
      {/* Live Indicator */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        background: 'rgba(16, 185, 129, 0.12)',
        borderRadius: '8px',
        border: '1px solid rgba(16, 185, 129, 0.25)'
      }}>
        <span style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          background: '#10b981',
          boxShadow: '0 0 10px #10b981'
        }} />
        <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '1px', color: '#10b981' }}>
          LIVE
        </span>
      </div>

      {/* Clock */}
      <div style={{ textAlign: 'center', minWidth: '95px' }}>
        <div style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'Space Grotesk', color: '#ffffff' }}>
          {timeStr}
        </div>
        <div style={{ fontSize: '9px', fontWeight: 600, letterSpacing: '0.5px', color: '#94a3b8' }}>
          {dateStr}
        </div>
      </div>

      {/* Admin Profile */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        paddingLeft: '12px',
        borderLeft: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#cbd5e1', fontSize: '12px', fontWeight: 600 }}>
          <User size={15} color="#94a3b8" />
          <span>admin</span>
        </div>
        <LayoutGrid size={15} color="#64748b" style={{ cursor: 'pointer' }} />
      </div>
    </div>
  );
}
