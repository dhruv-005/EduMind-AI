/* ============================================================
   EDUMIND AI — DASHBOARD PAGE
   Main overview with all 5 challenge quick-access cards
   ============================================================ */

import React from 'react'
import { Link } from 'react-router-dom'
import { useCountUp } from '@hooks/useCountUp'
import { useIntersection } from '@hooks/useIntersection'
import { useSparkline } from '@hooks/useSparkline'
import { useUTCClock } from '@hooks/useUTCClock'
import Card from '@components/ui/Card'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'
import { Sparkline } from '@components/ui/Sparkline'

/* ── STAT CARD ──────────────────────────────────────────────── */
function StatCard({ label, value, suffix = '', delta, color, index }) {
  const { ref, hasTriggered } = useIntersection({ once: true })
  const { displayValue } = useCountUp({
    end:     parseFloat(value),
    decimals:String(value).includes('.') ? 1 : 0,
    duration:1500,
    trigger: hasTriggered,
    suffix,
  })

  return (
    <div
      ref={ref}
      style={{
        background:  'var(--base)',
        border:      'var(--border)',
        boxShadow:   'var(--shadow)',
        padding:     'var(--space-6)',
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
        color:         color || 'var(--ink)',
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

/* ── ENGINE CARD ────────────────────────────────────────────── */
function EngineCard({ num, label, desc, path, status, color, stats }) {
  const [hovered, setHovered] = React.useState(false)

  return (
    <Link
      to={path}
      style={{ textDecoration: 'none' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div style={{
        background:  'var(--base)',
        border:      `var(--border)`,
        borderLeft:  `4px solid ${color}`,
        boxShadow:   hovered ? `8px 8px 0px ${color}` : 'var(--shadow)',
        padding:     'var(--space-6)',
        height:      '100%',
        transform:   hovered ? 'translate(-3px,-3px)' : 'translate(0,0)',
        transition:  'transform 0.12s ease, box-shadow 0.12s ease',
        cursor:      'pointer',
      }}>

        {/* Header */}
        <div style={{
          display:        'flex',
          justifyContent: 'space-between',
          alignItems:     'flex-start',
          marginBottom:   'var(--space-5)',
        }}>
          <div>
            <div style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              color:         color,
              marginBottom:  'var(--space-2)',
            }}>
              CH-{num}
            </div>
            <div style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      'var(--fs-h4)',
              fontWeight:    700,
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-tight)',
              lineHeight:    1,
            }}>
              {label}
            </div>
          </div>

          <Badge variant="green" dot pulse>
            {status}
          </Badge>
        </div>

        {/* Desc */}
        <p style={{
          fontFamily:   'var(--font-mono)',
          fontSize:     'var(--fs-nano)',
          color:        'var(--muted)',
          lineHeight:   1.6,
          marginBottom: 'var(--space-5)',
        }}>
          {desc}
        </p>

        {/* Stats */}
        {stats && (
          <div style={{
            display:             'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap:                 'var(--space-3)',
            paddingTop:          'var(--space-4)',
            borderTop:           'var(--border-thin)',
          }}>
            {stats.map((s) => (
              <div key={s.label}>
                <div style={{
                  fontFamily:    'var(--font-heading)',
                  fontSize:      'var(--fs-h4)',
                  fontWeight:    700,
                  color:         color,
                  letterSpacing: 'var(--ls-tight)',
                }}>
                  {s.value}
                </div>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--muted)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Arrow */}
        <div style={{
          marginTop:     'var(--space-4)',
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         color,
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wider)',
          display:       'flex',
          alignItems:    'center',
          gap:           'var(--space-2)',
          opacity:       hovered ? 1 : 0.5,
          transition:    'opacity 0.15s ease',
        }}>
          OPEN ENGINE →
        </div>
      </div>
    </Link>
  )
}

/* ── MAIN DASHBOARD ─────────────────────────────────────────── */
export default function Dashboard() {
  const { time } = useUTCClock()

  const ENGINES = [
    {
      num:    '01',
      label:  'AI EVALUATOR',
      desc:   'Multi-layer semantic answer evaluation with subject-specific rubrics and instant feedback generation.',
      path:   '/evaluator',
      status: 'ACTIVE',
      color:  'var(--accent-primary)',
      stats:  [
        { label: 'EVALUATED', value: '1.2K' },
        { label: 'ACCURACY',  value: '94%'  },
        { label: 'AVG SCORE', value: '7.4'  },
      ],
    },
    {
      num:    '02',
      label:  'Q GENERATOR',
      desc:   'Auto-generate exam questions from past papers using LLM pattern analysis with deduplication.',
      path:   '/generator',
      status: 'ACTIVE',
      color:  'var(--accent-cyber)',
      stats:  [
        { label: 'GENERATED', value: '4.8K' },
        { label: 'PAPERS',    value: '132'  },
        { label: 'UNIQUE',    value: '99%'  },
      ],
    },
    {
      num:    '03',
      label:  'SPELL CHECK',
      desc:   'OCR-powered spell detection in PDFs and images with coordinate-level annotation and smart filtering.',
      path:   '/spelling',
      status: 'ACTIVE',
      color:  'var(--term-amber)',
      stats:  [
        { label: 'DOCS',      value: '892'  },
        { label: 'ERRORS',    value: '14K'  },
        { label: 'PRECISION', value: '97%'  },
      ],
    },
    {
      num:    '04',
      label:  'VOICE TUTOR',
      desc:   '24/7 voice AI tutor with VAD, instant interruption, Socratic teaching method and session memory.',
      path:   '/voice-tutor',
      status: 'ACTIVE',
      color:  'var(--term-green)',
      stats:  [
        { label: 'SESSIONS',  value: '2.1K' },
        { label: 'AVG TIME',  value: '18m'  },
        { label: 'LATENCY',   value: '490ms'},
      ],
    },
    {
      num:    '05',
      label:  'SALES AI',
      desc:   'RAG-powered product recommendations with lead scoring, follow-up generation, zero hallucination.',
      path:   '/sales',
      status: 'ACTIVE',
      color:  'var(--accent-purple)',
      stats:  [
        { label: 'LEADS',     value: '341'  },
        { label: 'HOT LEADS', value: '28'   },
        { label: 'CONV RATE', value: '34%'  },
      ],
    },
  ]

  const GOVERNANCE = [
    { label: 'CONTENT FILTER',   status: 'ON',  color: 'var(--term-green)' },
    { label: 'AUDIT TRAIL',      status: 'ON',  color: 'var(--term-green)' },
    { label: 'HUMAN OVERSIGHT',  status: 'ON',  color: 'var(--term-green)' },
    { label: 'BIAS DETECTION',   status: 'ON',  color: 'var(--term-green)' },
    { label: 'RATE LIMITING',    status: 'ON',  color: 'var(--term-green)' },
    { label: 'DATA PRIVACY',     status: 'ON',  color: 'var(--term-green)' },
    { label: 'MODEL VERSIONING', status: 'ON',  color: 'var(--term-green)' },
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
            display:       'flex',
            alignItems:    'center',
            gap:           'var(--space-2)',
          }}>
            // MISSION CONTROL
            <span style={{
              width:        '6px',
              height:       '6px',
              background:   'var(--accent-primary)',
              borderRadius: '50%',
              animation:    'pulseDot 2s ease-in-out infinite',
            }} />
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            EDUMIND<br />
            <span style={{ color: 'var(--accent-primary)' }}>DASHBOARD</span>
          </h1>
        </div>

        <div style={{
          display:    'flex',
          alignItems: 'center',
          gap:        'var(--space-4)',
        }}>
          <Badge variant="green" dot pulse>ALL SYSTEMS ONLINE</Badge>
          <span style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            color:         'var(--term-green)',
            letterSpacing: 'var(--ls-wide)',
          }}>
            {time}
          </span>
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
          { label: 'TOTAL EVALUATIONS', value: 1247,  suffix: '',   delta: '+8% today',   color: 'var(--accent-primary)',  index: 0 },
          { label: 'AI ACCURACY RATE',  value: 94.2,  suffix: '%',  delta: '+2.1% week',  color: 'var(--term-green)',      index: 1 },
          { label: 'ACTIVE SESSIONS',   value: 38,    suffix: '',   delta: 'right now',   color: 'var(--accent-cyber)',    index: 2 },
          { label: 'AVG LATENCY',       value: 1.4,   suffix: 'ms', delta: '-0.2ms week', color: 'var(--term-amber)',      index: 3 },
        ].map((s) => (
          <StatCard key={s.label} {...s} />
        ))}
      </div>

      {/* ── ENGINE GRID ───────────────────────────────── */}
      <div style={{
        marginBottom:   'var(--space-8)',
      }}>
        <div style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-widest)',
          color:         'var(--muted)',
          marginBottom:  'var(--space-5)',
          display:       'flex',
          alignItems:    'center',
          gap:           'var(--space-3)',
        }}>
          <span>// AI ENGINES</span>
          <div style={{ flex: 1, height: '1px', background: 'var(--border-subtle)' }} />
          <span>5 ACTIVE</span>
        </div>

        <div style={{
          display:             'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap:                 'var(--space-4)',
        }}>
          {ENGINES.map((engine) => (
            <EngineCard key={engine.num} {...engine} />
          ))}
        </div>
      </div>

      {/* ── BOTTOM ROW — Governance + Sparkline ───────── */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: '1fr 1fr',
        gap:                 'var(--space-4)',
      }}>

        {/* Governance panel */}
        <div style={{
          background: 'var(--base)',
          border:     'var(--border)',
          boxShadow:  'var(--shadow)',
        }}>
          <div style={{
            padding:      'var(--space-5) var(--space-6)',
            borderBottom: 'var(--border)',
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
              GOVERNANCE STATUS
            </span>
            <Link
              to="/admin/governance"
              style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                color:         'var(--accent-primary)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wide)',
                textDecoration:'none',
              }}
            >
              VIEW ALL →
            </Link>
          </div>

          <div style={{ padding: 'var(--space-5) var(--space-6)' }}>
            {GOVERNANCE.map((g) => (
              <div
                key={g.label}
                style={{
                  display:        'flex',
                  justifyContent: 'space-between',
                  alignItems:     'center',
                  padding:        'var(--space-3) 0',
                  borderBottom:   '1px solid var(--border-subtle)',
                }}
              >
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                  color:         'var(--muted)',
                }}>
                  {g.label}
                </span>
                <Badge variant="green" dot>
                  {g.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Activity chart */}
        <div style={{
          background: 'var(--base)',
          border:     'var(--border)',
          boxShadow:  'var(--shadow)',
        }}>
          <div style={{
            padding:      'var(--space-5) var(--space-6)',
            borderBottom: 'var(--border)',
          }}>
            <span style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      'var(--fs-h4)',
              fontWeight:    700,
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-tight)',
            }}>
              LIVE ACTIVITY
            </span>
          </div>

          <div style={{ padding: 'var(--space-6)' }}>

            {/* Sparklines for each engine */}
            {[
              { label: 'EVALUATOR',   color: 'var(--accent-primary)' },
              { label: 'GENERATOR',   color: 'var(--accent-cyber)'   },
              { label: 'SPELL CHECK', color: 'var(--term-amber)'     },
              { label: 'VOICE TUTOR', color: 'var(--term-green)'     },
              { label: 'SALES AI',    color: 'var(--accent-purple)'  },
            ].map((eng) => (
              <div
                key={eng.label}
                style={{
                  display:        'flex',
                  alignItems:     'center',
                  gap:            'var(--space-4)',
                  marginBottom:   'var(--space-4)',
                }}
              >
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                  color:         'var(--muted)',
                  minWidth:      '80px',
                }}>
                  {eng.label}
                </span>
                <div style={{ flex: 1 }}>
                  <Sparkline
                    bars={20}
                    height={28}
                    color={eng.color}
                    interval={2000 + Math.random() * 1000}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 900px) {
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
        @media (max-width: 600px) {
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  )
}
