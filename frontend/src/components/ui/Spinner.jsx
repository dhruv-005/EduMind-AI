/* ============================================================
   EDUMIND AI — SPINNER COMPONENT
   ============================================================ */

import React from 'react'

export default function Spinner({
  size    = 24,
  color   = 'var(--accent-primary)',
  label   = 'Loading...',
  center  = false,
  style   = {},
}) {
  const spinner = (
    <div style={{
      display:    'inline-flex',
      alignItems: 'center',
      gap:        'var(--space-3)',
      ...style,
    }}>
      {/* Spinning ring */}
      <div style={{
        width:        `${size}px`,
        height:       `${size}px`,
        border:       `2px solid var(--border-subtle)`,
        borderTopColor: color,
        borderRadius: '50%',
        animation:    'spin 0.7s linear infinite',
        flexShrink:   0,
      }} />

      {/* Label */}
      {label && (
        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wider)',
          color:         'var(--muted)',
          animation:     'blink 1.5s ease-in-out infinite',
        }}>
          {label}
        </span>
      )}
    </div>
  )

  if (center) {
    return (
      <div style={{
        display:        'flex',
        justifyContent: 'center',
        alignItems:     'center',
        padding:        'var(--space-12)',
      }}>
        {spinner}
      </div>
    )
  }

  return spinner
}

/* Dots spinner variant */
export function SpinnerDots({ color = 'var(--accent-primary)', size = 8 }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '4px',
    }}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            width:        `${size}px`,
            height:       `${size}px`,
            borderRadius: '50%',
            background:   color,
            animation:    `pulseDot 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
    </div>
  )
}
