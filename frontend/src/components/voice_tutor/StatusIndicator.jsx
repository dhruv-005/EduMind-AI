import React from 'react'
import { m, useReducedMotion } from 'framer-motion'

const STATUS = {
  idle:        { label: 'Ready',       gradient: 'linear-gradient(135deg,#64748b,#94a3b8)', glow: 'rgba(100,116,139,0.3)', pulse: false },
  connected:   { label: 'Connected',   gradient: 'linear-gradient(135deg,#10b981,#06b6d4)', glow: 'rgba(16,185,129,0.4)',  pulse: false },
  recording:   { label: 'Listening…',  gradient: 'linear-gradient(135deg,#6366f1,#8b5cf6)', glow: 'rgba(99,102,241,0.5)',  pulse: true  },
  processing:  { label: 'Processing…', gradient: 'linear-gradient(135deg,#f59e0b,#ec4899)', glow: 'rgba(245,158,11,0.5)',  pulse: true  },
  speaking:    { label: 'AI Speaking', gradient: 'linear-gradient(135deg,#8b5cf6,#ec4899)', glow: 'rgba(139,92,246,0.5)',  pulse: true  },
  interrupted: { label: 'Interrupted', gradient: 'linear-gradient(135deg,#f59e0b,#f43f5e)', glow: 'rgba(245,158,11,0.4)',  pulse: false },
  error:       { label: 'Error',       gradient: 'linear-gradient(135deg,#f43f5e,#ec4899)', glow: 'rgba(244,63,94,0.4)',   pulse: false },
}

export default function StatusIndicator({ status, isConnected }) {
  const shouldReduce = useReducedMotion()
  const key = isConnected ? (status || 'connected') : 'idle'
  const cfg = STATUS[key] || STATUS.idle

  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 10,
      padding: '8px 16px',
      background: 'var(--bg-card)',
      borderRadius: 'var(--radius-full)',
      border: '1px solid var(--border)',
      boxShadow: 'var(--shadow-card)',
    }}>
      {/* Animated dot */}
      <div style={{ position: 'relative', width: 10, height: 10 }}>
        {cfg.pulse && !shouldReduce && (
          <m.span
            animate={{ scale: [1, 2], opacity: [0.6, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeOut' }}
            style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              background: cfg.gradient,
            }}
          />
        )}
        <span style={{
          position: 'absolute', inset: 0, borderRadius: '50%',
          background: cfg.gradient,
          boxShadow: cfg.pulse ? `0 0 8px ${cfg.glow}` : 'none',
          transition: 'all 0.3s ease',
        }} />
      </div>

      <span style={{
        fontFamily: '"Plus Jakarta Sans", sans-serif',
        fontSize: 12, fontWeight: 700,
        background: cfg.gradient,
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        whiteSpace: 'nowrap', letterSpacing: '-0.01em',
      }}>
        {cfg.label}
      </span>
    </div>
  )
}
