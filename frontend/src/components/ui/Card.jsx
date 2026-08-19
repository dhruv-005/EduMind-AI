/* ============================================================
   EDUMIND AI — CARD COMPONENT
   Neo-Brutalist hard shadow cards
   ============================================================ */

import React, { useState } from 'react'

const VARIANTS = {
  default: {
    background: 'var(--base)',
    border: 'var(--border)',
    shadow: 'var(--shadow)',
    shadowHover: 'var(--shadow-lg)',
  },
  surface: {
    background: 'var(--surface)',
    border: 'var(--border)',
    shadow: 'var(--shadow)',
    shadowHover: 'var(--shadow-lg)',
  },
  accent: {
    background: 'var(--base)',
    border: '3px solid var(--accent-primary)',
    shadow: 'var(--shadow-accent)',
    shadowHover: '10px 10px 0px var(--accent-primary)',
  },
  cyber: {
    background: 'var(--base)',
    border: '3px solid var(--accent-cyber)',
    shadow: 'var(--shadow-cyber)',
    shadowHover: '10px 10px 0px var(--accent-cyber)',
  },
  terminal: {
    background: 'var(--term-bg)',
    border: '1px solid rgba(255,255,255,0.08)',
    shadow: '6px 6px 0px #000000',
    shadowHover: '10px 10px 0px #000000',
  },
  green: {
    background: 'var(--base)',
    border: '3px solid var(--term-green)',
    shadow: 'var(--shadow-green)',
    shadowHover: '10px 10px 0px var(--term-green)',
  },
  flat: {
    background: 'var(--base)',
    border: 'var(--border-thin)',
    shadow: 'none',
    shadowHover: 'none',
  },
}

export default function Card({
  children,
  variant  = 'default',
  hoverable = false,
  padding  = 'var(--space-8)',
  style    = {},
  onClick,
  className = '',
  tag       = null,
  title     = null,
  action    = null,
  ...props
}) {
  const [isHovered, setIsHovered] = useState(false)
  const v = VARIANTS[variant] || VARIANTS.default

  const isClickable = !!onClick || hoverable

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => isClickable && setIsHovered(true)}
      onMouseLeave={() => isClickable && setIsHovered(false)}
      className={className}
      style={{
        background:  v.background,
        border:      v.border,
        boxShadow:   isHovered && isClickable ? v.shadowHover : v.shadow,
        transform:   isHovered && isClickable
          ? 'translate(-3px, -3px)'
          : 'translate(0, 0)',
        transition: 'transform 0.12s ease, box-shadow 0.12s ease',
        cursor:     onClick ? 'pointer' : 'default',
        position:   'relative',
        overflow:   'hidden',
        ...style,
      }}
      {...props}
    >
      {/* Tag */}
      {tag && (
        <div style={{
          padding: `calc(${padding} * 0.6) ${padding}`,
          borderBottom: v.border.includes('var(--border)') ? 'var(--border-thin)' : `1px solid ${v.border.split(' ').pop()}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <span style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wider)',
            color:         'var(--muted)',
          }}>
            {tag}
          </span>
          {action && action}
        </div>
      )}

      {/* Title */}
      {title && !tag && (
        <div style={{
          padding:       `${padding} ${padding} 0`,
          paddingBottom: 'var(--space-4)',
          borderBottom:  'var(--border-thin)',
          marginBottom:  'var(--space-4)',
          display:       'flex',
          alignItems:    'center',
          justifyContent:'space-between',
        }}>
          <span style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h4)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            color:         variant === 'terminal'
              ? 'var(--term-text)'
              : 'var(--ink)',
          }}>
            {title}
          </span>
          {action && action}
        </div>
      )}

      {/* Body */}
      <div style={{
        padding: tag || title ? `var(--space-4) ${padding} ${padding}` : padding,
      }}>
        {children}
      </div>
    </div>
  )
}
