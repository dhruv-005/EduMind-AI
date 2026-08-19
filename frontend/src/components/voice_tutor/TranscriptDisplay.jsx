import React, { useRef, useEffect } from 'react'
import { m, useReducedMotion } from 'framer-motion'

const bubbleVariants = {
  initial: { opacity: 0, y: 10, scale: 0.96 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] } },
}

export default function TranscriptDisplay({ history }) {
  const bottomRef    = useRef(null)
  const shouldReduce = useReducedMotion()

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [history])

  if (!history || history.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 24px', gap: 14, textAlign: 'center' }}>
        <div style={{
          width: 64, height: 64, borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.08))',
          border: '1px solid rgba(99,102,241,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28,
        }}>
          🎙️
        </div>
        <div>
          <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 15, fontWeight: 700, color: 'var(--ink)', margin: '0 0 4px', letterSpacing: '-0.02em' }}>
            Ready to chat
          </p>
          <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--ink-muted)', margin: 0, fontStyle: 'italic' }}>
            Start speaking to begin the session
          </p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, maxHeight: 420, overflowY: 'auto', padding: '4px 0' }}>
      {history.map((turn, i) => {
        const isStudent = turn.role === 'student'
        return (
          <m.div key={i}
            variants={shouldReduce ? undefined : bubbleVariants}
            initial="initial" animate="animate"
            style={{
              display: 'flex', gap: 10, flexDirection: isStudent ? 'row-reverse' : 'row',
              alignItems: 'flex-end',
            }}
          >
            <div style={{
              width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
              background: isStudent ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'linear-gradient(135deg,#8b5cf6,#ec4899)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 14,
              boxShadow: isStudent ? '0 4px 12px rgba(99,102,241,0.3)' : '0 4px 12px rgba(139,92,246,0.3)',
            }}>
              {isStudent ? '🧑' : '🤖'}
            </div>

            <div style={{
              maxWidth: '72%', padding: '12px 16px',
              borderRadius: isStudent
                ? 'var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg)'
                : 'var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm)',
              background: isStudent
                ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                : 'var(--bg-card)',
              border: isStudent ? 'none' : '1px solid var(--border)',
              boxShadow: isStudent
                ? '0 4px 16px rgba(99,102,241,0.3)'
                : 'var(--shadow-card)',
            }}>
              <p style={{
                fontFamily: 'Inter, sans-serif', fontSize: 13.5, lineHeight: 1.6,
                color: isStudent ? '#ffffff' : 'var(--ink)', margin: 0,
              }}>
                {turn.text}
              </p>
              {turn.timestamp && (
                <p style={{
                  fontFamily: 'Inter, sans-serif', fontSize: 10, margin: '5px 0 0',
                  color: isStudent ? 'rgba(255,255,255,0.6)' : 'var(--ink-muted)',
                  textAlign: 'right',
                }}>
                  {new Date(turn.timestamp).toLocaleTimeString()}
                </p>
              )}
            </div>
          </m.div>
        )
      })}
      <div ref={bottomRef} />
    </div>
  )
}
