/* ============================================================
   EDUMIND AI — BUTTON COMPONENT
   Neo-Brutalist hard shadow buttons
   ============================================================ */

import React from 'react'

const VARIANTS = {
  primary: {
    background: 'var(--accent-primary)',
    color: '#ffffff',
    borderColor: 'var(--accent-primary)',
    shadow: 'var(--shadow-accent)',
    shadowHover: '10px 10px 0px var(--accent-primary)',
  },
  secondary: {
    background: 'var(--base)',
    color: 'var(--ink)',
    borderColor: 'var(--ink)',
    shadow: 'var(--shadow)',
    shadowHover: 'var(--shadow-lg)',
  },
  cyber: {
    background: 'transparent',
    color: 'var(--accent-cyber)',
    borderColor: 'var(--accent-cyber)',
    shadow: 'var(--shadow-cyber)',
    shadowHover: '10px 10px 0px var(--accent-cyber)',
  },
  green: {
    background: 'transparent',
    color: 'var(--term-green)',
    borderColor: 'var(--term-green)',
    shadow: 'var(--shadow-green)',
    shadowHover: '10px 10px 0px var(--term-green)',
  },
  danger: {
    background: 'var(--term-red)',
    color: '#ffffff',
    borderColor: 'var(--term-red)',
    shadow: '6px 6px 0px rgba(255,45,85,0.4)',
    shadowHover: '10px 10px 0px rgba(255,45,85,0.6)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--muted)',
    borderColor: 'transparent',
    shadow: 'none',
    shadowHover: 'none',
  },
  surface: {
    background: 'var(--surface)',
    color: 'var(--ink)',
    borderColor: 'var(--ink)',
    shadow: 'var(--shadow)',
    shadowHover: 'var(--shadow-lg)',
  },
}

const SIZES = {
  sm: {
    fontSize: 'var(--fs-nano)',
    padding: '0.35rem 0.85rem',
    gap: '0.3rem',
  },
  md: {
    fontSize: 'var(--fs-data)',
    padding: '0.75rem 1.6rem',
    gap: '0.5rem',
  },
  lg: {
    fontSize: 'var(--fs-body)',
    padding: '1rem 2.2rem',
    gap: '0.6rem',
  },
  icon: {
    fontSize: 'var(--fs-data)',
    padding: '0.75rem',
    gap: '0',
  },
}

export default function Button({
  children,
  variant   = 'secondary',
  size      = 'md',
  disabled  = false,
  loading   = false,
  fullWidth = false,
  onClick,
  type      = 'button',
  className = '',
  style     = {},
  icon      = null,
  iconRight = null,
  ...props
}) {
  const v = VARIANTS[variant] || VARIANTS.secondary
  const s = SIZES[size]       || SIZES.md

  const [isHovered, setIsHovered] = React.useState(false)
  const [isActive,  setIsActive]  = React.useState(false)

  const computedStyle = {
    // Base
    fontFamily:    'var(--font-mono)',
    fontWeight:    700,
    textTransform: 'uppercase',
    letterSpacing: 'var(--ls-wide)',
    lineHeight:    1,
    whiteSpace:    'nowrap',
    cursor:        disabled || loading ? 'not-allowed' : 'pointer',
    display:       'inline-flex',
    alignItems:    'center',
    justifyContent:'center',
    textDecoration:'none',
    border:        `var(--border-width) solid ${v.borderColor}`,
    position:      'relative',
    userSelect:    'none',
    width:         fullWidth ? '100%' : 'auto',

    // Size
    fontSize:   s.fontSize,
    padding:    size === 'icon' ? s.padding : s.padding,
    gap:        s.gap,

    // Variant
    background: v.background,
    color:      v.color,

    // Shadow & Transform
    boxShadow: isActive
      ? 'var(--shadow-sm)'
      : isHovered && !disabled && !loading
        ? v.shadowHover
        : v.shadow,

    transform: isActive
      ? 'translate(2px, 2px)'
      : isHovered && !disabled && !loading
        ? 'translate(-3px, -3px)'
        : 'translate(0, 0)',

    // Disabled
    opacity:  disabled || loading ? 0.45 : 1,

    // Transition
    transition: 'transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease',

    // Ghost hover override
    ...(variant === 'ghost' && isHovered && {
      background: 'var(--surface)',
      transform:  'none',
    }),

    ...style,
  }

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => { setIsHovered(false); setIsActive(false) }}
      onMouseDown={() => setIsActive(true)}
      onMouseUp={() => setIsActive(false)}
      style={computedStyle}
      className={className}
      {...props}
    >
      {/* Loading spinner */}
      {loading && (
        <span style={{
          width:  '14px',
          height: '14px',
          border: `2px solid ${variant === 'primary' || variant === 'danger' ? 'rgba(255,255,255,0.3)' : 'var(--border-subtle)'}`,
          borderTopColor: variant === 'primary' || variant === 'danger'
            ? '#ffffff'
            : 'var(--accent-primary)',
          borderRadius: '50%',
          animation: 'spin 0.7s linear infinite',
          display: 'inline-block',
          flexShrink: 0,
        }} />
      )}

      {/* Left icon */}
      {!loading && icon && (
        <span style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          {icon}
        </span>
      )}

      {/* Label */}
      {children && (
        <span>{children}</span>
      )}

      {/* Right icon */}
      {!loading && iconRight && (
        <span style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          {iconRight}
        </span>
      )}
    </button>
  )
}
