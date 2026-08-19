import React from 'react'
import { m, useReducedMotion } from 'framer-motion'
import { StatCard } from '@components/ui/Card'
import Badge from '@components/ui/Badge'
import { FiShield, FiAlertTriangle, FiXCircle, FiCheckCircle, FiEye, FiActivity } from 'react-icons/fi'

const listVariants = { animate: { transition: { staggerChildren: 0.08, delayChildren: 0.05 } } }
const cardVariants = { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] } } }

const PILLARS = [
  { num:'01', name:'Content Safety',   color:'#10b981', grad:'linear-gradient(135deg,#10b981,#06b6d4)' },
  { num:'02', name:'Audit Trail',      color:'#6366f1', grad:'linear-gradient(135deg,#6366f1,#8b5cf6)' },
  { num:'03', name:'Human Oversight',  color:'#8b5cf6', grad:'linear-gradient(135deg,#8b5cf6,#ec4899)' },
  { num:'04', name:'Bias Detection',   color:'#f59e0b', grad:'linear-gradient(135deg,#f59e0b,#f43f5e)' },
  { num:'05', name:'Rate Limiting',    color:'#06b6d4', grad:'linear-gradient(135deg,#06b6d4,#6366f1)' },
  { num:'06', name:'Data Privacy',     color:'#ec4899', grad:'linear-gradient(135deg,#ec4899,#8b5cf6)' },
  { num:'07', name:'Model Versioning', color:'#f43f5e', grad:'linear-gradient(135deg,#f43f5e,#f59e0b)' },
]

export default function GovernanceStats({ stats }) {
  const shouldReduce = useReducedMotion()
  if (!stats) return null

  return (
    <m.div
      variants={shouldReduce ? undefined : listVariants}
      initial="initial" animate="animate"
      style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
    >
      {/* Stat cards */}
      <m.div variants={shouldReduce ? undefined : cardVariants}
        style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px,1fr))', gap: 12 }}>
        <StatCard title="Total Requests" value={(stats.total_requests||0).toLocaleString()} icon={FiActivity} gradient="linear-gradient(135deg,#6366f1,#8b5cf6)" color="#6366f1" />
        <StatCard title="Passed"         value={(stats.passed       ||0).toLocaleString()} icon={FiCheckCircle}   gradient="linear-gradient(135deg,#10b981,#06b6d4)" color="#10b981" />
        <StatCard title="Flagged"        value={(stats.flagged       ||0).toLocaleString()} icon={FiAlertTriangle} gradient="linear-gradient(135deg,#f59e0b,#f43f5e)" color="#f59e0b" />
        <StatCard title="Blocked"        value={(stats.blocked       ||0).toLocaleString()} icon={FiXCircle}       gradient="linear-gradient(135deg,#f43f5e,#ec4899)" color="#f43f5e" />
      </m.div>

      {/* Pillars */}
      <m.div variants={shouldReduce ? undefined : cardVariants}>
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', padding: '22px', boxShadow: 'var(--shadow-card)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'linear-gradient(90deg,#6366f1,#8b5cf6,#06b6d4,#10b981)' }} />
          <h4 style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 14, fontWeight: 800, color: 'var(--ink)', margin: '0 0 16px', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 8 }}>
            <FiShield size={16} strokeWidth={2} style={{ color: '#6366f1' }} />
            Governance Pillars
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px,1fr))', gap: 10 }}>
            {PILLARS.map(p => (
              <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 14px', background: `linear-gradient(135deg, ${p.color}0d, ${p.color}06)`, borderRadius: 'var(--radius-md)', border: `1px solid ${p.color}25`, transition: 'all 0.2s ease' }}>
                <div style={{ width: 24, height: 24, borderRadius: 'var(--radius-sm)', background: p.grad, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: `0 2px 8px ${p.color}40` }}>
                  <FiShield size={12} strokeWidth={2} color="#ffffff" />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 700, color: 'var(--ink)', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', letterSpacing: '-0.01em' }}>{p.name}</p>
                  <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 9, fontWeight: 700, background: p.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Active</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </m.div>

      {/* Human review queue */}
      <m.div variants={shouldReduce ? undefined : cardVariants}>
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', padding: '22px', boxShadow: 'var(--shadow-card)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'linear-gradient(90deg,#6366f1,#8b5cf6)' }} />
          <h4 style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 14, fontWeight: 800, color: 'var(--ink)', margin: '0 0 16px', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: 8 }}>
            <FiEye size={16} strokeWidth={2} style={{ color: '#6366f1' }} />
            Human Review Queue
          </h4>
          <div style={{ display: 'flex', gap: 28 }}>
            {[{ label:'Pending', value:stats.human_reviews_pending||0, grad:'linear-gradient(135deg,#f59e0b,#f43f5e)', glow:'rgba(245,158,11,0.3)' }, { label:'Completed', value:stats.human_reviews_completed||0, grad:'linear-gradient(135deg,#10b981,#06b6d4)', glow:'rgba(16,185,129,0.3)' }].map(item => (
              <div key={item.label} style={{ textAlign: 'center' }}>
                <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 32, fontWeight: 800, background: item.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: '0 0 4px', lineHeight: 1, letterSpacing: '-0.04em', filter: `drop-shadow(0 0 8px ${item.glow})` }}>
                  {item.value}
                </p>
                <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 600, color: 'var(--ink-muted)', margin: 0 }}>{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </m.div>
    </m.div>
  )
}
