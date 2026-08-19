import React, { useEffect, useRef } from 'react'
import { m, useReducedMotion, useSpring, useTransform, animate } from 'framer-motion'
import { LeadBadge } from '@components/ui/Badge'

function AnimatedScore({ score, gradient }) {
  const shouldReduce = useReducedMotion()
  const ref = useRef(null)
  useEffect(() => {
    if (!ref.current) return
    if (shouldReduce) { ref.current.textContent = score; return }
    const ctrl = animate(0, score, { duration: 0.8, ease: [0.25, 0.1, 0.25, 1], onUpdate: v => { if (ref.current) ref.current.textContent = Math.round(v) } })
    return ctrl.stop
  }, [score])
  return (
    <span ref={ref} style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 30, fontWeight: 800, background: gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', lineHeight: 1, letterSpacing: '-0.04em' }}>
      {score}
    </span>
  )
}

function getLeadConfig(score) {
  if (score >= 80) return { gradient: 'linear-gradient(135deg,#f43f5e,#ec4899)', glow: 'rgba(244,63,94,0.4)' }
  if (score >= 60) return { gradient: 'linear-gradient(135deg,#f59e0b,#f43f5e)', glow: 'rgba(245,158,11,0.4)' }
  if (score >= 40) return { gradient: 'linear-gradient(135deg,#6366f1,#8b5cf6)', glow: 'rgba(99,102,241,0.4)' }
  return              { gradient: 'linear-gradient(135deg,#64748b,#94a3b8)', glow: 'rgba(100,116,139,0.3)' }
}

export default function LeadScoreMeter({ leadScore }) {
  const shouldReduce = useReducedMotion()
  if (!leadScore) return null
  const { total_score = 0, budget_score = 0, intent_score = 0, authority_score = 0, urgency_score = 0, category = 'cold', next_action = '' } = leadScore
  const cfg = getLeadConfig(total_score)
  const breakdown = [{ label: 'Budget', score: budget_score, max: 25 }, { label: 'Intent', score: intent_score, max: 25 }, { label: 'Authority', score: authority_score, max: 25 }, { label: 'Urgency', score: urgency_score, max: 25 }]
  const circumference = 2 * Math.PI * 38
  const spring    = useSpring(0, { stiffness: 50, damping: 15 })
  const dashOffset= useTransform(spring, v => circumference - (v / 100) * circumference)
  useEffect(() => { spring.set(total_score) }, [total_score])

  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', padding: '20px', boxShadow: 'var(--shadow-card)', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: cfg.gradient }} />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h4 style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 800, color: 'var(--ink)', margin: 0, letterSpacing: '-0.02em' }}>Lead Score</h4>
        <LeadBadge category={category} />
      </div>

      <div style={{ display: 'flex', gap: 18, alignItems: 'center' }}>
        {/* Circle */}
        <div style={{ flexShrink: 0, position: 'relative', width: 100, height: 100 }}>
          {!shouldReduce && (
            <div style={{ position: 'absolute', inset: -8, borderRadius: '50%', background: `radial-gradient(circle, ${cfg.glow} 0%, transparent 70%)`, filter: 'blur(12px)', opacity: 0.6, pointerEvents: 'none' }} />
          )}
          <svg width={100} height={100} style={{ transform: 'rotate(-90deg)', position: 'relative', zIndex: 1 }}>
            <circle cx={50} cy={50} r={38} fill="none" stroke="var(--bg-tertiary)" strokeWidth={8} />
            <m.circle
              cx={50} cy={50} r={38} fill="none"
              stroke="url(#leadGrad)" strokeWidth={8} strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={shouldReduce ? circumference - (total_score / 100) * circumference : dashOffset}
            />
            <defs>
              <linearGradient id="leadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={category === 'hot' ? '#f43f5e' : category === 'warm' ? '#f59e0b' : category === 'cool' ? '#6366f1' : '#64748b'} />
                <stop offset="100%" stopColor={category === 'hot' ? '#ec4899' : category === 'warm' ? '#f43f5e' : category === 'cool' ? '#8b5cf6' : '#94a3b8'} />
              </linearGradient>
            </defs>
          </svg>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <AnimatedScore score={total_score} gradient={cfg.gradient} />
          </div>
        </div>

        {/* Bars */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 9 }}>
          {breakdown.map(item => (
            <div key={item.label}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 600, color: 'var(--ink-muted)' }}>{item.label}</span>
                <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 800, background: cfg.gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  {item.score}/{item.max}
                </span>
              </div>
              <div style={{ height: 6, background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <m.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.score / item.max) * 100}%` }}
                  transition={shouldReduce ? { duration: 0 } : { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
                  style={{ height: '100%', background: cfg.gradient, borderRadius: 'var(--radius-full)', boxShadow: `0 0 10px ${cfg.glow}` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {next_action && (
        <div style={{ marginTop: 14, padding: '11px 14px', background: 'linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.06))', borderRadius: 'var(--radius-md)', borderLeft: '3px solid #6366f1' }}>
          <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 12, fontWeight: 600, color: '#6366f1', margin: 0, lineHeight: 1.5 }}>
            💡 {next_action}
          </p>
        </div>
      )}
    </div>
  )
}
