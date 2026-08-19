	/* ============================================================
   EDUMIND AI — AUDIT LOGS PAGE
   Complete AI decision audit trail
   ============================================================ */

import React, { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { formatRelative } from '@utils/formatters'
import { copyToClipboard } from '@utils/helpers'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import Modal from '@components/ui/Modal'
import toast from 'react-hot-toast'

/* ── DEMO AUDIT LOG DATA ────────────────────────────────────── */
const DEMO_LOGS = Array.from({ length: 40 }, (_, i) => {
  const challenges  = ['evaluator', 'generator', 'spelling', 'voice_tutor', 'sales']
  const models      = ['Groq LLaMA 3.3-70B', 'Gemini 1.5 Flash', 'Whisper Large']
  const statuses    = ['PASS', 'PASS', 'PASS', 'PASS', 'FLAG']
  const challenge   = challenges[i % challenges.length]
  const model       = models[i % models.length]
  const status      = statuses[i % statuses.length]
  const confidence  = status === 'FLAG'
    ? 0.5 + Math.random() * 0.1
    : 0.7 + Math.random() * 0.3

  return {
    id:           8831 - i,
    request_id:   `req_${Math.random().toString(36).slice(2, 10)}`,
    timestamp:    new Date(Date.now() - i * 180000).toISOString(),
    challenge,
    model,
    model_version:'v1.0',
    prompt_version:'v2.1',
    status,
    confidence:   Number(confidence.toFixed(2)),
    latency:      `${(Math.random() * 3 + 0.5).toFixed(1)}ms`,
    user_id:      `usr_${Math.floor(Math.random() * 100)}`,
    output_summary: status === 'FLAG'
      ? 'Low confidence score — flagged for human review'
      : `${challenge.replace('_', ' ')} processed successfully`,
  }
})

/* ── CHALLENGE COLOR MAP ────────────────────────────────────── */
const CHALLENGE_COLORS = {
  evaluator:   'var(--accent-primary)',
  generator:   'var(--accent-cyber)',
  spelling:    'var(--term-amber)',
  voice_tutor: 'var(--term-green)',
  sales:       'var(--accent-purple)',
}

const CHALLENGE_LABELS = {
  evaluator:   'EVALUATOR',
  generator:   'GENERATOR',
  spelling:    'SPELL CHECK',
  voice_tutor: 'VOICE TUTOR',
  sales:       'SALES AI',
}

/* ── LOG ROW ────────────────────────────────────────────────── */
function LogRow({ log, onSelect }) {
  const color = CHALLENGE_COLORS[log.challenge] || 'var(--muted)'

  return (
    <div
      onClick={() => onSelect(log)}
      style={{
        display:             'grid',
        gridTemplateColumns: '80px 120px 100px 100px 80px 80px 1fr 80px',
        gap:                 'var(--space-3)',
        padding:             'var(--space-3) var(--space-5)',
        borderBottom:        'var(--border-thin)',
        alignItems:          'center',
        cursor:              'pointer',
        transition:          'background 0.12s ease',
      }}
      onMouseEnter={(e) =>
        (e.currentTarget.style.background = 'var(--surface)')
      }
      onMouseLeave={(e) =>
        (e.currentTarget.style.background = 'transparent')
      }
    >
      {/* ID */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        textAlign:     'center',
      }}>
        #{log.id}
      </span>

      {/* Timestamp */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-wide)',
      }}>
        {formatRelative(log.timestamp)}
      </span>

      {/* Challenge */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-wide)',
        color,
        fontWeight:    700,
      }}>
        {CHALLENGE_LABELS[log.challenge]}
      </span>

      {/* Model */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        textTransform: 'uppercase',
        overflow:      'hidden',
        textOverflow:  'ellipsis',
        whiteSpace:    'nowrap',
      }}>
        {log.model.split(' ')[0]}
      </span>

      {/* Confidence */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        fontWeight:    700,
        color:         log.confidence >= 0.7
          ? 'var(--term-green)'
          : log.confidence >= 0.6
            ? 'var(--term-amber)'
            : 'var(--term-red)',
        textAlign:     'right',
      }}>
        {(log.confidence * 100).toFixed(0)}%
      </span>

      {/* Latency */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--term-green)',
        textAlign:     'right',
      }}>
        {log.latency}
      </span>

      {/* Summary */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        overflow:      'hidden',
        textOverflow:  'ellipsis',
        whiteSpace:    'nowrap',
      }}>
        {log.output_summary}
      </span>

      {/* Status */}
      <Badge
        variant={log.status === 'PASS' ? 'green' : 'amber'}
        dot={log.status === 'FLAG'}
      >
        {log.status}
      </Badge>
    </div>
  )
}

/* ── MAIN AUDIT LOGS PAGE ───────────────────────────────────── */
export default function AuditLogs() {
  const [searchQuery,   setSearchQuery]   = useState('')
  const [filterChallenge, setFilterChallenge] = useState('ALL')
  const [filterStatus,  setFilterStatus]  = useState('ALL')
  const [currentPage,   setCurrentPage]   = useState(1)
  const [selectedLog,   setSelectedLog]   = useState(null)
  const ITEMS_PER_PAGE = 15

  /* ── FILTER LOGS ──────────────────────────────────────── */
  const filteredLogs = useMemo(() => {
    return DEMO_LOGS.filter((log) => {
      const matchSearch = searchQuery
        ? log.request_id.includes(searchQuery) ||
          log.output_summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
          log.user_id.includes(searchQuery)
        : true

      const matchChallenge = filterChallenge === 'ALL'
        ? true
        : log.challenge === filterChallenge

      const matchStatus = filterStatus === 'ALL'
        ? true
        : log.status === filterStatus

      return matchSearch && matchChallenge && matchStatus
    })
  }, [searchQuery, filterChallenge, filterStatus])

  /* ── PAGINATION ───────────────────────────────────────── */
  const totalPages  = Math.ceil(filteredLogs.length / ITEMS_PER_PAGE)
  const paginatedLogs = filteredLogs.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  )

  const handleCopyRequestId = async (id) => {
    await copyToClipboard(id)
    toast.success('[ COPIED ] Request ID copied')
  }

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
            // ADMIN — AUDIT TRAIL
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            AUDIT<br />
            <span style={{ color: 'var(--accent-primary)' }}>LOGS</span>
          </h1>
        </div>

        <div style={{
          display:    'flex',
          gap:        'var(--space-3)',
          flexWrap:   'wrap',
          alignItems: 'flex-start',
        }}>
          <Badge variant="green" dot>
            {DEMO_LOGS.length} TOTAL RECORDS
          </Badge>
          <Badge variant="amber">
            {DEMO_LOGS.filter((l) => l.status === 'FLAG').length} FLAGGED
          </Badge>
          <Link to="/admin/governance">
            <Button variant="surface" size="sm">
              GOVERNANCE →
            </Button>
          </Link>
        </div>
      </div>

      {/* ── STATS STRIP ───────────────────────────────── */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap:                 'var(--space-3)',
        marginBottom:        'var(--space-6)',
      }}>
        {Object.entries(CHALLENGE_LABELS).map(([key, label]) => {
          const count = DEMO_LOGS.filter((l) => l.challenge === key).length
          const color = CHALLENGE_COLORS[key]
          return (
            <button
              key={key}
              onClick={() => {
                setFilterChallenge(
                  filterChallenge === key ? 'ALL' : key
                )
                setCurrentPage(1)
              }}
              style={{
                background:  filterChallenge === key
                  ? `color-mix(in srgb, ${color} 10%, var(--base))`
                  : 'var(--base)',
                border:      filterChallenge === key
                  ? `2px solid ${color}`
                  : 'var(--border)',
                boxShadow:   filterChallenge === key
                  ? `3px 3px 0px ${color}`
                  : 'var(--shadow-sm)',
                padding:     'var(--space-4)',
                cursor:      'pointer',
                textAlign:   'left',
                transition:  'all 0.12s ease',
              }}
            >
              <div style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h3)',
                fontWeight:    700,
                letterSpacing: 'var(--ls-tight)',
                color,
                lineHeight:    1,
                marginBottom:  'var(--space-1)',
              }}>
                {count}
              </div>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wide)',
                color:         filterChallenge === key ? color : 'var(--muted)',
              }}>
                {label}
              </div>
            </button>
          )
        })}
      </div>

      {/* ── FILTERS BAR ───────────────────────────────── */}
      <div style={{
        display:      'flex',
        gap:          'var(--space-4)',
        marginBottom: 'var(--space-5)',
        flexWrap:     'wrap',
        alignItems:   'center',
      }}>
        {/* Search */}
        <input
          type="text"
          placeholder="SEARCH BY REQUEST ID, USER, OUTPUT..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value)
            setCurrentPage(1)
          }}
          style={{
            flex:          1,
            minWidth:      '240px',
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
            color:         'var(--ink)',
            background:    'var(--base)',
            border:        'var(--border-thin)',
            outline:       'none',
            padding:       '0.55rem 1rem',
          }}
        />

        {/* Status filter */}
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          {['ALL', 'PASS', 'FLAG'].map((s) => (
            <button
              key={s}
              onClick={() => {
                setFilterStatus(s)
                setCurrentPage(1)
              }}
              style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                padding:       '0.4rem 0.8rem',
                border:        filterStatus === s
                  ? 'var(--border)'
                  : 'var(--border-thin)',
                background:    filterStatus === s
                  ? 'var(--ink)'
                  : 'var(--base)',
                color:         filterStatus === s
                  ? 'var(--base)'
                  : 'var(--muted)',
                cursor:        'pointer',
                transition:    'all 0.12s ease',
              }}
            >
              {s}
            </button>
          ))}
        </div>

        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
          marginLeft:    'auto',
        }}>
          {filteredLogs.length} RESULTS
        </span>
      </div>

      {/* ── TABLE ─────────────────────────────────────── */}
      <div style={{
        background:   'var(--base)',
        border:       'var(--border)',
        boxShadow:    'var(--shadow)',
        marginBottom: 'var(--space-6)',
      }}>
        {/* Column headers */}
        <div style={{
          display:             'grid',
          gridTemplateColumns: '80px 120px 100px 100px 80px 80px 1fr 80px',
          gap:                 'var(--space-3)',
          padding:             'var(--space-3) var(--space-5)',
          borderBottom:        'var(--border)',
          background:          'var(--surface)',
        }}>
          {['ID', 'TIME', 'ENGINE', 'MODEL', 'CONF', 'LATENCY', 'SUMMARY', 'STATUS'].map((h) => (
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

        {/* Log rows */}
        {paginatedLogs.length > 0 ? (
          paginatedLogs.map((log) => (
            <LogRow
              key={log.id}
              log={log}
              onSelect={setSelectedLog}
            />
          ))
        ) : (
          <div style={{
            padding:    'var(--space-16)',
            textAlign:  'center',
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-data)',
            color:      'var(--muted)',
            textTransform:'uppercase',
            letterSpacing:'var(--ls-wider)',
          }}>
            NO LOGS MATCH YOUR FILTER
          </div>
        )}
      </div>

      {/* ── PAGINATION ────────────────────────────────── */}
      {totalPages > 1 && (
        <div style={{
          display:        'flex',
          justifyContent: 'center',
          alignItems:     'center',
          gap:            'var(--space-3)',
        }}>
          <Button
            variant="surface"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
          >
            ← PREV
          </Button>

          <div style={{ display: 'flex', gap: 'var(--space-1)' }}>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const page = i + 1
              return (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  style={{
                    width:      '36px',
                    height:     '36px',
                    fontFamily: 'var(--font-mono)',
                    fontSize:   'var(--fs-nano)',
                    fontWeight: 700,
                    border:     currentPage === page
                      ? 'var(--border)'
                      : 'var(--border-thin)',
                    background: currentPage === page
                      ? 'var(--ink)'
                      : 'var(--base)',
                    color:      currentPage === page
                      ? 'var(--base)'
                      : 'var(--muted)',
                    cursor:     'pointer',
                    transition: 'all 0.12s ease',
                  }}
                >
                  {page}
                </button>
              )
            })}
            {totalPages > 5 && (
              <span style={{
                display:    'flex',
                alignItems: 'center',
                fontFamily: 'var(--font-mono)',
                fontSize:   'var(--fs-nano)',
                color:      'var(--muted)',
                padding:    '0 var(--space-2)',
              }}>
                ...{totalPages}
              </span>
            )}
          </div>

          <Button
            variant="surface"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
          >
            NEXT →
          </Button>
        </div>
      )}

      {/* ── LOG DETAIL MODAL ──────────────────────────── */}
      <Modal
        isOpen={!!selectedLog}
        onClose={() => setSelectedLog(null)}
        title={`AUDIT RECORD #${selectedLog?.id}`}
        size="md"
      >
        {selectedLog && (
          <div style={{
            display:       'flex',
            flexDirection: 'column',
            gap:           'var(--space-5)',
          }}>
            {/* Field grid */}
            <div style={{
              display:             'grid',
              gridTemplateColumns: '1fr 1fr',
              gap:                 'var(--space-4)',
            }}>
              {[
                { label: 'REQUEST ID',     value: selectedLog.request_id },
                { label: 'USER ID',        value: selectedLog.user_id    },
                { label: 'ENGINE',         value: CHALLENGE_LABELS[selectedLog.challenge] },
                { label: 'MODEL',          value: selectedLog.model      },
                { label: 'MODEL VERSION',  value: selectedLog.model_version    },
                { label: 'PROMPT VERSION', value: selectedLog.prompt_version   },
                { label: 'CONFIDENCE',     value: `${(selectedLog.confidence * 100).toFixed(1)}%` },
                { label: 'LATENCY',        value: selectedLog.latency    },
              ].map((field) => (
                <div
                  key={field.label}
                  style={{
                    padding:    'var(--space-3)',
                    background: 'var(--surface)',
                    border:     'var(--border-thin)',
                  }}
                >
                  <div style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wider)',
                    color:         'var(--muted)',
                    marginBottom:  'var(--space-1)',
                  }}>
                    {field.label}
                  </div>
                  <div style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-data)',
                    fontWeight:    700,
                    color:         'var(--ink)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                  }}>
                    {field.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Output summary */}
            <div>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color:         'var(--muted)',
                marginBottom:  'var(--space-2)',
              }}>
                OUTPUT SUMMARY
              </div>
              <div style={{
                padding:    'var(--space-4)',
                background: 'var(--surface)',
                border:     'var(--border-thin)',
                borderLeft: selectedLog.status === 'FLAG'
                  ? '3px solid var(--term-amber)'
                  : '3px solid var(--term-green)',
                fontFamily: 'var(--font-mono)',
                fontSize:   'var(--fs-data)',
                color:      'var(--ink)',
                lineHeight: 1.6,
              }}>
                {selectedLog.output_summary}
              </div>
            </div>

            {/* Governance status */}
            <div style={{
              display:    'flex',
              gap:        'var(--space-3)',
              flexWrap:   'wrap',
            }}>
              <Badge
                variant={selectedLog.status === 'PASS' ? 'green' : 'amber'}
                dot
              >
                GOVERNANCE: {selectedLog.status}
              </Badge>
              <Badge variant="default">
                {new Date(selectedLog.timestamp).toLocaleString()}
              </Badge>
            </div>

            {/* Copy request ID */}
            <Button
              variant="surface"
              size="sm"
              onClick={() => handleCopyRequestId(selectedLog.request_id)}
            >
              COPY REQUEST ID
            </Button>
          </div>
        )}
      </Modal>

      {/* Responsive */}
      <style>{`
        @media (max-width: 1024px) {
          div[style*="80px 120px 100px 100px 80px 80px 1fr 80px"] {
            grid-template-columns: 60px 1fr 80px 80px !important;
          }
        }
        @media (max-width: 600px) {
          div[style*="repeat(5, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
      `}</style>
    </div>
  )
}
