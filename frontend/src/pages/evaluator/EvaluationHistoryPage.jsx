/* ============================================================
   EDUMIND AI — EVALUATION HISTORY PAGE
   ============================================================ */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useEvaluatorStore } from '@store/evaluatorStore'
import { formatRelative, formatScore } from '@utils/formatters'
import { getGrade } from '@utils/formatters'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ScoreGauge from '@components/ui/ScoreGauge'
import Modal from '@components/ui/Modal'

export default function EvaluationHistoryPage() {
  const { history, clearHistory } = useEvaluatorStore()
  const [selected, setSelected] = useState(null)

  const getScoreVariant = (score) => {
    if (score >= 8) return 'green'
    if (score >= 5) return 'amber'
    return 'red'
  }

  return (
    <div style={{ padding: 'var(--space-8)' }}>

      {/* Header */}
      <div style={{
        display:        'flex',
        alignItems:     'flex-start',
        justifyContent: 'space-between',
        marginBottom:   'var(--space-8)',
        paddingBottom:  'var(--space-6)',
        borderBottom:   'var(--border)',
        flexWrap:       'wrap',
        gap:            'var(--space-4)',
      }}>
        <div>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color:         'var(--accent-primary)',
            marginBottom:  'var(--space-3)',
          }}>
            // CH-01 — EVALUATION LOG
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            HISTORY
          </h1>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <Link to="/evaluator">
            <Button variant="primary" size="sm">
              + NEW EVALUATION
            </Button>
          </Link>
          {history.length > 0 && (
            <Button
              variant="danger"
              size="sm"
              onClick={clearHistory}
            >
              CLEAR ALL
            </Button>
          )}
        </div>
      </div>

      {/* Empty state */}
      {history.length === 0 && (
        <div style={{
          padding:        'var(--space-20)',
          textAlign:      'center',
          border:         'var(--border-dashed)',
          background:     'var(--surface)',
        }}>
          <div style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h2)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            color:         'var(--muted)',
            marginBottom:  'var(--space-4)',
          }}>
            NO EVALUATIONS YET
          </div>
          <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-data)',
            color:      'var(--muted)',
            marginBottom:'var(--space-6)',
          }}>
            Run your first evaluation to see it here
          </p>
          <Link to="/evaluator">
            <Button variant="primary">
              ▶ START EVALUATING
            </Button>
          </Link>
        </div>
      )}

      {/* History table */}
      {history.length > 0 && (
        <div style={{
          border:     'var(--border)',
          boxShadow:  'var(--shadow)',
          background: 'var(--base)',
        }}>
          <table className="data-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th>#</th>
                <th>SUBJECT</th>
                <th>QUESTION</th>
                <th>SCORE</th>
                <th>GRADE</th>
                <th>TIME</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item, i) => {
                const grade = getGrade(item.score, item.max_score || 10)
                return (
                  <tr key={item.id || i}>
                    <td style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   'var(--fs-nano)',
                      color:      'var(--muted)',
                    }}>
                      {String(i + 1).padStart(2, '0')}
                    </td>
                    <td>
                      <Badge variant="default">
                        {item.subject || 'GENERAL'}
                      </Badge>
                    </td>
                    <td style={{
                      fontFamily:  'var(--font-mono)',
                      fontSize:    'var(--fs-data)',
                      color:       'var(--ink)',
                      maxWidth:    '300px',
                      overflow:    'hidden',
                      textOverflow:'ellipsis',
                      whiteSpace:  'nowrap',
                    }}>
                      {item.question || '—'}
                    </td>
                    <td>
                      <Badge variant={getScoreVariant(item.score)}>
                        {item.score} / {item.max_score || 10}
                      </Badge>
                    </td>
                    <td style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   'var(--fs-data)',
                      fontWeight: 700,
                      color:      item.score >= 8
                        ? 'var(--term-green)'
                        : item.score >= 5
                          ? 'var(--term-amber)'
                          : 'var(--term-red)',
                    }}>
                      {grade?.grade}
                    </td>
                    <td style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   'var(--fs-nano)',
                      color:      'var(--muted)',
                    }}>
                      {item.timestamp
                        ? formatRelative(item.timestamp)
                        : '—'}
                    </td>
                    <td>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelected(item)}
                      >
                        VIEW →
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail Modal */}
      <Modal
        isOpen={!!selected}
        onClose={() => setSelected(null)}
        title="EVALUATION DETAIL"
        size="lg"
      >
        {selected && (
          <div style={{
            display:       'flex',
            flexDirection: 'column',
            gap:           'var(--space-6)',
          }}>
            {/* Score */}
            <div style={{
              display:    'flex',
              gap:        'var(--space-8)',
              alignItems: 'center',
            }}>
              <ScoreGauge
                score={selected.score}
                maxScore={selected.max_score || 10}
                size={140}
                animated
              />
              <div>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  color:         'var(--muted)',
                  marginBottom:  'var(--space-2)',
                }}>
                  SUBJECT
                </div>
                <Badge variant="default">
                  {selected.subject || 'GENERAL'}
                </Badge>
              </div>
            </div>

            {/* Question */}
            <div>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color:         'var(--muted)',
                marginBottom:  'var(--space-2)',
              }}>
                QUESTION
              </div>
              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   'var(--fs-data)',
                color:      'var(--ink)',
                lineHeight: 1.6,
                padding:    'var(--space-4)',
                background: 'var(--surface)',
                border:     'var(--border-thin)',
              }}>
                {selected.question}
              </p>
            </div>

            {/* Feedback */}
            {selected.feedback && (
              <div>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  color:         'var(--muted)',
                  marginBottom:  'var(--space-2)',
                }}>
                  FEEDBACK
                </div>
                <p style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize:   'var(--fs-data)',
                  color:      'var(--ink)',
                  lineHeight: 1.7,
                  padding:    'var(--space-4)',
                  background: 'var(--surface)',
                  border:     'var(--border-thin)',
                  borderLeft: '4px solid var(--accent-primary)',
                }}>
                  {selected.feedback}
                </p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
