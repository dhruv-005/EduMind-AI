	/* ============================================================
   EDUMIND AI — BADGE COMPONENT
   ============================================================ */

import React from 'react'

const VARIANTS = {
  default: { color: 'var(--ink)',        bg: 'var(--surface)',       border: 'var(--ink)'        },
  accent:  { color: '#ffffff',           bg: 'var(--accent-primary)',border: 'var(--accent-primary)'},
  cyber:   { color: 'var(--accent-cyber)',bg: 'var(--accent-cyber-dim)',border: 'var(--accent-cyber)'},
  green:   { color: 'var(--term-green)', bg: 'var(--term-green-dim)',border: 'var(--term-green)'  },
  amber:   { color: 'var(--term-amber)', bg: 'var(--term-amber-dim)',border: 'var(--term-amber)'  },
  red:     { color: 'var(--term-red)',   bg: 'var(--term-red-dim)',  border: 'var(--term-red)'    },
  muted:   { color: 'var(--muted)',      bg: 'var(--surface)',       border: 'var(--border-subtle)'},
}

export default function Badge({
  children,
  variant = 'default',
  dot     = false,
  pulse   = false,
  style   = {},
  ...props
}) {
  const v = VARIANTS[variant] || VARIANTS.default

  return (
    <span
      style={{
        display:       'inline-flex',
        alignItems:    'center',
        gap:           '0.3rem',
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-wider)',
        fontWeight:    700,
        padding:       '0.2rem 0.55rem',
        border:        `1px solid ${v.border}`,
        background:    v.bg,
        color:         v.color,
        lineHeight:    1.4,
        ...style,
      }}
      {...props}
    >
      {dot && (
        <span style={{
          width:        '6px',
          height:       '6px',
          borderRadius: '50%',
          background:   v.color,
          display:      'inline-block',
          flexShrink:   0,
          ...(pulse && {
            boxShadow: `0 0 6px ${v.color}`,
            animation: 'pulseDot 2s ease-in-out infinite',
          }),
        }} />
      )}
      {children}
    </span>
  )
}
