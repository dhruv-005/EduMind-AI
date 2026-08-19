import React, { useEffect, useRef } from 'react'
import { m, useReducedMotion, animate } from 'framer-motion'
import { GradeBadge } from '@components/ui/Badge'

const TOTAL_TICKS = 40
const RADIUS = 52, CX = 70, CY = 70
const START_DEG = 220, SWEEP_DEG = 280

function degToRad(deg) { return (deg * Math.PI) / 180 }

function tickCoords(i) {
  const angle = START_DEG + (i / (TOTAL_TICKS - 1)) * SWEEP_DEG
  const rad   = degToRad(angle)
  return {
    x1: CX + (RADIUS - 8) * Math.cos(rad),
    y1: CY + (RADIUS - 8) * Math.sin(rad),
    x2: CX + RADIUS * Math.cos(rad),
    y2: CY + RADIUS * Math.sin(rad),
  }
}

function Counter({ value, gradient }) {
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
      fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 38, fontWeight: 800,
      background: gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
      lineHeight: 1, letterSpacing: '-0.04em',
    }}>
      {value.toFixed(1)}
    </span>
  )
}

function getConfig(score, max) {
  const t = score / max
  if (t >= 0.8) return { stroke: '#10b981', gradient: 'linear-gradient(135deg,#10b981,#06b6d4)', glow: 'rgba(16,185,129,0.5)', label: 'Excellent!' }
  if (t >= 0.7) return { stroke: '#06b6d4', gradient: 'linear-gradient(135deg,#06b6d4,#6366f1)', glow: 'rgba(6,182,212,0.5)',  label: 'Great work!'  }
  if (t >= 0.6) return { stroke: '#6366f1', gradient: 'linear-gradient(135deg,#6366f1,#8b5cf6)', glow: 'rgba(99,102,241,0.5)', label: 'Good job!'    }
  if (t >= 0.5) return { stroke: '#f59e0b', gradient: 'linear-gradient(135deg,#f59e0b,#f43f5e)', glow: 'rgba(245,158,11,0.5)', label: 'Keep going!'  }
  return              { stroke: '#f43f5e', gradient: 'linear-gradient(135deg,#f43f5e,#8b5cf6)', glow: 'rgba(244,63,94,0.5)',  label: 'Try again!'  }
}

export default function ScoreGauge({ score, maxScore = 10, grade, size = 160 }) {
  const shouldReduce = useReducedMotion()
  const pct          = Math.max(0, Math.min(score / maxScore, 1))
  const activeTicks  = Math.round(pct * (TOTAL_TICKS - 1))
  const cfg          = getConfig(score, maxScore)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        {/* Glow halo */}
        {!shouldReduce && (
          <div style={{
            position: 'absolute',
            top: '40%', left: '50%', transform: 'translate(-50%,-50%)',
            width: size * 0.7, height: size * 0.7,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${cfg.glow} 0%, transparent 70%)`,
            filter: 'blur(16px)', opacity: 0.7, pointerEvents: 'none',
            transition: 'all 0.5s ease',
          }} />
        )}

        <svg viewBox="0 0 140 140" width={size} height={size} aria-hidden="true" style={{ overflow: 'visible' }}>
          {/* BG ticks */}
          {Array.from({ length: TOTAL_TICKS }).map((_, i) => {
            const c = tickCoords(i)
            return <line key={`bg-${i}`} x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2} stroke="rgba(148,163,184,0.15)" strokeWidth={i % 5 === 0 ? 3 : 2} strokeLinecap="round" />
          })}

          {/* Active ticks */}
          {Array.from({ length: activeTicks + 1 }).map((_, i) => {
            const c       = tickCoords(i)
            const alpha   = 0.5 + (i / Math.max(activeTicks, 1)) * 0.5
            return (
              <m.line
                key={`active-${i}`}
                x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2}
                stroke={cfg.stroke}
                strokeWidth={i % 5 === 0 ? 3.5 : 2.5}
                strokeLinecap="round"
                initial={shouldReduce ? undefined : { opacity: 0 }}
                animate={shouldReduce ? undefined : { opacity: alpha }}
                transition={shouldReduce ? undefined : { delay: i * 0.012, duration: 0.2 }}
                style={{ filter: `drop-shadow(0 0 2px ${cfg.stroke})` }}
              />
            )
          })}
        </svg>

        {/* Center */}
        <div style={{
          position: 'absolute', inset: 0, display: 'flex',
          flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          paddingBottom: 14, gap: 3,
        }}>
          <Counter value={score} gradient={cfg.gradient} />
          <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--ink-muted)' }}>
            / {maxScore}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
        {grade && <GradeBadge grade={grade} />}
        <m.span
          initial={shouldReduce ? {} : { opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 700,
            background: cfg.gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.01em',
          }}
        >
          {cfg.label}
        </m.span>
      </div>
    </div>
  )
}
