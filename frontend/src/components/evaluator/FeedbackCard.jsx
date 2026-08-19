import React from 'react'
import { m, useReducedMotion } from 'framer-motion'
import { FiTrendingUp, FiCheckCircle, FiAlertTriangle, FiXCircle, FiTarget } from 'react-icons/fi'

const listVariants = { animate: { transition: { staggerChildren: 0.08, delayChildren: 0.05 } } }
const cardVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] } },
}

function ConceptChip({ text, type }) {
  const styles = {
    correct: { bg: 'rgba(16,185,129,0.1)',  color: '#10b981', border: 'rgba(16,185,129,0.2)'  },
    missing: { bg: 'rgba(245,158,11,0.1)',  color: '#f59e0b', border: 'rgba(245,158,11,0.2)'  },
    wrong:   { bg: 'rgba(244,63,94,0.1)',   color: '#f43f5e', border: 'rgba(244,63,94,0.2)'   },
  }[type] || { bg: 'var(--bg-secondary)', color: 'var(--ink-muted)', border: 'var(--border)' }

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '4px 11px', borderRadius: 'var(--radius-full)',
      background: styles.bg, color: styles.color,
      border: `1px solid ${styles.border}`,
      fontFamily: '"Plus Jakarta Sans", sans-serif',
      fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap',
      letterSpacing: '-0.01em',
    }}>
      {text}
    </span>
  )
}

function SectionCard({ title, icon: Icon, gradient, children }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      padding: '20px',
      boxShadow: 'var(--shadow-card)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 2,
        background: gradient || 'linear-gradient(90deg, #6366f1, #8b5cf6)',
      }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 'var(--radius-md)',
          background: gradient || 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(99,102,241,0.3)',
          flexShrink: 0,
        }}>
          {Icon && <Icon size={15} strokeWidth={2} color="#ffffff" />}
        </div>
        <h4 style={{
          fontFamily: '"Plus Jakarta Sans", sans-serif',
          fontSize: 14, fontWeight: 800, color: 'var(--ink)', margin: 0, letterSpacing: '-0.02em',
        }}>
          {title}
        </h4>
      </div>
      {children}
    </div>
  )
}

export default function FeedbackCard({ result }) {
  const shouldReduce = useReducedMotion()
  if (!result) return null

  const {
    feedback = '', improvement_suggestions = [],
    concept_analysis = {}, subject_specific_notes,
    semantic_similarity, confidence_score,
  } = result

  return (
    <m.div
      variants={shouldReduce ? undefined : listVariants}
      initial="initial" animate="animate"
      style={{ display: 'flex', flexDirection: 'column', gap: 14 }}
    >
      {/* Feedback */}
      <m.div variants={shouldReduce ? undefined : cardVariants}>
        <div style={{
          background: 'linear-gradient(135deg, rgba(99,102,241,0.06), rgba(139,92,246,0.04))',
          border: '1px solid rgba(99,102,241,0.15)',
          borderRadius: 'var(--radius-lg)',
          padding: '20px', position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'linear-gradient(90deg,#6366f1,#8b5cf6,#06b6d4)' }} />
          <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 14, lineHeight: 1.75, color: 'var(--ink-soft)', margin: 0 }}>
            {feedback}
          </p>
          {subject_specific_notes && (
            <div style={{
              marginTop: 14, padding: '12px 16px',
              background: 'rgba(99,102,241,0.08)',
              borderRadius: 'var(--radius-md)',
              borderLeft: '3px solid #6366f1',
            }}>
              <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 600, color: '#6366f1', margin: 0, lineHeight: 1.6 }}>
                💡 {subject_specific_notes}
              </p>
            </div>
          )}
        </div>
      </m.div>

      {/* Concept Analysis */}
      {(concept_analysis.correct_concepts?.length > 0 ||
        concept_analysis.missing_concepts?.length > 0 ||
        concept_analysis.wrong_concepts?.length > 0) && (
        <m.div variants={shouldReduce ? undefined : cardVariants}>
          <SectionCard title="Concept Analysis" icon={FiTarget} gradient="linear-gradient(135deg,#10b981,#06b6d4)">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px,1fr))', gap: 16 }}>
              {concept_analysis.correct_concepts?.length > 0 && (
                <div>
                  <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 700, color: '#10b981', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <FiCheckCircle size={11} strokeWidth={2} /> Correct ({concept_analysis.correct_concepts.length})
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                    {concept_analysis.correct_concepts.slice(0, 6).map((c, i) => <ConceptChip key={i} text={c} type="correct" />)}
                  </div>
                </div>
              )}
              {concept_analysis.missing_concepts?.length > 0 && (
                <div>
                  <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 700, color: '#f59e0b', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <FiAlertTriangle size={11} strokeWidth={2} /> Missing ({concept_analysis.missing_concepts.length})
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                    {concept_analysis.missing_concepts.slice(0, 6).map((c, i) => <ConceptChip key={i} text={c} type="missing" />)}
                  </div>
                </div>
              )}
              {concept_analysis.wrong_concepts?.length > 0 && (
                <div>
                  <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 700, color: '#f43f5e', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: 5 }}>
                    <FiXCircle size={11} strokeWidth={2} /> Wrong ({concept_analysis.wrong_concepts.length})
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                    {concept_analysis.wrong_concepts.slice(0, 4).map((c, i) => <ConceptChip key={i} text={c} type="wrong" />)}
                  </div>
                </div>
              )}
            </div>
            {concept_analysis.coverage_percentage !== undefined && (
              <div style={{ marginTop: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
                  <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 12, fontWeight: 600, color: 'var(--ink-soft)' }}>Concept Coverage</span>
                  <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 12, fontWeight: 800, background: 'linear-gradient(135deg,#10b981,#06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    {concept_analysis.coverage_percentage.toFixed(0)}%
                  </span>
                </div>
                <div style={{ height: 8, background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                  <m.div
                    initial={{ width: 0 }} animate={{ width: `${concept_analysis.coverage_percentage}%` }}
                    transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
                    style={{
                      height: '100%', borderRadius: 'var(--radius-full)',
                      background: concept_analysis.coverage_percentage >= 70 ? 'linear-gradient(90deg,#10b981,#06b6d4)' : concept_analysis.coverage_percentage >= 40 ? 'linear-gradient(90deg,#6366f1,#8b5cf6)' : 'linear-gradient(90deg,#f43f5e,#ec4899)',
                      boxShadow: '0 0 12px rgba(16,185,129,0.4)',
                    }}
                  />
                </div>
              </div>
            )}
          </SectionCard>
        </m.div>
      )}

      {/* Suggestions */}
      {improvement_suggestions.length > 0 && (
        <m.div variants={shouldReduce ? undefined : cardVariants}>
          <SectionCard title="How to Improve" icon={FiTrendingUp} gradient="linear-gradient(135deg,#6366f1,#8b5cf6)">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {improvement_suggestions.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: '50%', flexShrink: 0, marginTop: 1,
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    color: '#ffffff', fontSize: 11, fontWeight: 800,
                    fontFamily: '"Plus Jakarta Sans", sans-serif',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 2px 8px rgba(99,102,241,0.3)',
                    letterSpacing: '-0.02em',
                  }}>
                    {i + 1}
                  </span>
                  <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, lineHeight: 1.65, color: 'var(--ink-soft)' }}>
                    {s}
                  </span>
                </div>
              ))}
            </div>
          </SectionCard>
        </m.div>
      )}

      {/* Metrics */}
      <m.div variants={shouldReduce ? undefined : cardVariants} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        {[
          { label: 'Semantic Similarity', value: `${Math.round((semantic_similarity || 0) * 100)}%`, grad: 'linear-gradient(135deg,#6366f1,#8b5cf6)' },
          { label: 'AI Confidence',       value: `${Math.round((confidence_score    || 0) * 100)}%`, grad: 'linear-gradient(135deg,#10b981,#06b6d4)' },
        ].map(item => (
          <div key={item.label} style={{
            background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border)', padding: '16px',
            boxShadow: 'var(--shadow-card)', textAlign: 'center',
            position: 'relative', overflow: 'hidden',
          }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: item.grad }} />
            <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 600, color: 'var(--ink-muted)', letterSpacing: '0.06em', textTransform: 'uppercase', margin: '0 0 6px' }}>
              {item.label}
            </p>
            <p style={{
              fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 24, fontWeight: 800,
              background: item.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              margin: 0, lineHeight: 1, letterSpacing: '-0.03em',
            }}>
              {item.value}
            </p>
          </div>
        ))}
      </m.div>
    </m.div>
  )
}
