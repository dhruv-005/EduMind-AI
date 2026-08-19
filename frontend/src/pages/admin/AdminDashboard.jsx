/* ============================================================
   EDUMIND AI — ADMIN DASHBOARD PAGE
   Platform overview with governance stats
   ============================================================ */

import React from 'react'
import { Link } from 'react-router-dom'
import { useCountUp } from '@hooks/useCountUp'
import { useIntersection } from '@hooks/useIntersection'
import { useSparkline } from '@hooks/useSparkline'
import { Sparkline } from '@components/ui/Sparkline'
import Badge from '@components/ui/Badge'
import Button from '@components/ui/Button'
import ProgressBar from '@components/ui/ProgressBar'

/* ── STAT CARD ──────────────────────────────────────────────── */
function AdminStatCard({ label, value, suffix, color, delta, index }) {
  const { ref, hasTriggered } = useIntersection({ once: true })
  const { displayValue } = useCountUp({
    end:      parseFloat(value),
    decimals: String(value).includes('.') ? 1 : 0,
    duration: 1500,
    trigger:  hasTriggered,
    suffix:   suffix || '',
  })

  return (
    <div
      ref={ref}
      style={{
        background:  'var(--base)',
        border:      'var(--border)',
        boxShadow:   'var(--shadow)',
        padding:     'var(--space-6)',
        borderLeft:  `4px solid ${color}`,
        opacity:     hasTriggered ? 1 : 0,
        transform:   hasTriggered ? 'translateY(0)' : 'translateY(16px)',
        transition:  `opacity 0.4s ease ${index * 0.08}s,
                      transform 0.4s ease ${index * 0.08}s`,
      }}
    >
      <div style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-widest)',
        color:         'var(--muted)',
        marginBottom:  'var(--space-3)',
      }}>
        {label}
      </div>
      <div style={{
        fontFamily:    'var(--font-heading)',
        fontSize:      'var(--fs-h1)',
        fontWeight:    700,
        letterSpacing: 'var(--ls-tight)',
        lineHeight:    1,
        color,
        marginBottom:  'var(--space-2)',
      }}>
        {displayValue}
      </div>
      {delta && (
        <div style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--term-green)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
        }}>
          ↑ {delta}
        </div>
      )}
    </div>
  )
}

/* ── ENGINE STATUS ROW ──────────────────────────────────────── */
function EngineStatusRow({ num, name, status, calls, latency, color }) {
  return (
    <div style={{
      display:        'grid',
      gridTemplateColumns: '40px 1fr 80px 60px 60px 120px',
      gap:            'var(--space-4)',
      padding:        'var(--space-4) var(--space-5)',
      borderBottom:   'var(--border-thin)',
      alignItems:     'center',
    }}>
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         color,
        fontWeight:    700,
      }}>
        {num}
      </span>

      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-data)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-wide)',
        color:         'var(--ink)',
      }}>
        {name}
      </span>

      <Badge
        variant={status === 'ACTIVE' ? 'green' : 'amber'}
        dot={status === 'ACTIVE'}
        pulse={status === 'ACTIVE'}
      >
        {status}
      </Badge>

      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        textAlign:     'right',
      }}>
        {calls}
      </span>

      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--term-green)',
        textAlign:     'right',
      }}>
        {latency}
      </span>

      <div style={{ width: '100%' }}>
        <Sparkline bars={12} height={20} color={color} interval={2500} />
      </div>
    </div>
  )
}

/* ── GOVERNANCE PILLAR ──────────────────────────────────────── */
function GovernancePillar({ num, label, status, detail, color }) {
  return (
    <div style={{
      padding:     'var(--space-5)',
      border:      'var(--border)',
      boxShadow:   'var(--shadow-sm)',
      background:  'var(--base)',
      transition:  'transform 0.12s ease, box-shadow 0.12s ease',
    }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translate(-3px,-3px)'
        e.currentTarget.style.boxShadow = `6px 6px 0px ${color}`
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translate(0,0)'
        e.currentTarget.style.boxShadow = 'var(--shadow-sm)'
      }}
    >
      <div style={{
        display:        'flex',
        justifyContent: 'space-between',
        alignItems:     'flex-start',
        marginBottom:   'var(--space-3)',
      }}>
        <span style={{
          fontFamily:    'var(--font-heading)',
          fontSize:      'var(--fs-h3)',
          fontWeight:    700,
          letterSpacing: 'var(--ls-tight)',
          color,
          lineHeight:    1,
        }}>
          {num}
        </span>
        <Badge variant={status === 'ACTIVE' ? 'green' : 'amber'} dot>
          {status}
        </Badge>
      </div>
      <div style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        fontWeight:    700,
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-wider)',
        color:         'var(--ink)',
        marginBottom:  'var(--space-2)',
      }}>
        {label}
      </div>
      <p style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        lineHeight:    1.5,
      }}>
        {detail}
      </p>
    </div>
  )
}

/* ── MAIN ADMIN DASHBOARD ───────────────────────────────────── */
export default function AdminDashboard() {
  const ENGINES = [
    {
      num:     'CH-01',
      name:    'AI EVALUATOR',
      status:  'ACTIVE',
      calls:   '1.2K',
      latency: '1.2ms',
      color:   'var(--accent-primary)',
    },
    {
      num:     'CH-02',
      name:    'Q GENERATOR',
      status:  'ACTIVE',
      calls:   '489',
      latency: '3.4ms',
      color:   'var(--accent-cyber)',
    },
    {
      num:     'CH-03',
      name:    'SPELL CHECK',
      status:  'ACTIVE',
      calls:   '892',
      latency: '2.1ms',
      color:   'var(--term-amber)',
    },
    {
      num:     'CH-04',
      name:    'VOICE TUTOR',
      status:  'ACTIVE',
      calls:   '341',
      latency: '490ms',
      color:   'var(--term-green)',
    },
    {
      num:     'CH-05',
      name:    'SALES AI',
      status:  'ACTIVE',
      calls:   '203',
      latency: '1.8ms',
      color:   'var(--accent-purple)',
    },
  ]

  const PILLARS = [
    {
      num:    '01',
      label:  'CONTENT SAFETY',
      status: 'ACTIVE',
      detail: 'Input + output filtering active. 0 harmful outputs blocked today.',
      color:  'var(--accent-primary)',
    },
    {
      num:    '02',
      label:  'AUDIT TRAIL',
      status: 'ACTIVE',
      detail: '8,831 decisions logged. 90-day retention policy active.',
      color:  'var(--accent-cyber)',
    },
    {
      num:    '03',
      label:  'HUMAN OVERSIGHT',
      status: 'ACTIVE',
      detail: '3 items in review queue. 12 approved today.',
      color:  'var(--term-green)',
    },
    {
      num:    '04',
      label:  'BIAS DETECTION',
      status: 'ACTIVE',
      detail: 'No significant bias patterns detected. Last scan: 2h ago.',
      color:  'var(--term-amber)',
    },
    {
      num:    '05',
      label:  'RATE LIMITING',
      status: 'ACTIVE',
      detail: '100 req/hr per IP. 2 IPs throttled today.',
      color:  'var(--accent-primary)',
    },
    {
      num:    '06',
      label:  'DATA PRIVACY',
      status: 'ACTIVE',
      detail: 'No raw data stored. Voice data deleted post-transcription.',
      color:  'var(--accent-cyber)',
    },
    {
      num:    '07',
      label:  'MODEL VERSIONING',
      status: 'ACTIVE',
      detail: 'Primary: Groq LLaMA 3.3-70B. Fallback chain ready.',
      color:  'var(--term-green)',
    },
  ]

  const RECENT_EVENTS = [
    { time: '14:32:01', type: 'AUDIT',     msg: 'Evaluation #8831 logged — score 8.2/10',         color: 'var(--accent-cyber)'   },
    { time: '14:31:44', type: 'GOVERN',    msg: 'Content filter: clean output — evaluator',        color: 'var(--term-green)'     },
    { time: '14:30:12', type: 'RATE',      msg: 'IP 192.168.1.45 throttled — 101 req/hr',          color: 'var(--term-amber)'     },
    { time: '14:28:55', type: 'MODEL',     msg: 'Groq LLaMA 3.3-70B responding — 1.4ms latency',  color: 'var(--accent-primary)' },
    { time: '14:27:33', type: 'BIAS',      msg: 'Bias scan complete — no patterns detected',       color: 'var(--term-green)'     },
    { time: '14:25:11', type: 'HUMAN',     msg: 'Evaluation #8828 flagged for review — conf 0.58', color: 'var(--term-amber)'     },
    { time: '14:24:00', type: 'PRIVACY',   msg: 'Voice session data purged — session #441',        color: 'var(--accent-cyber)'   },
    { time: '14:22:18', type: 'AUDIT',     msg: 'Lead score #89 — HOT tier — rep notified',        color: 'var(--term-red)'       },
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
            // ADMIN — MISSION CONTROL
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            ADMIN<br />
            <span style={{ color: 'var(--accent-primary)' }}>DASHBOARD</span>
          </h1>
        </div>

        <div style={{
          display:    'flex',
          gap:        'var(--space-3)',
          flexWrap:   'wrap',
        }}>
          <Link to="/admin/governance">
            <Button variant="primary" size="sm">
              GOVERNANCE →
            </Button>
          </Link>
          <Link to="/admin/audit">
            <Button variant="surface" size="sm">
              AUDIT LOGS →
            </Button>
          </Link>
        </div>
      </div>

      {/* ── STATS ROW ─────────────────────────────────── */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap:                 'var(--space-4)',
        marginBottom:        'var(--space-8)',
      }}>
        {[
          { label: 'TOTAL AI CALLS',    value: 8831,  suffix: '',   color: 'var(--accent-primary)', delta: '+128 today',  index: 0 },
          { label: 'CONTENT FILTERED',  value: 0,     suffix: '',   color: 'var(--term-green)',     delta: 'clean today', index: 1 },
          { label: 'FLAGGED FOR REVIEW',value: 3,     suffix: '',   color: 'var(--term-amber)',     delta: 'in queue',    index: 2 },
          { label: 'AVG LATENCY',       value: 1.4,   suffix: 'ms', color: 'var(--accent-cyber)',   delta: '-0.2ms week', index: 3 },
        ].map((s) => (
          <AdminStatCard key={s.label} {...s} />
        ))}
      </div>

      {/* ── ENGINE STATUS ─────────────────────────────── */}
      <div style={{
        background:   'var(--base)',
        border:       'var(--border)',
        boxShadow:    'var(--shadow)',
        marginBottom: 'var(--space-6)',
      }}>
        {/* Header */}
        <div style={{
          padding:      'var(--space-5) var(--space-6)',
          borderBottom: 'var(--border)',
          background:   'var(--surface)',
          display:      'flex',
          alignItems:   'center',
          justifyContent:'space-between',
        }}>
          <span style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h4)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
          }}>
            ENGINE STATUS
          </span>
          <Badge variant="green" dot pulse>
            ALL SYSTEMS OPERATIONAL
          </Badge>
        </div>

        {/* Column headers */}
        <div style={{
          display:             'grid',
          gridTemplateColumns: '40px 1fr 80px 60px 60px 120px',
          gap:                 'var(--space-4)',
          padding:             'var(--space-3) var(--space-5)',
          borderBottom:        'var(--border)',
          background:          'var(--surface)',
        }}>
          {['ID', 'ENGINE', 'STATUS', 'CALLS', 'LATENCY', 'ACTIVITY'].map((h) => (
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

        {/* Rows */}
        {ENGINES.map((e) => (
          <EngineStatusRow key={e.num} {...e} />
        ))}
      </div>

      {/* ── BOTTOM ROW ────────────────────────────────── */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: '1fr 1fr',
        gap:                 'var(--space-6)',
        marginBottom:        'var(--space-6)',
      }}>

        {/* Governance pillars */}
        <div>
          <div style={{
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'space-between',
            marginBottom:   'var(--space-5)',
          }}>
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-widest)',
              color:         'var(--muted)',
            }}>
              // GOVERNANCE PILLARS
            </span>
            <Link to="/admin/governance">
              <Button variant="ghost" size="sm">VIEW ALL →</Button>
            </Link>
          </div>

          <div style={{
            display:             'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap:                 'var(--space-3)',
          }}>
            {PILLARS.slice(0, 4).map((p) => (
              <GovernancePillar key={p.num} {...p} />
            ))}
          </div>
        </div>

        {/* Recent events */}
        <div>
          <div style={{
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'space-between',
            marginBottom:   'var(--space-5)',
          }}>
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-widest)',
              color:         'var(--muted)',
            }}>
              // RECENT EVENTS
            </span>
            <Link to="/admin/audit">
              <Button variant="ghost" size="sm">VIEW ALL →</Button>
            </Link>
          </div>

          <div style={{
            background:  'var(--term-bg)',
            border:      '1px solid var(--term-border)',
            height:      '380px',
            overflowY:   'auto',
          }}>
            {/* Terminal header */}
            <div style={{
              padding:      'var(--space-3) var(--space-4)',
              borderBottom: '1px solid var(--term-border)',
              display:      'flex',
              alignItems:   'center',
              gap:          'var(--space-2)',
            }}>
              <span style={{
                width:        '6px',
                height:       '6px',
                borderRadius: '50%',
                background:   'var(--term-green)',
                animation:    'pulseDot 2s ease-in-out infinite',
                boxShadow:    '0 0 6px var(--term-green)',
              }} />
              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                color:         'var(--term-green)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
              }}>
                GOVERNANCE EVENT STREAM
              </span>
            </div>

            {/* Events */}
            <div style={{ padding: 'var(--space-4)' }}>
              {RECENT_EVENTS.map((ev, i) => (
                <div
                  key={i}
                  style={{
                    display:      'flex',
                    gap:          'var(--space-3)',
                    marginBottom: 'var(--space-3)',
                    fontFamily:   'var(--font-mono)',
                    fontSize:     '0.65rem',
                    lineHeight:   1.5,
                  }}
                >
                  <span style={{
                    color:     'rgba(255,255,255,0.25)',
                    flexShrink:0,
                    minWidth:  '56px',
                  }}>
                    {ev.time}
                  </span>
                  <span style={{
                    color:     ev.color,
                    flexShrink:0,
                    minWidth:  '52px',
                    fontWeight:700,
                  }}>
                    [{ev.type}]
                  </span>
                  <span style={{
                    color: 'rgba(255,255,255,0.5)',
                    wordBreak: 'break-all',
                  }}>
                    {ev.msg}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── LLM FALLBACK CHAIN ────────────────────────── */}
      <div style={{
        background:  'var(--base)',
        border:      'var(--border)',
        boxShadow:   'var(--shadow)',
      }}>
        <div style={{
          padding:      'var(--space-5) var(--space-6)',
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
            LLM FALLBACK CHAIN
          </span>
        </div>

        <div style={{
          padding:             'var(--space-6)',
          display:             'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap:                 'var(--space-4)',
        }}>
          {[
            { priority: 'PRIMARY',   model: 'Groq LLaMA 3.3-70B',  status: 'ACTIVE',  latency: '1.4ms', calls: '8,203', color: 'var(--term-green)'     },
            { priority: 'FALLBACK1', model: 'Gemini 1.5 Flash',    status: 'STANDBY', latency: '2.1ms', calls: '128',   color: 'var(--term-amber)'     },
            { priority: 'FALLBACK2', model: 'Together LLaMA',      status: 'STANDBY', latency: '3.8ms', calls: '0',     color: 'var(--accent-cyber)'   },
            { priority: 'FALLBACK3', model: 'Local Ollama',         status: 'STANDBY', latency: '12ms',  calls: '0',     color: 'var(--accent-primary)' },
          ].map((m, i) => (
            <div
              key={m.priority}
              style={{
                padding:     'var(--space-5)',
                border:      `2px solid ${m.status === 'ACTIVE' ? m.color : 'var(--border-subtle)'}`,
                boxShadow:   m.status === 'ACTIVE' ? `4px 4px 0px ${m.color}` : 'none',
                background:  m.status === 'ACTIVE'
                  ? `color-mix(in srgb, ${m.color} 5%, var(--base))`
                  : 'var(--surface)',
              }}
            >
              <div style={{
                display:        'flex',
                justifyContent: 'space-between',
                alignItems:     'center',
                marginBottom:   'var(--space-3)',
              }}>
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  color:         m.color,
                  fontWeight:    700,
                }}>
                  {m.priority}
                </span>
                <Badge variant={m.status === 'ACTIVE' ? 'green' : 'default'}>
                  {m.status}
                </Badge>
              </div>

              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-data)',
                fontWeight:    700,
                color:         'var(--ink)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wide)',
                marginBottom:  'var(--space-3)',
              }}>
                {m.model}
              </div>

              <div style={{
                display:       'flex',
                flexDirection: 'column',
                gap:           'var(--space-1)',
              }}>
                {[
                  { k: 'LATENCY', v: m.latency },
                  { k: 'CALLS',   v: m.calls   },
                ].map((row) => (
                  <div
                    key={row.k}
                    style={{
                      display:        'flex',
                      justifyContent: 'space-between',
                    }}
                  >
                    <span style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      color:         'var(--muted)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wide)',
                    }}>
                      {row.k}
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   'var(--fs-nano)',
                      color:      m.status === 'ACTIVE'
                        ? m.color
                        : 'var(--muted)',
                      fontWeight: 700,
                    }}>
                      {row.v}
                    </span>
                  </div>
                ))}
              </div>

              {/* Fallback arrow */}
              {i < 3 && (
                <div style={{
                  marginTop:  'var(--space-3)',
                  textAlign:  'center',
                  fontFamily: 'var(--font-mono)',
                  fontSize:   'var(--fs-nano)',
                  color:      'var(--muted)',
                }}>
                  IF FAIL →
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Responsive */}
      <style>{`
        @media (max-width: 1024px) {
          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
        @media (max-width: 600px) {
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="40px 1fr 80px 60px 60px 120px"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  )
}
