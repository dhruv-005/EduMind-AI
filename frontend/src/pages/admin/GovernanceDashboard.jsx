/* ============================================================
   EDUMIND AI — GOVERNANCE DASHBOARD PAGE
   Full 7-pillar governance monitoring system
   ============================================================ */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'
import Tabs from '@components/ui/Tabs'
import Modal from '@components/ui/Modal'

/* ── FLAGGED ITEM CARD ──────────────────────────────────────── */
function FlaggedItemCard({ item, onApprove, onReject }) {
  const typeColors = {
    evaluation:  'var(--accent-primary)',
    generation:  'var(--accent-cyber)',
    voice:       'var(--term-green)',
    sales:       'var(--accent-purple)',
  }

  const color = typeColors[item.type] || 'var(--muted)'

  return (
    <div style={{
      background:  'var(--base)',
      border:      'var(--border)',
      boxShadow:   'var(--shadow-sm)',
      borderLeft:  `4px solid ${color}`,
    }}>
      {/* Header */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        'var(--space-4) var(--space-5)',
        borderBottom:   'var(--border-thin)',
        background:     'var(--surface)',
      }}>
        <div style={{
          display:    'flex',
          alignItems: 'center',
          gap:        'var(--space-3)',
        }}>
          <span style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            color,
            fontWeight:    700,
            textTransform: 'uppercase',
          }}>
            #{item.id}
          </span>
          <Badge style={{ color, borderColor: color, background: 'transparent' }}>
            {item.type.toUpperCase()}
          </Badge>
          <Badge variant="amber">
            CONFIDENCE: {(item.confidence * 100).toFixed(0)}%
          </Badge>
        </div>

        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
        }}>
          {item.time}
        </span>
      </div>

      {/* Body */}
      <div style={{ padding: 'var(--space-5)' }}>
        <div style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wider)',
          color:         'var(--muted)',
          marginBottom:  'var(--space-2)',
        }}>
          REASON FLAGGED
        </div>
        <p style={{
          fontFamily:   'var(--font-mono)',
          fontSize:     'var(--fs-data)',
          color:        'var(--ink)',
          lineHeight:   1.6,
          marginBottom: 'var(--space-4)',
        }}>
          {item.reason}
        </p>

        {/* Confidence bar */}
        <ProgressBar
          value={item.confidence * 100}
          max={100}
          label="AI CONFIDENCE"
          color={item.confidence < 0.6
            ? 'var(--term-red)'
            : 'var(--term-amber)'}
          height="4px"
        />

        {/* Actions */}
        <div style={{
          display:      'flex',
          gap:          'var(--space-3)',
          marginTop:    'var(--space-5)',
          paddingTop:   'var(--space-4)',
          borderTop:    'var(--border-thin)',
        }}>
          <Button
            variant="green"
            size="sm"
            onClick={() => onApprove(item.id)}
          >
            ✓ APPROVE
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => onReject(item.id)}
          >
            ✕ REJECT
          </Button>
          <Button variant="ghost" size="sm">
            VIEW DETAIL
          </Button>
        </div>
      </div>
    </div>
  )
}

/* ── BIAS REPORT CHART ──────────────────────────────────────── */
function BiasReportChart({ data }) {
  return (
    <div style={{
      display:       'flex',
      flexDirection: 'column',
      gap:           'var(--space-4)',
    }}>
      {data.map((item) => (
        <div key={item.dimension}>
          <div style={{
            display:        'flex',
            justifyContent: 'space-between',
            marginBottom:   'var(--space-2)',
          }}>
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wide)',
              color:         'var(--ink)',
            }}>
              {item.dimension}
            </span>
            <div style={{
              display:    'flex',
              alignItems: 'center',
              gap:        'var(--space-2)',
            }}>
              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                fontWeight:    700,
                color:         item.score < 0.2
                  ? 'var(--term-green)'
                  : item.score < 0.5
                    ? 'var(--term-amber)'
                    : 'var(--term-red)',
              }}>
                {(item.score * 100).toFixed(1)}%
              </span>
              <Badge
                variant={item.score < 0.2 ? 'green' : item.score < 0.5 ? 'amber' : 'red'}
              >
                {item.status}
              </Badge>
            </div>
          </div>
          <ProgressBar
            value={item.score * 100}
            max={100}
            color={item.score < 0.2
              ? 'var(--term-green)'
              : item.score < 0.5
                ? 'var(--term-amber)'
                : 'var(--term-red)'}
            showValue={false}
            height="6px"
          />
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            color:         'var(--muted)',
            marginTop:     'var(--space-1)',
          }}>
            {item.detail}
          </div>
        </div>
      ))}
    </div>
  )
}

/* ── RATE LIMIT MONITOR ─────────────────────────────────────── */
function RateLimitMonitor({ data }) {
  return (
    <div style={{
      border:     'var(--border)',
      background: 'var(--base)',
    }}>
      <div style={{
        display:             'grid',
        gridTemplateColumns: '1fr 80px 80px 100px 80px',
        gap:                 'var(--space-4)',
        padding:             'var(--space-3) var(--space-5)',
        borderBottom:        'var(--border)',
        background:          'var(--surface)',
      }}>
        {['IP ADDRESS', 'REQUESTS', 'LIMIT', 'STATUS', 'ACTION'].map((h) => (
          <span key={h} style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wider)',
            color:         'var(--muted)',
          }}>
            {h}
          </span>
        ))}
      </div>

      {data.map((row, i) => (
        <div
          key={i}
          style={{
            display:             'grid',
            gridTemplateColumns: '1fr 80px 80px 100px 80px',
            gap:                 'var(--space-4)',
            padding:             'var(--space-3) var(--space-5)',
            borderBottom:        i < data.length - 1
              ? 'var(--border-thin)'
              : 'none',
            alignItems:          'center',
          }}
        >
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-data)',
            color:      'var(--ink)',
          }}>
            {row.ip}
          </span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-data)',
            fontWeight: 700,
            color:      row.requests > 90
              ? 'var(--term-red)'
              : row.requests > 70
                ? 'var(--term-amber)'
                : 'var(--term-green)',
            textAlign:  'right',
          }}>
            {row.requests}
          </span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-nano)',
            color:      'var(--muted)',
            textAlign:  'right',
          }}>
            {row.limit}
          </span>
          <Badge
            variant={
              row.status === 'BLOCKED'  ? 'red'
              : row.status === 'WARNING' ? 'amber'
              : 'green'
            }
          >
            {row.status}
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {}}
          >
            {row.status === 'BLOCKED' ? 'UNBLOCK' : 'BLOCK'}
          </Button>
        </div>
      ))}
    </div>
  )
}

/* ── MAIN GOVERNANCE DASHBOARD ──────────────────────────────── */
export default function GovernanceDashboard() {

  const [flaggedItems, setFlaggedItems] = useState([
    {
      id:         8828,
      type:       'evaluation',
      confidence: 0.58,
      reason:     'AI confidence below 60% threshold. Student answer contains ambiguous mathematical notation. Requires teacher verification before score is finalized.',
      time:       '14:25:11',
    },
    {
      id:         8819,
      type:       'generation',
      confidence: 0.55,
      reason:     'Generated question similarity score 91% — above 85% deduplication threshold. Requires human approval before adding to paper.',
      time:       '13:41:03',
    },
    {
      id:         8801,
      type:       'voice',
      confidence: 0.52,
      reason:     'Student distress signal detected in voice session. Possible emotional distress. Flagged for counselor review.',
      time:       '12:18:44',
    },
  ])

  const [showApproveModal, setShowApproveModal] = useState(false)
  const [pendingAction, setPendingAction]       = useState(null)

  const handleApprove = (id) => {
    setPendingAction({ id, action: 'approve' })
    setShowApproveModal(true)
  }

  const handleReject = (id) => {
    setPendingAction({ id, action: 'reject' })
    setShowApproveModal(true)
  }

  const confirmAction = () => {
    setFlaggedItems((prev) =>
      prev.filter((item) => item.id !== pendingAction.id)
    )
    setShowApproveModal(false)
    setPendingAction(null)
  }

  const BIAS_DATA = [
    {
      dimension: 'GENDER BIAS IN EVALUATIONS',
      score:     0.04,
      status:    'CLEAN',
      detail:    'Score variance < 2% across gender groups. 1,247 evaluations analyzed.',
    },
    {
      dimension: 'REGIONAL LANGUAGE BIAS',
      score:     0.11,
      status:    'LOW',
      detail:    'Slight preference for formal English detected. Monitoring active.',
    },
    {
      dimension: 'DIFFICULTY CALIBRATION',
      score:     0.08,
      status:    'CLEAN',
      detail:    'Question difficulty matches target grade levels within 5% margin.',
    },
    {
      dimension: 'SALES RECOMMENDATION FAIRNESS',
      score:     0.03,
      status:    'CLEAN',
      detail:    'Equal quality recommendations across all customer profiles.',
    },
    {
      dimension: 'CONTENT CULTURAL SENSITIVITY',
      score:     0.15,
      status:    'LOW',
      detail:    'Some cultural context gaps in STEM examples. Review scheduled.',
    },
  ]

  const RATE_LIMIT_DATA = [
    { ip: '192.168.1.45',  requests: 101, limit: '100/hr', status: 'BLOCKED'  },
    { ip: '10.0.0.128',    requests: 87,  limit: '100/hr', status: 'WARNING'  },
    { ip: '172.16.0.23',   requests: 54,  limit: '100/hr', status: 'NORMAL'   },
    { ip: '192.168.2.101', requests: 12,  limit: '100/hr', status: 'NORMAL'   },
    { ip: '10.0.1.55',     requests: 3,   limit: '100/hr', status: 'NORMAL'   },
  ]

  const PRIVACY_LOG = [
    { time: '14:32:01', event: 'Voice data purged',         session: '#441', detail: 'Post-transcription — 2.3MB deleted'       },
    { time: '13:18:44', event: 'PDF document deleted',      session: '#390', detail: 'Post-spell-check — 1.1MB deleted'          },
    { time: '12:45:22', event: 'Answer hash logged',        session: '#381', detail: 'Raw answer not stored — SHA-256 hash only' },
    { time: '11:30:11', event: '90-day retention purge',    session: 'BATCH', detail: '124 old audit records purged'             },
    { time: '10:15:09', event: 'User consent recorded',     session: '#340', detail: 'Recording consent: YES — session started'  },
  ]

  const tabsData = [
    {
      id:    'flagged',
      label: 'FLAGGED ITEMS',
      count: flaggedItems.length,
      content: (
        <div style={{
          display:       'flex',
          flexDirection: 'column',
          gap:           'var(--space-4)',
          padding:       'var(--space-6) 0',
        }}>
          {flaggedItems.length === 0 ? (
            <div style={{
              padding:    'var(--space-16)',
              textAlign:  'center',
              border:     'var(--border-dashed)',
              background: 'var(--surface)',
            }}>
              <div style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h2)',
                fontWeight:    700,
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-tight)',
                color:         'var(--term-green)',
                marginBottom:  'var(--space-3)',
              }}>
                ✓ ALL CLEAR
              </div>
              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   'var(--fs-data)',
                color:      'var(--muted)',
              }}>
                No items require human review
              </p>
            </div>
          ) : (
            flaggedItems.map((item) => (
              <FlaggedItemCard
                key={item.id}
                item={item}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            ))
          )}
        </div>
      ),
    },
    {
      id:    'bias',
      label: 'BIAS REPORT',
      content: (
        <div style={{ padding: 'var(--space-6) 0' }}>
          <div style={{
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'space-between',
            marginBottom:   'var(--space-6)',
            padding:        'var(--space-4)',
            background:     'var(--term-green-dim)',
            border:         '1px solid var(--term-green)',
            borderLeft:     '4px solid var(--term-green)',
          }}>
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-data)',
              color:         'var(--term-green)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wide)',
            }}>
              ✓ OVERALL BIAS LEVEL: LOW — SYSTEM OPERATING FAIRLY
            </span>
            <Badge variant="green">LAST SCAN: 2H AGO</Badge>
          </div>

          <BiasReportChart data={BIAS_DATA} />

          <div style={{
            marginTop:   'var(--space-6)',
            padding:     'var(--space-5)',
            background:  'var(--surface)',
            border:      'var(--border)',
          }}>
            <div style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              color:         'var(--muted)',
              marginBottom:  'var(--space-4)',
            }}>
              MULTI-MODEL VOTING SYSTEM
            </div>
            <div style={{
              display:             'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap:                 'var(--space-4)',
            }}>
              {[
                { model: 'Groq LLaMA', weight: '50%', votes: 1247, color: 'var(--accent-primary)' },
                { model: 'Gemini 1.5', weight: '30%', votes: 748,  color: 'var(--accent-cyber)'   },
                { model: 'Similarity', weight: '20%', votes: 1247, color: 'var(--term-green)'     },
              ].map((m) => (
                <div key={m.model} style={{
                  padding:    'var(--space-4)',
                  border:     `1px solid ${m.color}`,
                  background: `color-mix(in srgb, ${m.color} 5%, var(--base))`,
                }}>
                  <div style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                    color:         m.color,
                    marginBottom:  'var(--space-2)',
                    fontWeight:    700,
                  }}>
                    {m.model}
                  </div>
                  <div style={{
                    fontFamily:    'var(--font-heading)',
                    fontSize:      'var(--fs-h3)',
                    fontWeight:    700,
                    letterSpacing: 'var(--ls-tight)',
                    color:         'var(--ink)',
                    marginBottom:  'var(--space-1)',
                  }}>
                    {m.weight}
                  </div>
                  <div style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    color:         'var(--muted)',
                    textTransform: 'uppercase',
                  }}>
                    WEIGHT — {m.votes} VOTES
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
    },
    {
      id:    'ratelimit',
      label: 'RATE LIMITS',
      content: (
        <div style={{ padding: 'var(--space-6) 0' }}>
          <div style={{
            display:             'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap:                 'var(--space-4)',
            marginBottom:        'var(--space-6)',
          }}>
            {[
              { label: 'LIMIT PER IP',    value: '100 req/hr',  color: 'var(--accent-primary)' },
              { label: 'LIMIT PER USER',  value: '500 req/day', color: 'var(--accent-cyber)'   },
              { label: 'BURST LIMIT',     value: '10 req/sec',  color: 'var(--term-amber)'     },
            ].map((s) => (
              <div key={s.label} style={{
                padding:    'var(--space-5)',
                border:     `2px solid ${s.color}`,
                boxShadow:  `4px 4px 0px ${s.color}`,
                background: 'var(--base)',
              }}>
                <div style={{
                  fontFamily:    'var(--font-heading)',
                  fontSize:      'var(--fs-h3)',
                  fontWeight:    700,
                  letterSpacing: 'var(--ls-tight)',
                  color:         s.color,
                  marginBottom:  'var(--space-1)',
                }}>
                  {s.value}
                </div>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  color:         'var(--muted)',
                }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>

          <RateLimitMonitor data={RATE_LIMIT_DATA} />
        </div>
      ),
    },
    {
      id:    'privacy',
      label: 'DATA PRIVACY',
      content: (
        <div style={{ padding: 'var(--space-6) 0' }}>
          <div style={{
            display:             'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap:                 'var(--space-4)',
            marginBottom:        'var(--space-6)',
          }}>
            {[
              {
                label:   'RAW DATA STORED',
                value:   'NEVER',
                desc:    'Answers hashed, voice deleted post-transcription',
                color:   'var(--term-green)',
                variant: 'green',
              },
              {
                label:   'RETENTION POLICY',
                value:   '90 DAYS',
                desc:    'Audit logs retained 90 days then auto-purged',
                color:   'var(--accent-cyber)',
                variant: 'cyber',
              },
              {
                label:   'GDPR COMPLIANCE',
                value:   'ACTIVE',
                desc:    'Data handling follows GDPR-inspired policies',
                color:   'var(--term-green)',
                variant: 'green',
              },
              {
                label:   'USER CONSENT',
                value:   'REQUIRED',
                desc:    'Session recording requires explicit consent',
                color:   'var(--term-amber)',
                variant: 'amber',
              },
            ].map((item) => (
              <div key={item.label} style={{
                padding:    'var(--space-5)',
                border:     `2px solid ${item.color}`,
                boxShadow:  `4px 4px 0px ${item.color}`,
                background: 'var(--base)',
              }}>
                <div style={{
                  display:        'flex',
                  justifyContent: 'space-between',
                  alignItems:     'flex-start',
                  marginBottom:   'var(--space-3)',
                }}>
                  <span style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wider)',
                    color:         'var(--muted)',
                  }}>
                    {item.label}
                  </span>
                  <Badge variant={item.variant}>
                    {item.value}
                  </Badge>
                </div>
                <p style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--muted)',
                  lineHeight:    1.5,
                }}>
                  {item.desc}
                </p>
              </div>
            ))}
          </div>

          {/* Privacy event log */}
          <div style={{
            border:     'var(--border)',
            background: 'var(--base)',
          }}>
            <div style={{
              padding:      'var(--space-4) var(--space-5)',
              borderBottom: 'var(--border)',
              background:   'var(--surface)',
            }}>
              <span style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h4)',
                fontWeight:    700,
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-tight)',
              }}>
                PRIVACY EVENT LOG
              </span>
            </div>

            {PRIVACY_LOG.map((log, i) => (
              <div
                key={i}
                style={{
                  display:             'grid',
                  gridTemplateColumns: '80px 1fr 80px 1fr',
                  gap:                 'var(--space-4)',
                  padding:             'var(--space-4) var(--space-5)',
                  borderBottom:        i < PRIVACY_LOG.length - 1
                    ? 'var(--border-thin)'
                    : 'none',
                  alignItems:          'center',
                }}
              >
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--muted)',
                  textTransform: 'uppercase',
                }}>
                  {log.time}
                </span>
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-data)',
                  color:         'var(--ink)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                  fontWeight:    700,
                }}>
                  {log.event}
                </span>
                <Badge variant="default">
                  {log.session}
                </Badge>
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--muted)',
                }}>
                  {log.detail}
                </span>
              </div>
            ))}
          </div>
        </div>
      ),
    },
  ]

  return (
    <div style={{ padding: 'var(--space-8)' }}>

      {/* ── PAGE HEADER ───────────────────────────────── */}
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
            // ADMIN — AI GOVERNANCE
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            GOVERNANCE<br />
            <span style={{ color: 'var(--accent-primary)' }}>DASHBOARD</span>
          </h1>
        </div>

        <div style={{
          display:    'flex',
          gap:        'var(--space-3)',
          flexWrap:   'wrap',
        }}>
          <Badge variant="green" dot pulse>
            7 PILLARS ACTIVE
          </Badge>
          {flaggedItems.length > 0 && (
            <Badge variant="amber" dot>
              {flaggedItems.length} ITEMS NEED REVIEW
            </Badge>
          )}
          <Link to="/admin/audit">
            <Button variant="surface" size="sm">
              AUDIT LOGS →
            </Button>
          </Link>
        </div>
      </div>

      {/* ── GOVERNANCE OVERVIEW STATS ─────────────────── */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap:                 'var(--space-4)',
        marginBottom:        'var(--space-8)',
      }}>
        {[
          { label: 'CONTENT FILTERED',   value: 0,    color: 'var(--term-green)',     desc: 'harmful outputs blocked' },
          { label: 'FLAGGED FOR REVIEW', value: flaggedItems.length, color: 'var(--term-amber)', desc: 'awaiting human review' },
          { label: 'BIAS SCORE',         value: '0.08', color: 'var(--term-green)',   desc: 'overall bias index'      },
          { label: 'IPs BLOCKED',        value: 1,    color: 'var(--term-red)',        desc: 'rate limit violations'   },
        ].map((s) => (
          <div key={s.label} style={{
            background:  'var(--base)',
            border:      'var(--border)',
            boxShadow:   'var(--shadow)',
            padding:     'var(--space-5)',
            borderTop:   `4px solid ${s.color}`,
          }}>
            <div style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      'var(--fs-h2)',
              fontWeight:    700,
              letterSpacing: 'var(--ls-tight)',
              color:         s.color,
              lineHeight:    1,
              marginBottom:  'var(--space-1)',
            }}>
              {s.value}
            </div>
            <div style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              color:         'var(--muted)',
              marginBottom:  'var(--space-1)',
            }}>
              {s.label}
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize:   'var(--fs-nano)',
              color:      'var(--muted)',
              opacity:    0.7,
            }}>
              {s.desc}
            </div>
          </div>
        ))}
      </div>

      {/* ── TABS ──────────────────────────────────────── */}
      <Tabs tabs={tabsData} defaultTab="flagged" />

      {/* ── APPROVE/REJECT CONFIRMATION MODAL ─────────── */}
      <Modal
        isOpen={showApproveModal}
        onClose={() => setShowApproveModal(false)}
        title={`CONFIRM ${pendingAction?.action?.toUpperCase()}`}
        size="sm"
        footer={
          <>
            <Button
              variant={pendingAction?.action === 'approve' ? 'green' : 'danger'}
              onClick={confirmAction}
            >
              {pendingAction?.action === 'approve'
                ? '✓ CONFIRM APPROVE'
                : '✕ CONFIRM REJECT'}
            </Button>
            <Button
              variant="ghost"
              onClick={() => setShowApproveModal(false)}
            >
              CANCEL
            </Button>
          </>
        }
      >
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize:   'var(--fs-data)',
          color:      'var(--ink)',
          lineHeight: 1.7,
        }}>
          {pendingAction?.action === 'approve'
            ? `You are approving item #${pendingAction?.id}. This will mark it as human-reviewed and remove it from the flagged queue.`
            : `You are rejecting item #${pendingAction?.id}. This will mark the AI output as incorrect and remove it from the queue.`}
        </p>
        <div style={{
          marginTop:   'var(--space-4)',
          padding:     'var(--space-3)',
          background:  'var(--surface)',
          border:      'var(--border-thin)',
          borderLeft:  '3px solid var(--term-amber)',
          fontFamily:  'var(--font-mono)',
          fontSize:    'var(--fs-nano)',
          color:       'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
        }}>
          ⚡ THIS ACTION WILL BE RECORDED IN THE AUDIT LOG
        </div>
      </Modal>

      {/* Responsive */}
      <style>{`
        @media (max-width: 900px) {
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          div[style*="repeat(3, 1fr)"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="repeat(2, 1fr)"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  )
}
