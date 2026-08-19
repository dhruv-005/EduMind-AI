/* ============================================================
   EDUMIND AI — PROGRESS BAR COMPONENT
   ============================================================ */

import React, { useEffect, useState } from 'react'

export default function ProgressBar({
  value       = 0,
  max         = 100,
  label       = '',
  showValue   = true,
  color       = 'var(--accent-primary)',
  height      = '6px',
  animated    = true,
  style       = {},
}) {
  const [width, setWidth] = useState(0)
  const percent = Math.min(100, Math.max(0, (value / max) * 100))

  // Animate in on mount
  useEffect(() => {
    const timer = setTimeout(() => setWidth(percent), 50)
    return () => clearTimeout(timer)
  }, [percent])

  // Color based on value if using score color
  const barColor = color === 'score'
    ? percent >= 80
      ? 'var(--term-green)'
      : percent >= 50
        ? 'var(--term-amber)'
        : 'var(--term-red)'
    : color

  return (
    <div style={{ ...style }}>

      {/* Label row */}
      {(label || showValue) && (
        <div style={{
          display:        'flex',
          justifyContent: 'space-between',
          alignItems:     'center',
          marginBottom:   'var(--space-2)',
        }}>
          {label && (
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              color:         'var(--muted)',
            }}>
              {label}
            </span>
          )}
          {showValue && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize:   'var(--fs-nano)',
              fontWeight: 700,
              color:      barColor,
            }}>
              {Math.round(percent)}%
            </span>
          )}
        </div>
      )}

      {/* Track */}
      <div style={{
        height:     height,
        background: 'var(--surface)',
        border:     '1px solid var(--border-subtle)',
        overflow:   'hidden',
        position:   'relative',
      }}>
        {/* Fill */}
        <div style={{
          height:     '100%',
          width:      `${width}%`,
          background: barColor,
          transition: animated ? 'width 1s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
          position:   'relative',
        }}>
          {/* Shimmer on fill */}
          {animated && width > 0 && (
            <div style={{
              position:   'absolute',
              inset:      0,
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
              animation:  'shimmer 1.5s infinite',
              backgroundSize: '200% 100%',
            }} />
          )}
        </div>
      </div>
    </div>
  )
}

/* Multi-segment progress bar */
export function SegmentedProgress({ segments = [], style = {} }) {
  return (
    <div style={{
      display: 'flex',
      gap: '2px',
      height: '8px',
      ...style,
    }}>
      {segments.map((seg, i) => (
        <div
          key={i}
          style={{
            flex: seg.value,
            background: seg.color || 'var(--accent-primary)',
            transition: 'flex 1s ease',
            position: 'relative',
          }}
          title={`${seg.label}: ${seg.value}%`}
        />
      ))}
    </div>
  )
}
