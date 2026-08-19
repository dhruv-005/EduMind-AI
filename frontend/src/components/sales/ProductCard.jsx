import React from 'react'
import { FiStar, FiCheck, FiPackage } from 'react-icons/fi'
import { m, useReducedMotion } from 'framer-motion'
import { formatPrice } from '@utils/formatters'

function getMatchGrad(pct) {
  if (pct >= 80) return 'linear-gradient(135deg,#10b981,#06b6d4)'
  if (pct >= 60) return 'linear-gradient(135deg,#6366f1,#8b5cf6)'
  return 'linear-gradient(135deg,#f59e0b,#ec4899)'
}

export default function ProductCard({ product, compact = false }) {
  const shouldReduce = useReducedMotion()
  if (!product) return null
  const matchPct  = Math.round((product.match_score || 0) * 100)
  const matchGrad = getMatchGrad(matchPct)

  if (compact) {
    return (
      <div style={{
        background: 'var(--bg-card)', borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border)', padding: '12px',
        display: 'flex', gap: 10, alignItems: 'center',
        boxShadow: 'var(--shadow-card)',
      }}>
        <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.08))', border: '1px solid rgba(99,102,241,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <FiPackage size={17} strokeWidth={1.5} style={{ color: '#6366f1' }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 700, color: 'var(--ink)', margin: '0 0 1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', letterSpacing: '-0.01em' }}>{product.name}</p>
          <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 12, fontWeight: 700, background: matchGrad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>{formatPrice(product.price || product.final_price)}</p>
        </div>
        <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 800, padding: '3px 9px', borderRadius: 'var(--radius-full)', background: matchGrad, color: '#ffffff', flexShrink: 0, boxShadow: '0 2px 8px rgba(99,102,241,0.3)' }}>
          {matchPct}%
        </span>
      </div>
    )
  }

  return (
    <m.div
      whileHover={shouldReduce ? undefined : { y: -6, boxShadow: '0 20px 60px rgba(0,0,0,0.12), 0 0 40px rgba(99,102,241,0.15)' }}
      transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', padding: '20px', boxShadow: 'var(--shadow-card)', overflow: 'hidden', position: 'relative' }}
    >
      {/* Match progress bar */}
      <div style={{ position: 'absolute', top: 0, left: 0, width: `${matchPct}%`, height: 3, background: matchGrad, transition: 'width 0.6s ease' }} />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14, gap: 10, marginTop: 8 }}>
        <div>
          <h4 style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 15, fontWeight: 800, color: 'var(--ink)', margin: '0 0 3px', letterSpacing: '-0.02em' }}>{product.name}</h4>
          {product.brand && <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--ink-muted)', margin: 0 }}>{product.brand}</p>}
        </div>
        <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 800, padding: '4px 10px', borderRadius: 'var(--radius-full)', background: matchGrad, color: '#ffffff', flexShrink: 0, whiteSpace: 'nowrap', boxShadow: '0 2px 8px rgba(99,102,241,0.3)' }}>
          {matchPct}% match
        </span>
      </div>

      {/* Price */}
      <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 24, fontWeight: 800, background: matchGrad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: '0 0 14px', letterSpacing: '-0.03em', lineHeight: 1 }}>
        {formatPrice(product.final_price || product.price)}
      </p>

      {/* Match reasons */}
      {product.match_reasons?.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14 }}>
          {product.match_reasons.slice(0, 3).map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 18, height: 18, borderRadius: '50%', background: 'linear-gradient(135deg,#10b981,#06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 2px 6px rgba(16,185,129,0.3)' }}>
                <FiCheck size={10} strokeWidth={3} color="#ffffff" />
              </div>
              <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--ink-soft)' }}>{r}</span>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 7, height: 7, borderRadius: '50%', background: product.in_stock ? '#10b981' : '#f43f5e', boxShadow: product.in_stock ? '0 0 6px rgba(16,185,129,0.4)' : 'none', flexShrink: 0 }} />
          <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 600, color: 'var(--ink-muted)' }}>
            {product.in_stock ? 'In Stock' : 'Out of Stock'}
          </span>
        </div>
        {product.rating && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <FiStar size={12} strokeWidth={1.5} style={{ color: '#f59e0b', fill: '#f59e0b' }} />
            <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 12, fontWeight: 700, color: 'var(--ink-soft)' }}>{product.rating}</span>
          </div>
        )}
      </div>
    </m.div>
  )
}
