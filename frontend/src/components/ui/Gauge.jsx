import React, { useEffect, useRef } from 'react'
import { m, useReducedMotion, animate } from 'framer-motion'

const TOTAL_TICKS = 40
const RADIUS      = 52
const CX = 70, CY = 70
const START_DEG = 220
const SWEEP_DEG = 280

function degToRad(deg) { return (deg * Math.PI) / 180 }

function tickCoords(i) {
  const angle = START_DEG + (i / (TOTAL_TICKS - 1)) * SWEEP_DEG
  const rad   = degToRad(angle)
  const inner = RADIUS - 8
  return {
    x1: CX + inner * Math.cos(rad), y1: CY + inner * Math.sin(rad),
    x2: CX + RADIUS * Math.cos(rad), y2: CY + RADIUS * Math.sin(rad),
  }
}

function AnimatedCounter({ value, gradient, fontSize = 22 }) {
  const shouldReduce = useReducedMotion()
  const ref = useRef(null)
  useEffect(() => {
    if (!ref.current) return
    if (shouldReduce) { ref.current.textContent = value.toFixed(1); return }
    const ctrl = animate(0, value, {
      duration: 0.8, ease: [0.25, 0.1, 0.25, 1],
      onUpdate: v => { if (ref.current) ref.current.textContent = v.toFixed(1) },
    })
    return ctrl.stop
  }, [value])
  return (
    <span ref={ref} style={{
      fontFamily: '"Plus Jakarta Sans", sans-serif',
      fontSize, fontWeight: 800,
      background: gradient || 'linear-gradient(135deg, #6366f1, #8b5cf6)',
      WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
      lineHeight: 1, letterSpacing: '-0.04em',
    }}>
      {value.toFixed(1)}
    </span>
  )
}

function getTickGradient(pct) {
  if (pct >= 0.8) return { stroke: '#10b981', glow: 'rgba(16,185,129,0.6)'  }
  if (pct >= 0.6) return { stroke: '#6366f1', glow: 'rgba(99,102,241,0.6)'  }
  if (pct >= 0.4) return { stroke: '#f59e0b', glow: 'rgba(245,158,11,0.6)'  }
  return              { stroke: '#f43f5e', glow: 'rgba(244,63,94,0.6)'   }
}

export default function Gauge({ value = 0, max = 100, size = 150, label, minLabel, maxLabel }) {
  const shouldReduce = useReducedMotion()
  const pct          = Math.max(0, Math.min(value / max, 1))
  const activeTicks  = Math.round(pct * (TOTAL_TICKS - 1))
  const { stroke, glow } = getTickGradient(pct)
  const gradient = pct >= 0.8
    ? 'linear-gradient(135deg, #10b981, #06b6d4)'
    : pct >= 0.6
      ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
      : pct >= 0.4
        ? 'linear-gradient(135deg, #f59e0b, #ec4899)'
        : 'linear-gradient(135deg, #f43f5e, #8b5cf6)'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        {/* Glow halo */}
        {!shouldReduce && (
          <div style={{
            position: 'absolute',
            top: '30%', left: '50%', transform: 'translate(-50%, -50%)',
            width: size * 0.6, height: size * 0.6,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${glow} 0%, transparent 70%)`,
            filter: 'blur(12px)',
            opacity: 0.6,
            transition: 'background 0.5s ease',
            pointerEvents: 'none',
          }} />
        )}

        <svg viewBox="0 0 140 140" width={size} height={size} aria-hidden="true" style={{ overflow: 'visible' }}>
          {/* Background ticks */}
          {Array.from({ length: TOTAL_TICKS }).map((_, i) => {
            const c = tickCoords(i)
            return (
              <line key={`bg-${i}`}
                x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2}
                stroke="rgba(148,163,184,0.2)"
                strokeWidth={i % 5 === 0 ? 3 : 2}
                strokeLinecap="round"
              />
            )
          })}

          {/* Active ticks with staggered animation */}
          {Array.from({ length: TOTAL_TICKS }).map((_, i) => {
            if (i > activeTicks) return null
            const c = tickCoords(i)
            const progress = i / activeTicks
            const alpha    = 0.4 + progress * 0.6

            return (
              <m.line
                key={`active-${i}`}
                x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2}
                stroke={stroke}
                strokeWidth={i % 5 === 0 ? 3.5 : 2.5}
                strokeLinecap="round"
                initial={shouldReduce ? undefined : { opacity: 0, scale: 0 }}
                animate={shouldReduce ? undefined : { opacity: alpha, scale: 1 }}
                transition={shouldReduce ? undefined : {
                  delay: i * 0.015,
                  duration: 0.2,
                  ease: [0.34, 1.56, 0.64, 1],
                }}
                style={{ filter: `drop-shadow(0 0 3px ${stroke})` }}
              />
            )
          })}
        </svg>

        {/* Center content */}
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          paddingBottom: 12, gap: 2,
        }}>
          <AnimatedCounter value={value} gradient={gradient} fontSize={size * 0.22} />
          {max !== 100 && (
            <span style={{
              fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
              color: 'var(--ink-muted)',
            }}>
              / {max}
            </span>
          )}
        </div>
      </div>

      {label && (
        <span style={{
          fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 700,
          background: gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          letterSpacing: '-0.01em',
        }}>
          {label}
        </span>
      )}

      {(minLabel || maxLabel) && (
        <div style={{
          display: 'flex', justifyContent: 'space-between', width: size,
          fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 500,
          color: 'var(--ink-muted)',
        }}>
          <span>{minLabel || '0'}</span>
          <span>{maxLabel || max}</span>
        </div>
      )}
    </div>
  )
}
