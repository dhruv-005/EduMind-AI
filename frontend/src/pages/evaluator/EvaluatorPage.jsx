/* ============================================================
   EDUMIND AI — EVALUATOR PAGE (Challenge 1)
   ============================================================ */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useEvaluatorStore } from '@store/evaluatorStore'
import { useEvaluation } from '@hooks/useEvaluation'
import { SUBJECTS, GRADE_THRESHOLDS } from '@utils/constants'
import { validateEvaluatorForm } from '@utils/validators'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ScoreGauge from '@components/ui/ScoreGauge'
import ProgressBar from '@components/ui/ProgressBar'
import Tabs from '@components/ui/Tabs'
import toast from 'react-hot-toast'

/* ── PARSE HELPER ───────────────────────────────────────────── */
function parseList(val) {
  if (Array.isArray(val)) return val
  if (typeof val === 'string') {
    try { return JSON.parse(val) } catch { return [] }
  }
  return []
}

/* ── SUBJECT SELECTOR ───────────────────────────────────────── */
function SubjectSelector({ value, onChange }) {
  const META = {
    mathematics:    { icon: '∑', color: 'var(--accent-primary)' },
    science:        { icon: '⚗', color: 'var(--accent-cyber)'   },
    english:        { icon: 'A', color: 'var(--term-green)'      },
    general:        { icon: '◎', color: 'var(--term-amber)'      },
    physics:        { icon: 'φ', color: 'var(--accent-cyber)'    },
    chemistry:      { icon: '⚗', color: 'var(--term-amber)'      },
    biology:        { icon: '🧬', color: 'var(--term-green)'     },
    history:        { icon: '📜', color: 'var(--accent-primary)' },
    geography:      { icon: '🌍', color: 'var(--accent-cyber)'   },
    computer_science:{ icon: '</>', color: 'var(--term-green)'   },
  }

  return (
    <div>
      <div style={{
        fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
        textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
        color: 'var(--muted)', marginBottom: 'var(--space-3)',
      }}>
        SUBJECT *
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
        {SUBJECTS.map((s) => {
          const meta = META[s.value] || { icon: '◇', color: 'var(--muted)' }
          const isActive = value === s.value
          return (
            <button key={s.value} onClick={() => onChange(s.value)} style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
              padding: 'var(--space-2) var(--space-4)',
              border: isActive ? `2px solid ${meta.color}` : 'var(--border-thin)',
              background: isActive ? `color-mix(in srgb, ${meta.color} 12%, transparent)` : 'var(--surface)',
              color: isActive ? meta.color : 'var(--muted)',
              cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
              transition: 'all 0.12s ease',
              boxShadow: isActive ? `3px 3px 0px ${meta.color}` : 'none',
            }}>
              <span>{meta.icon}</span>{s.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}

/* ── CONCEPT BADGE ──────────────────────────────────────────── */
function ConceptBadge({ text, type }) {
  const styles = {
    correct: { color: 'var(--term-green)', bg: 'var(--term-green-dim)', border: 'var(--term-green)', icon: '✓' },
    missing: { color: 'var(--term-amber)', bg: 'var(--term-amber-dim)', border: 'var(--term-amber)', icon: '○' },
    wrong:   { color: 'var(--term-red)',   bg: 'var(--term-red-dim)',   border: 'var(--term-red)',   icon: '✕' },
  }
  const s = styles[type] || styles.correct
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 'var(--space-1)',
      fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
      textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
      padding: '0.2rem 0.5rem',
      border: `1px solid ${s.border}`, background: s.bg, color: s.color,
      margin: '0.2rem',
    }}>
      <span>{s.icon}</span>{text}
    </span>
  )
}

/* ── RESULT PANEL ───────────────────────────────────────────── */
function ResultPanel({ result, onReset }) {
  // Normalize all fields from backend response
  const score       = result.score_out_of_10 ?? result.score ?? 0
  const maxScore    = result.max_score ?? 10
  const grade       = result.grade ?? 'N/A'
  const percentage  = result.percentage ?? result.total_score ?? 0
  const feedback    = result.feedback ?? ''
  const modelUsed   = result.model_used ?? result.provider ?? 'AI'
  const confidence  = result.confidence_score ?? result.confidence ?? 0
  const govStatus   = result.governance_status ?? 'passed'
  const processingMs = result.processing_time_ms ?? 0

  // Parse concepts — handle both direct arrays and nested in concept_analysis
  const ca             = result.concept_analysis || {}
  const correctConcepts = parseList(result.correct_concepts ?? ca.correct_concepts ?? [])
  const missingConcepts = parseList(result.missing_concepts ?? ca.missing_concepts ?? [])
  const wrongConcepts   = parseList(result.wrong_concepts   ?? ca.wrong_concepts   ?? [])
  const suggestions     = parseList(result.improvement_suggestions ?? [])

  // Parse score breakdown
  const bd = result.score_breakdown || result.breakdown || {}
  const breakdown = {
    correctness:  bd.correctness  ?? 0,
    relevance:    bd.relevance    ?? 0,
    completeness: bd.completeness ?? 0,
    clarity:      bd.clarity      ?? 0,
  }

  const tabsData = [
    {
      id: 'overview', label: 'OVERVIEW',
      content: (
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 2fr',
          gap: 'var(--space-8)', alignItems: 'start',
        }}>
          {/* Score gauge */}
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            padding: 'var(--space-6)', background: 'var(--surface)',
            border: 'var(--border)', boxShadow: 'var(--shadow)',
          }}>
            <ScoreGauge score={score} maxScore={maxScore} size={160} animated />
            <div style={{
              marginTop: 'var(--space-4)', textAlign: 'center',
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              color: 'var(--muted)', textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
            }}>
              {percentage.toFixed(1)}% — {grade}
            </div>
          </div>

          {/* Breakdown */}
          <div>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-widest)',
              color: 'var(--muted)', marginBottom: 'var(--space-5)',
            }}>
              SCORE BREAKDOWN
            </div>

            {[
              { key: 'correctness',  label: 'CORRECTNESS',  max: 40, color: 'var(--term-green)'    },
              { key: 'relevance',    label: 'RELEVANCE',    max: 20, color: 'var(--accent-cyber)'   },
              { key: 'completeness', label: 'COMPLETENESS', max: 25, color: 'var(--term-amber)'     },
              { key: 'clarity',      label: 'CLARITY',      max: 15, color: 'var(--accent-primary)' },
            ].map((dim) => (
              <div key={dim.key} style={{ marginBottom: 'var(--space-4)' }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  marginBottom: 'var(--space-2)',
                }}>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                    textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
                    color: 'var(--muted)',
                  }}>
                    {dim.label}
                  </span>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
                    fontWeight: 700, color: dim.color,
                  }}>
                    {breakdown[dim.key].toFixed(1)} / {dim.max}
                  </span>
                </div>
                <ProgressBar
                  value={(breakdown[dim.key] / dim.max) * 100}
                  max={100} color={dim.color} showValue={false} height="5px"
                />
              </div>
            ))}

            {/* Governance */}
            <div style={{
              marginTop: 'var(--space-6)', padding: 'var(--space-3)',
              background: 'var(--term-green-dim)', border: '1px solid var(--term-green)',
              display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
            }}>
              <span style={{
                width: '6px', height: '6px', borderRadius: '50%',
                background: 'var(--term-green)', flexShrink: 0,
              }} />
              <span style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
                color: 'var(--term-green)',
              }}>
                GOVERNANCE: {govStatus.toUpperCase()} — MODEL: {modelUsed} — {(processingMs/1000).toFixed(1)}s
              </span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'concepts', label: 'CONCEPTS',
      content: (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {correctConcepts.length > 0 && (
            <div>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
                color: 'var(--term-green)', marginBottom: 'var(--space-3)',
              }}>
                ✓ CORRECT CONCEPTS ({correctConcepts.length})
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                {correctConcepts.map((c, i) => <ConceptBadge key={i} text={c} type="correct" />)}
              </div>
            </div>
          )}

          {missingConcepts.length > 0 && (
            <div>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
                color: 'var(--term-amber)', marginBottom: 'var(--space-3)',
              }}>
                ○ MISSING CONCEPTS ({missingConcepts.length})
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                {missingConcepts.map((c, i) => <ConceptBadge key={i} text={c} type="missing" />)}
              </div>
            </div>
          )}

          {wrongConcepts.length > 0 && (
            <div>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
                color: 'var(--term-red)', marginBottom: 'var(--space-3)',
              }}>
                ✕ INCORRECT CONCEPTS ({wrongConcepts.length})
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                {wrongConcepts.map((c, i) => <ConceptBadge key={i} text={c} type="wrong" />)}
              </div>
            </div>
          )}

          {correctConcepts.length === 0 && missingConcepts.length === 0 && wrongConcepts.length === 0 && (
            <div style={{
              padding: 'var(--space-8)', textAlign: 'center',
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
              color: 'var(--muted)', textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
            }}>
              CONCEPT ANALYSIS NOT AVAILABLE
            </div>
          )}
        </div>
      ),
    },
    {
      id: 'feedback', label: 'FEEDBACK',
      content: (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {/* Main feedback */}
          <div style={{
            padding: 'var(--space-6)', background: 'var(--surface)',
            border: 'var(--border)', borderLeft: '4px solid var(--accent-primary)',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
              color: 'var(--accent-primary)', marginBottom: 'var(--space-4)',
            }}>
              AI EVALUATION FEEDBACK
            </div>
            <p style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
              color: 'var(--ink)', lineHeight: 1.7,
            }}>
              {feedback || 'No detailed feedback available.'}
            </p>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
                color: 'var(--muted)', marginBottom: 'var(--space-4)',
              }}>
                IMPROVEMENT SUGGESTIONS
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {suggestions.map((sug, i) => (
                  <div key={i} style={{
                    display: 'flex', gap: 'var(--space-3)',
                    padding: 'var(--space-4)', background: 'var(--surface)',
                    border: 'var(--border-thin)', borderLeft: '3px solid var(--accent-cyber)',
                  }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                      color: 'var(--accent-cyber)', fontWeight: 700, flexShrink: 0,
                    }}>
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <p style={{
                      fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
                      color: 'var(--muted)', lineHeight: 1.6,
                    }}>
                      {sug}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Confidence */}
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: 'var(--space-4)', background: 'var(--surface)', border: 'var(--border-thin)',
          }}>
            <span style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--muted)',
            }}>
              AI CONFIDENCE SCORE
            </span>
            <span style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', fontWeight: 700,
              color: confidence >= 0.6 ? 'var(--term-green)' : 'var(--term-amber)',
            }}>
              {(confidence * 100).toFixed(1)}%
              {confidence < 0.6 && (
                <span style={{ marginLeft: 'var(--space-2)', fontSize: 'var(--fs-nano)', color: 'var(--term-amber)' }}>
                  ⚠ FLAGGED FOR REVIEW
                </span>
              )}
            </span>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div style={{ background: 'var(--base)', border: 'var(--border)', boxShadow: 'var(--shadow)' }}>
      {/* Header */}
      <div style={{
        padding: 'var(--space-5) var(--space-6)', borderBottom: 'var(--border)',
        background: 'var(--surface)', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          <div style={{
            fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h3)',
            fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)',
          }}>
            EVALUATION COMPLETE
          </div>
          <Badge variant="green" dot>PROCESSED</Badge>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <Button variant="surface" size="sm" onClick={onReset}>← NEW EVALUATION</Button>
          <Link to="/evaluator/history">
            <Button variant="cyber" size="sm">VIEW HISTORY</Button>
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ padding: 'var(--space-6)' }}>
        <Tabs tabs={tabsData} defaultTab="overview" />
      </div>
    </div>
  )
}

/* ── MAIN PAGE ──────────────────────────────────────────────── */
export default function EvaluatorPage() {
  const {
    question, referenceAnswer, studentAnswer, subject, maxScore,
    result, isLoading, error,
    setQuestion, setReferenceAnswer, setStudentAnswer, setSubject, setMaxScore,
  } = useEvaluatorStore()

  const { evaluate, reset } = useEvaluation()
  const [formErrors, setFormErrors] = useState({})

  const handleSubmit = async (e) => {
    e.preventDefault()
    const { isValid, errors } = validateEvaluatorForm({
      question, reference_answer: referenceAnswer,
      student_answer: studentAnswer, subject, max_score: maxScore,
    })
    if (!isValid) { setFormErrors(errors); return }
    setFormErrors({})
    await evaluate()
  }

  const handleReset = () => { reset(); setFormErrors({}) }

  if (result) {
    const resultData = result?.data || result
    return (
      <div style={{ padding: 'var(--space-8)' }}>
        <ResultPanel result={resultData} onReset={handleReset} />
      </div>
    )
  }

  const taStyle = (err) => ({
    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
    color: 'var(--ink)', background: 'var(--base)',
    border: `1px solid ${err ? 'var(--term-red)' : 'var(--ink)'}`,
    outline: 'none', padding: '0.75rem 1rem', width: '100%',
    resize: 'vertical', lineHeight: 1.6,
    boxShadow: err ? '3px 3px 0 var(--term-red)' : 'none',
    transition: 'border-color 0.12s, box-shadow 0.12s',
  })

  const labelStyle = (err) => ({
    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
    textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
    color: err ? 'var(--term-red)' : 'var(--muted)',
    display: 'block', marginBottom: 'var(--space-2)',
  })

  return (
    <div style={{ padding: 'var(--space-8)' }}>
      {/* Header */}
      <div style={{
        marginBottom: 'var(--space-8)', paddingBottom: 'var(--space-6)',
        borderBottom: 'var(--border)',
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          textTransform: 'uppercase', letterSpacing: 'var(--ls-widest)',
          color: 'var(--accent-primary)', marginBottom: 'var(--space-3)',
        }}>
          // CH-01 — AI EVALUATION ENGINE
        </div>
        <h1 style={{
          fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h1)',
          fontWeight: 700, textTransform: 'uppercase',
          letterSpacing: 'var(--ls-tight)', lineHeight: 0.92,
        }}>
          ANSWER<br />
          <span style={{ color: 'var(--accent-primary)' }}>EVALUATOR</span>
        </h1>
      </div>

      {/* Form grid */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 320px',
        gap: 'var(--space-6)', alignItems: 'start',
      }}>
        {/* Left form */}
        <form onSubmit={handleSubmit}>
          <div style={{
            background: 'var(--base)', border: 'var(--border)', boxShadow: 'var(--shadow)',
          }}>
            <div style={{
              padding: 'var(--space-5) var(--space-6)', borderBottom: 'var(--border)',
              background: 'var(--surface)',
            }}>
              <span style={{
                fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)',
                fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)',
              }}>
                EVALUATION INPUT
              </span>
            </div>

            <div style={{
              padding: 'var(--space-6)', display: 'flex',
              flexDirection: 'column', gap: 'var(--space-6)',
            }}>
              <SubjectSelector value={subject} onChange={setSubject} />

              {/* Question */}
              <div>
                <label style={labelStyle(formErrors.question)}>QUESTION *</label>
                <textarea
                  value={question}
                  onChange={(e) => { setQuestion(e.target.value); setFormErrors(p => ({...p, question: ''})) }}
                  placeholder="Enter the exam question here..."
                  rows={3}
                  style={taStyle(formErrors.question)}
                />
                {formErrors.question && (
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--term-red)', textTransform: 'uppercase' }}>
                    ✕ {formErrors.question}
                  </span>
                )}
              </div>

              {/* Reference Answer */}
              <div>
                <label style={labelStyle(formErrors.reference_answer)}>REFERENCE / MODEL ANSWER *</label>
                <textarea
                  value={referenceAnswer}
                  onChange={(e) => { setReferenceAnswer(e.target.value); setFormErrors(p => ({...p, reference_answer: ''})) }}
                  placeholder="Enter the correct/model answer..."
                  rows={5}
                  style={{ ...taStyle(false), background: 'var(--surface)' }}
                />
              </div>

              {/* Student Answer */}
              <div>
                <label style={labelStyle(formErrors.student_answer)}>STUDENT ANSWER *</label>
                <textarea
                  value={studentAnswer}
                  onChange={(e) => { setStudentAnswer(e.target.value); setFormErrors(p => ({...p, student_answer: ''})) }}
                  placeholder="Enter the student's answer to evaluate..."
                  rows={5}
                  style={taStyle(formErrors.student_answer)}
                />
                {formErrors.student_answer && (
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--term-red)', textTransform: 'uppercase' }}>
                    ✕ {formErrors.student_answer}
                  </span>
                )}
              </div>

              {/* Submit */}
              <div style={{
                display: 'flex', gap: 'var(--space-4)',
                paddingTop: 'var(--space-4)', borderTop: 'var(--border-thin)', flexWrap: 'wrap',
              }}>
                <Button type="submit" variant="primary" size="lg" loading={isLoading} disabled={isLoading}>
                  {isLoading ? 'EVALUATING... (30-60s)' : '▶ RUN EVALUATION'}
                </Button>
                <Button type="button" variant="ghost" size="lg" onClick={handleReset} disabled={isLoading}>
                  CLEAR
                </Button>
              </div>

              {isLoading && (
                <div style={{
                  padding: 'var(--space-4)', background: 'var(--surface)',
                  border: '1px solid var(--accent-cyber)', borderLeft: '4px solid var(--accent-cyber)',
                  fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                  color: 'var(--accent-cyber)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
                }}>
                  ● AI IS ANALYZING... EMBEDDING + LLM SCORING IN PROGRESS. PLEASE WAIT 30-60 SECONDS.
                </div>
              )}

              {error && (
                <div style={{
                  padding: 'var(--space-4)', background: 'var(--term-red-dim)',
                  border: '1px solid var(--term-red)', borderLeft: '4px solid var(--term-red)',
                  fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--term-red)',
                }}>
                  ✕ {error}
                </div>
              )}
            </div>
          </div>
        </form>

        {/* Right sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Max score */}
          <div style={{
            background: 'var(--base)', border: 'var(--border)',
            boxShadow: 'var(--shadow)', padding: 'var(--space-5)',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
              color: 'var(--muted)', marginBottom: 'var(--space-4)',
              borderBottom: 'var(--border-thin)', paddingBottom: 'var(--space-3)',
            }}>
              CONFIGURATION
            </div>
            <label style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
              color: 'var(--muted)', display: 'block', marginBottom: 'var(--space-2)',
            }}>
              MAX SCORE
            </label>
            <input
              type="number" min={1} max={100} value={maxScore}
              onChange={(e) => setMaxScore(Number(e.target.value))}
              style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
                color: 'var(--ink)', background: 'var(--base)',
                border: 'var(--border-thin)', outline: 'none',
                padding: '0.6rem 0.9rem', width: '100%',
              }}
            />
          </div>

          {/* Pipeline info */}
          <div style={{
            background: 'var(--term-bg)', border: '1px solid var(--term-border)',
            padding: 'var(--space-5)',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
              color: 'var(--term-green)', marginBottom: 'var(--space-4)',
              borderBottom: '1px solid var(--term-border)', paddingBottom: 'var(--space-3)',
            }}>
              HOW IT WORKS
            </div>
            {[
              { step: '01', label: 'Semantic Similarity',  detail: 'sentence-transformers', color: 'var(--accent-cyber)'   },
              { step: '02', label: 'LLM Deep Analysis',    detail: 'Groq openai/gpt-oss-20b', color: 'var(--accent-primary)' },
              { step: '03', label: 'Subject Rubric Check', detail: 'Math/Science/English',  color: 'var(--term-green)'     },
              { step: '04', label: 'Score Aggregation',    detail: '4-dimension weighted',   color: 'var(--term-amber)'     },
              { step: '05', label: 'Governance Audit',     detail: 'Log + bias check',        color: 'var(--term-red)'       },
            ].map((item) => (
              <div key={item.step} style={{
                display: 'flex', gap: 'var(--space-3)',
                marginBottom: 'var(--space-3)', alignItems: 'flex-start',
              }}>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                  color: item.color, fontWeight: 700, flexShrink: 0, minWidth: '20px',
                }}>{item.step}</span>
                <div>
                  <div style={{
                    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                    textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
                    color: 'rgba(255,255,255,0.7)', marginBottom: '2px',
                  }}>{item.label}</div>
                  <div style={{
                    fontFamily: 'var(--font-mono)', fontSize: '0.6rem',
                    color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                  }}>{item.detail}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Grade scale */}
          <div style={{
            background: 'var(--base)', border: 'var(--border)',
            boxShadow: 'var(--shadow)', padding: 'var(--space-5)',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
              color: 'var(--muted)', marginBottom: 'var(--space-4)',
              borderBottom: 'var(--border-thin)', paddingBottom: 'var(--space-3)',
            }}>
              GRADE SCALE
            </div>
            {GRADE_THRESHOLDS.map((g) => (
              <div key={g.grade} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: 'var(--space-2) 0', borderBottom: '1px solid var(--border-subtle)',
              }}>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                  textTransform: 'uppercase', color: 'var(--muted)',
                }}>
                  {g.min}–{g.max} / 10
                </span>
                <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                    color: g.min >= 8 ? 'var(--term-green)' : g.min >= 5 ? 'var(--term-amber)' : 'var(--term-red)',
                    fontWeight: 700,
                  }}>{g.grade}</span>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                    color: 'var(--muted)', textTransform: 'uppercase',
                  }}>{g.label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Responsive */}
      <style>{`
        @media (max-width: 900px) {
          div[style*="grid-template-columns: 1fr 320px"] { grid-template-columns: 1fr !important; }
          div[style*="grid-template-columns: 1fr 2fr"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
