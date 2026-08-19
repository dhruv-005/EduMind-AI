/* ============================================================
   EDUMIND AI — LANDING PAGE
   Neo-Brutalist Hero + Radar + Bento + Stack + Features
   ============================================================ */

import React, { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTheme } from '@hooks/useTheme'
import { useUTCClock } from '@hooks/useUTCClock'
import { useCountUp } from '@hooks/useCountUp'
import { useIntersection } from '@hooks/useIntersection'
import { useSparkline } from '@hooks/useSparkline'
import { useTerminalLogs } from '@hooks/useTerminalLogs'
import { TELEMETRY_STATS } from '@utils/constants'

/* ── TELEMETRY CELL ─────────────────────────────────────────── */
function TelemetryCell({ label, value, delta, index }) {
  const { ref, hasTriggered } = useIntersection({ once: true })
  return (
    <div
      ref={ref}
      className="ribbon__cell"
      style={{
        opacity:   hasTriggered ? 1 : 0,
        transform: hasTriggered ? 'translateY(0)' : 'translateY(12px)',
        transition: `opacity 0.4s ease ${index * 0.1}s,
                     transform 0.4s ease ${index * 0.1}s`,
      }}
    >
      <div className="ribbon__label">{label}</div>
      <div className="ribbon__value" style={{ color: 'var(--accent-primary)' }}>
        {value}
      </div>
      {delta && (
        <div className="ribbon__delta">{delta}</div>
      )}
    </div>
  )
}

/* ── BENTO CARD ─────────────────────────────────────────────── */
function BentoCard({ tag, title, desc, span, children, accent }) {
  const [hovered, setHovered] = useState(false)
  return (
    <div
      className={`bento__card bento__card--${span}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        transform: hovered ? 'translate(-4px,-4px)' : 'translate(0,0)',
        boxShadow: hovered
          ? accent
            ? `10px 10px 0px ${accent}`
            : 'var(--shadow-lg)'
          : accent
            ? `6px 6px 0px ${accent}`
            : 'var(--shadow)',
        borderColor: accent || 'var(--ink)',
        transition:  'transform 0.12s ease, box-shadow 0.12s ease',
      }}
    >
      {tag && (
        <div style={{
          display:       'flex',
          alignItems:    'center',
          gap:           'var(--space-2)',
          marginBottom:  'var(--space-4)',
        }}>
          <span className="bento__tag">{tag}</span>
          {accent && (
            <span style={{
              width:      '6px',
              height:     '6px',
              background: accent,
              borderRadius: '50%',
              animation:  'pulseDot 2s ease-in-out infinite',
              boxShadow:  `0 0 6px ${accent}`,
            }} />
          )}
        </div>
      )}
      <div className="bento__title">{title}</div>
      {desc && (
        <p style={{
          fontSize:   'var(--fs-data)',
          color:      'var(--muted)',
          lineHeight: 1.7,
          marginTop:  'var(--space-3)',
        }}>
          {desc}
        </p>
      )}
      {children}
    </div>
  )
}

/* ── STACK STEP CARD ────────────────────────────────────────── */
function StackCard({ num, title, desc, tag, detail, index }) {
  const { ref, hasTriggered } = useIntersection({ threshold: 0.2 })
  return (
    <div
      ref={ref}
      className="stack__card"
      style={{
        zIndex:     10 + index,
        opacity:    hasTriggered ? 1 : 0,
        transform:  hasTriggered ? 'translateY(0)' : 'translateY(24px)',
        transition: `opacity 0.5s ease ${index * 0.1}s,
                     transform 0.5s ease ${index * 0.1}s`,
      }}
    >
      <div>
        <div className="stack__num">{num}</div>
      </div>
      <div>
        <div style={{
          display:       'flex',
          alignItems:    'center',
          gap:           'var(--space-3)',
          marginBottom:  'var(--space-3)',
        }}>
          <span className="bento__tag">{tag}</span>
        </div>
        <div className="stack__title">{title}</div>
        <p className="stack__desc">{desc}</p>
        {detail && (
          <div style={{
            marginTop:   'var(--space-4)',
            padding:     'var(--space-4)',
            background:  'var(--surface)',
            border:      'var(--border-thin)',
            fontFamily:  'var(--font-mono)',
            fontSize:    'var(--fs-nano)',
            color:       'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
          }}>
            {'>'} {detail}
          </div>
        )}
      </div>
    </div>
  )
}

/* ── MAIN LANDING PAGE ──────────────────────────────────────── */
export default function Landing() {
  const { theme, toggleTheme } = useTheme()
  const { time } = useUTCClock()
  const { logs } = useTerminalLogs(true, 2500)
  const { normalized: sparkData } = useSparkline({
    bars: 24, minVal: 30, maxVal: 100, interval: 1800
  })

  // Radar ref
  const radarRef = useRef(null)

  // Stats counters
  const stat1 = useCountUp({ end: 1247, duration: 2000, trigger: true })
  const stat2 = useCountUp({ end: 94.2, decimals: 1, duration: 2000, trigger: true })
  const stat3 = useCountUp({ end: 8831, duration: 2000, trigger: true })
  const stat4 = useCountUp({ end: 1.4, decimals: 1, duration: 1500, trigger: true })

  return (
    <div style={{
      minHeight:  '100vh',
      background: 'var(--base)',
    }}>

      {/* ════════════════════════════════════════════════
          STANDALONE HEADER (Landing has its own navbar)
          ════════════════════════════════════════════════ */}
      <header style={{
        position:     'fixed',
        top:          0,
        left:         0,
        right:        0,
        height:       'var(--header-h)',
        zIndex:       'var(--z-header)',
        background:   'var(--base)',
        borderBottom: 'var(--border)',
        display:      'flex',
        alignItems:   'center',
        padding:      '0 var(--space-6)',
      }}>
        <div style={{
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'space-between',
          width:          '100%',
        }}>
          {/* Logo */}
          <div style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      '0.9rem',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            display:       'flex',
            alignItems:    'center',
            gap:           'var(--space-2)',
          }}>
            <div style={{
              width:      '28px',
              height:     '28px',
              background: 'var(--accent-primary)',
              border:     'var(--border-thin)',
              display:    'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize:   'var(--fs-nano)',
              color:      '#fff',
              fontWeight: 700,
            }}>
              E
            </div>
            EDUMIND
            <span style={{
              background:    'var(--accent-primary)',
              color:         '#fff',
              fontSize:      'var(--fs-nano)',
              padding:       '0.1rem 0.4rem',
              fontFamily:    'var(--font-mono)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wide)',
              border:        '1px solid var(--ink)',
            }}>
              AI
            </span>
          </div>

          {/* Nav */}
          <nav style={{
            display:    'flex',
            height:     'var(--header-h)',
            alignItems: 'center',
          }}>
            {[
              { label: '01. ENGINE',    path: '/evaluator'   },
              { label: '02. CURRICULUM',path: '/generator'   },
              { label: '03. NEURAL',    path: '/voice-tutor' },
              { label: '04. BENCHMARKS',path: '/dashboard'   },
            ].map((item) => (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  padding:       '0 var(--space-5)',
                  height:        '100%',
                  display:       'flex',
                  alignItems:    'center',
                  borderLeft:    'var(--border-subtle)',
                  color:         'var(--muted)',
                  textDecoration:'none',
                  transition:    'background-color 0.12s, color 0.12s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--accent-primary)'
                  e.currentTarget.style.color = '#fff'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--muted)'
                }}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Right controls */}
          <div style={{
            display:    'flex',
            alignItems: 'center',
            gap:        'var(--space-4)',
          }}>
            {/* Status */}
            <div style={{
              display:    'flex',
              alignItems: 'center',
              gap:        'var(--space-2)',
            }}>
              <span style={{
                width:        '7px',
                height:       '7px',
                borderRadius: '50%',
                background:   'var(--term-green)',
                boxShadow:    '0 0 8px var(--term-green)',
                animation:    'pulseDot 2s ease-in-out infinite',
                display:      'inline-block',
              }} />
              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color:         'var(--term-green)',
              }}>
                CORE ONLINE
              </span>
            </div>

            {/* UTC Clock */}
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              color:         'var(--term-green)',
              letterSpacing: 'var(--ls-wide)',
            }}>
              {time}
            </span>

            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                padding:       '0.35rem 0.8rem',
                background:    'var(--surface)',
                color:         'var(--muted)',
                border:        'var(--border-thin)',
                cursor:        'pointer',
              }}
            >
              {theme === 'dark' ? '[ LIGHT ]' : '[ DARK ]'}
            </button>
          </div>
        </div>
      </header>

      {/* ════════════════════════════════════════════════
          SECTION 01 — HERO / NEURAL RADAR
          ════════════════════════════════════════════════ */}
      <section style={{
        position:   'relative',
        minHeight:  '100vh',
        paddingTop: 'var(--header-h)',
        display:    'grid',
        gridTemplateColumns: '1fr var(--sidebar-w)',
        borderBottom: 'var(--border)',
        overflow:   'hidden',
      }}>

        {/* Main hero content */}
        <div style={{
          padding:  'var(--space-16) var(--space-8) var(--space-12)',
          position: 'relative',
          display:  'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          borderRight: 'var(--border)',
        }}>

          {/* Coordinate grid */}
          <div className="coord-grid" />

          {/* Radar rings */}
          {[300, 600, 900].map((d, i) => (
            <div
              key={d}
              style={{
                position:     'absolute',
                top:          '50%',
                left:         '50%',
                width:        `${d}px`,
                height:       `${d}px`,
                marginLeft:   `-${d / 2}px`,
                marginTop:    `-${d / 2}px`,
                border:       '1px solid var(--border-subtle)',
                borderRadius: '50%',
                pointerEvents:'none',
                opacity:      1 - i * 0.25,
              }}
            />
          ))}

          {/* Radar sweep */}
          <div style={{
            position:        'absolute',
            top:             '50%',
            left:            '50%',
            width:           '450px',
            height:          '2px',
            background:      'linear-gradient(90deg, var(--accent-primary), transparent)',
            transformOrigin: '0 0',
            animation:       'radarSweep 6s linear infinite',
            pointerEvents:   'none',
            opacity:         0.6,
          }} />

          {/* Radar ping dots */}
          {[
            { top: '35%', left: '45%' },
            { top: '55%', left: '60%' },
            { top: '40%', left: '70%' },
          ].map((pos, i) => (
            <div
              key={i}
              style={{
                position:     'absolute',
                ...pos,
                width:        '8px',
                height:       '8px',
                borderRadius: '50%',
                background:   'var(--accent-primary)',
                boxShadow:    '0 0 10px var(--accent-primary)',
                pointerEvents:'none',
                zIndex:       1,
              }}
            >
              <div style={{
                position:     'absolute',
                top:          '50%',
                left:         '50%',
                transform:    'translate(-50%,-50%)',
                width:        '100%',
                height:       '100%',
                borderRadius: '50%',
                border:       '1px solid var(--accent-primary)',
                animation:    `radarPing ${1.5 + i * 0.5}s ease-out infinite`,
              }} />
            </div>
          ))}

          {/* Content */}
          <div style={{ position: 'relative', zIndex: 2 }}>

            {/* Pre-title label */}
            <div style={{
              display:       'flex',
              alignItems:    'center',
              gap:           'var(--space-3)',
              marginBottom:  'var(--space-6)',
            }}>
              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-widest)',
                color:         'var(--accent-primary)',
              }}>
                // EDUMIND NEURAL CORE v2.0
              </span>
              <div style={{
                flex:          1,
                height:        '1px',
                background:    'var(--border-subtle)',
                maxWidth:      '120px',
              }} />
            </div>

            {/* Hero title */}
            <h1 style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      'var(--fs-hero)',
              fontWeight:    700,
              textTransform: 'uppercase',
              lineHeight:    0.88,
              letterSpacing: 'var(--ls-tight)',
              marginBottom:  'var(--space-8)',
              maxWidth:      '900px',
            }}>
              <span style={{ display: 'block' }}>AUTONOMOUS</span>
              <span style={{
                display:    'block',
                color:      'var(--accent-primary)',
                WebkitTextStroke: theme === 'light'
                  ? 'none'
                  : '1px var(--accent-primary)',
              }}>
                KNOWLEDGE
              </span>
              <span style={{ display: 'block' }}>SYNTHESIS</span>
              <span style={{
                display:    'block',
                color:      'var(--accent-cyber)',
              }}>
                ENGINE
              </span>
            </h1>

            {/* Subtitle */}
            <p style={{
              fontFamily: 'var(--font-mono)',
              fontSize:   'var(--fs-body)',
              color:      'var(--muted)',
              maxWidth:   '560px',
              lineHeight: 1.7,
              marginBottom: 'var(--space-10)',
            }}>
              One platform. Five AI powers. Zero cost.
              The most intelligent educational AI that thinks,
              speaks, evaluates, generates, and assists — production ready.
            </p>

            {/* CTA Buttons */}
            <div style={{
              display:   'flex',
              gap:       'var(--space-4)',
              flexWrap:  'wrap',
              marginBottom: 'var(--space-12)',
            }}>
              <Link
                to="/dashboard"
                style={{
                  fontFamily:    'var(--font-mono)',
                  fontWeight:    700,
                  fontSize:      'var(--fs-data)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                  padding:       '1rem 2rem',
                  border:        'var(--border)',
                  background:    'var(--accent-primary)',
                  color:         '#ffffff',
                  boxShadow:     'var(--shadow-accent)',
                  textDecoration:'none',
                  display:       'inline-flex',
                  alignItems:    'center',
                  gap:           'var(--space-2)',
                  transition:    'transform 0.12s ease, box-shadow 0.12s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translate(-3px,-3px)'
                  e.currentTarget.style.boxShadow = '10px 10px 0px var(--accent-primary)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translate(0,0)'
                  e.currentTarget.style.boxShadow = 'var(--shadow-accent)'
                }}
              >
                ▶ LAUNCH LEARNING NODE
              </Link>

              <Link
                to="/evaluator"
                style={{
                  fontFamily:    'var(--font-mono)',
                  fontWeight:    700,
                  fontSize:      'var(--fs-data)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                  padding:       '1rem 2rem',
                  border:        'var(--border)',
                  background:    'transparent',
                  color:         'var(--accent-cyber)',
                  boxShadow:     'var(--shadow-cyber)',
                  borderColor:   'var(--accent-cyber)',
                  textDecoration:'none',
                  display:       'inline-flex',
                  alignItems:    'center',
                  gap:           'var(--space-2)',
                  transition:    'transform 0.12s ease, box-shadow 0.12s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translate(-3px,-3px)'
                  e.currentTarget.style.boxShadow = '10px 10px 0px var(--accent-cyber)'
                  e.currentTarget.style.background = 'var(--accent-cyber)'
                  e.currentTarget.style.color = 'var(--term-bg)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translate(0,0)'
                  e.currentTarget.style.boxShadow = 'var(--shadow-cyber)'
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--accent-cyber)'
                }}
              >
                ◎ VIEW BENCHMARKS
              </Link>
            </div>

            {/* Live stats row */}
            <div style={{
              display:             'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap:                 'var(--space-6)',
              paddingTop:          'var(--space-6)',
              borderTop:           'var(--border-thin)',
            }}>
              {[
                { label: 'EVALUATIONS',   value: stat1.value, suffix: '+' },
                { label: 'ACCURACY',      value: stat2.value, suffix: '%' },
                { label: 'AI CALLS',      value: stat3.value, suffix: ''  },
                { label: 'LATENCY (MS)', value: stat4.value, suffix: ''  },
              ].map((s, i) => (
                <div key={i}>
                  <div style={{
                    fontFamily:    'var(--font-heading)',
                    fontSize:      'var(--fs-h2)',
                    fontWeight:    700,
                    letterSpacing: 'var(--ls-tight)',
                    color:         'var(--ink)',
                    lineHeight:    1,
                  }}>
                    {s.value}{s.suffix}
                  </div>
                  <div style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    color:         'var(--muted)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wider)',
                    marginTop:     'var(--space-1)',
                  }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Terminal sidebar — hero */}
        <div style={{
          background:    'var(--term-bg)',
          display:       'flex',
          flexDirection: 'column',
          overflow:      'hidden',
        }}>

          {/* Terminal header */}
          <div style={{
            padding:      'var(--space-3) var(--space-4)',
            borderBottom: '1px solid rgba(255,255,255,0.08)',
            display:      'flex',
            alignItems:   'center',
            justifyContent: 'space-between',
          }}>
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              color:         'var(--term-green)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
            }}>
              ● NEURAL STREAM ACTIVE
            </span>
            <span style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              color:         'rgba(255,255,255,0.2)',
            }}>
              {time}
            </span>
          </div>

          {/* Log stream */}
          <div style={{
            flex:       1,
            padding:    'var(--space-4)',
            overflowY:  'auto',
            fontFamily: 'var(--font-mono)',
            fontSize:   '0.65rem',
          }}>
            <div style={{
              color:         'var(--term-green)',
              marginBottom:  'var(--space-3)',
              letterSpacing: 'var(--ls-wide)',
            }}>
              {'>'} EDUMIND_CORE --init --stream<span style={{
                animation: 'blink 1s step-end infinite',
              }}>_</span>
            </div>

            {logs.slice(-20).map((log) => {
              const tagColors = {
                SYS:  'var(--accent-cyber)',
                OK:   'var(--term-green)',
                WARN: 'var(--term-amber)',
                ERR:  'var(--term-red)',
              }
              return (
                <div key={log.id} style={{
                  display:       'flex',
                  gap:           'var(--space-2)',
                  marginBottom:  'var(--space-2)',
                  animation:     'fadeInUp 0.2s ease forwards',
                }}>
                  <span style={{ color: 'rgba(255,255,255,0.2)', flexShrink: 0 }}>
                    {log.time}
                  </span>
                  <span style={{
                    color:     tagColors[log.tag] || 'var(--accent-cyber)',
                    flexShrink: 0,
                    minWidth:  '36px',
                  }}>
                    [{log.tag}]
                  </span>
                  <span style={{ color: 'rgba(255,255,255,0.5)', wordBreak: 'break-all' }}>
                    {log.message}
                  </span>
                </div>
              )
            })}
          </div>

          {/* Sparkline at bottom */}
          <div style={{
            padding:      'var(--space-3) var(--space-4)',
            borderTop:    '1px solid rgba(255,255,255,0.08)',
          }}>
            <div style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              color:         'rgba(255,255,255,0.3)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              marginBottom:  'var(--space-2)',
            }}>
              INFERENCE LOAD
            </div>
            <div style={{
              display:    'flex',
              alignItems: 'flex-end',
              gap:        '2px',
              height:     '40px',
            }}>
              {sparkData.map((val, i) => (
                <div
                  key={i}
                  style={{
                    flex:       1,
                    height:     `${Math.max(4, val)}%`,
                    background: 'var(--accent-primary)',
                    opacity:    0.3 + (i / sparkData.length) * 0.7,
                    transition: 'height 0.5s ease',
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════
          TELEMETRY RIBBON
          ════════════════════════════════════════════════ */}
      <div className="ribbon">
        {TELEMETRY_STATS.map((stat, i) => (
          <TelemetryCell
            key={stat.label}
            index={i}
            {...stat}
          />
        ))}
      </div>

      {/* ════════════════════════════════════════════════
          SECTION 02 — BENTO FEATURE MATRIX
          ════════════════════════════════════════════════ */}
      <section style={{
        padding:      'var(--space-6) var(--space-8)',
        borderBottom: 'var(--border)',
      }}>

        {/* Section header */}
        <div style={{
          display:       'flex',
          alignItems:    'center',
          gap:           'var(--space-4)',
          marginBottom:  'var(--space-8)',
          paddingBottom: 'var(--space-6)',
          borderBottom:  'var(--border)',
        }}>
          <div>
            <div style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-widest)',
              color:         'var(--accent-primary)',
              marginBottom:  'var(--space-2)',
            }}>
              // 02. CAPABILITY MATRIX
            </div>
            <h2 style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      'var(--fs-h2)',
              fontWeight:    700,
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-tight)',
              lineHeight:    0.92,
            }}>
              FIVE AI ENGINES.<br />ONE PLATFORM.
            </h2>
          </div>
        </div>

        {/* Bento grid */}
        <div className="bento" style={{ padding: 0 }}>

          {/* Card 01 — Evaluator (wide) */}
          <BentoCard
            span={8}
            tag="CH-01 // AI EVALUATOR"
            title="ADAPTIVE ASSESSMENT ENGINE"
            desc="Multi-layer semantic evaluation with subject-specific rubrics.
                  Scores student answers across correctness, relevance,
                  completeness and clarity. Zero manual grading required."
            accent="var(--accent-primary)"
          >
            {/* Live sparkline */}
            <div style={{ marginTop: 'var(--space-6)' }}>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                color:         'var(--muted)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                marginBottom:  'var(--space-2)',
              }}>
                EVALUATION THROUGHPUT
              </div>
              <div style={{
                display:    'flex',
                alignItems: 'flex-end',
                gap:        '3px',
                height:     '60px',
              }}>
                {sparkData.map((val, i) => (
                  <div
                    key={i}
                    style={{
                      flex:       1,
                      height:     `${Math.max(4, val)}%`,
                      background: 'var(--accent-primary)',
                      opacity:    0.4 + (i / sparkData.length) * 0.6,
                      transition: 'height 0.5s ease',
                    }}
                  />
                ))}
              </div>

              {/* Score breakdown */}
              <div style={{
                display:             'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap:                 'var(--space-4)',
                marginTop:           'var(--space-4)',
              }}>
                {[
                  { label: 'CORRECTNESS', val: '40pt', color: 'var(--term-green)' },
                  { label: 'RELEVANCE',   val: '20pt', color: 'var(--accent-cyber)' },
                  { label: 'COMPLETENESS',val: '25pt', color: 'var(--term-amber)' },
                  { label: 'CLARITY',     val: '15pt', color: 'var(--accent-primary)' },
                ].map((item) => (
                  <div key={item.label}>
                    <div style={{
                      fontFamily:    'var(--font-heading)',
                      fontSize:      'var(--fs-h4)',
                      fontWeight:    700,
                      color:         item.color,
                    }}>
                      {item.val}
                    </div>
                    <div style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      color:         'var(--muted)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wide)',
                    }}>
                      {item.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </BentoCard>

          {/* Card 02 — Generator */}
          <BentoCard
            span={4}
            tag="CH-02 // GENERATOR"
            title="NEURAL QUESTION FORGE"
            desc="Auto-generates exam questions from past papers using LLM
                  pattern analysis with deduplication."
            accent="var(--accent-cyber)"
          >
            <div style={{ marginTop: 'var(--space-5)' }}>
              {['MCQ', 'SHORT ANS', 'LONG ANS', 'NUMERICAL'].map((type, i) => (
                <div key={type} style={{
                  display:        'flex',
                  justifyContent: 'space-between',
                  alignItems:     'center',
                  padding:        'var(--space-2) 0',
                  borderBottom:   '1px solid var(--border-subtle)',
                }}>
                  <span style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                    color:         'var(--muted)',
                  }}>
                    {type}
                  </span>
                  <div style={{
                    width:      `${[65, 45, 30, 55][i]}px`,
                    height:     '4px',
                    background: 'var(--accent-cyber)',
                    opacity:    0.6,
                  }} />
                </div>
              ))}
            </div>
          </BentoCard>

          {/* Card 03 — Spelling */}
          <BentoCard
            span={4}
            tag="CH-03 // SPELL CHECK"
            title="OCR SPELL DETECTION"
            desc="Detects spelling errors in PDFs and images with coordinate-level
                  annotation. Smart filter skips names and technical terms."
            accent="var(--term-amber)"
          >
            <div style={{
              marginTop:   'var(--space-5)',
              padding:     'var(--space-4)',
              background:  'var(--surface)',
              border:      'var(--border-thin)',
              fontFamily:  'var(--font-mono)',
              fontSize:    'var(--fs-nano)',
              color:       'var(--muted)',
            }}>
              <div style={{ color: 'var(--term-amber)', marginBottom: 'var(--space-2)' }}>
                ⚠ DETECTED ERRORS
              </div>
              {[
                { word: 'recieve',    fix: 'receive'   },
                { word: 'occured',    fix: 'occurred'  },
                { word: 'seperately', fix: 'separately'},
              ].map((e) => (
                <div key={e.word} style={{
                  display:        'flex',
                  justifyContent: 'space-between',
                  marginBottom:   'var(--space-1)',
                  textTransform:  'uppercase',
                  letterSpacing:  'var(--ls-wide)',
                }}>
                  <span style={{ color: 'var(--term-red)',   textDecoration: 'line-through' }}>
                    {e.word}
                  </span>
                  <span>→</span>
                  <span style={{ color: 'var(--term-green)' }}>
                    {e.fix}
                  </span>
                </div>
              ))}
            </div>
          </BentoCard>

          {/* Card 04 — Voice Tutor */}
          <BentoCard
            span={4}
            tag="CH-04 // VOICE TUTOR"
            title="24/7 VOICE AI TUTOR"
            desc="Real-time voice conversation with a Socratic AI tutor.
                  VAD-powered speech detection with instant interruption."
            accent="var(--term-green)"
          >
            {/* Waveform animation */}
            <div style={{
              display:     'flex',
              alignItems:  'center',
              gap:         '3px',
              marginTop:   'var(--space-5)',
              height:      '40px',
            }}>
              {Array.from({ length: 16 }).map((_, i) => (
                <div
                  key={i}
                  style={{
                    flex:       1,
                    background: 'var(--term-green)',
                    borderRadius:'1px',
                    animation:  `pulseDot ${0.6 + i * 0.1}s ease-in-out infinite`,
                    height:     `${20 + Math.sin(i) * 15}px`,
                    opacity:    0.7,
                  }}
                />
              ))}
            </div>
            <div style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              color:         'var(--term-green)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              marginTop:     'var(--space-3)',
            }}>
              ● VAD ACTIVE — LISTENING...
            </div>
          </BentoCard>

          {/* Card 05 — Sales */}
          <BentoCard
            span={4}
            tag="CH-05 // SALES AI"
            title="INTELLIGENT SALES ASSISTANT"
            desc="RAG-powered product recommendations with lead scoring,
                  follow-up generation, and zero hallucination guarantee."
            accent="var(--accent-purple)"
          >
            {/* Lead score meter */}
            <div style={{ marginTop: 'var(--space-5)' }}>
              {[
                { tier: 'HOT',  score: 87, color: 'var(--term-red)'   },
                { tier: 'WARM', score: 63, color: 'var(--term-amber)'  },
                { tier: 'COOL', score: 41, color: 'var(--accent-cyber)'},
              ].map((l) => (
                <div key={l.tier} style={{
                  marginBottom: 'var(--space-3)',
                }}>
                  <div style={{
                    display:        'flex',
                    justifyContent: 'space-between',
                    marginBottom:   'var(--space-1)',
                  }}>
                    <span style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wider)',
                      color:         l.color,
                    }}>
                      {l.tier}
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   'var(--fs-nano)',
                      color:      l.color,
                      fontWeight: 700,
                    }}>
                      {l.score}%
                    </span>
                  </div>
                  <div style={{
                    height:     '4px',
                    background: 'var(--surface)',
                    border:     '1px solid var(--border-subtle)',
                  }}>
                    <div style={{
                      height:     '100%',
                      width:      `${l.score}%`,
                      background: l.color,
                      transition: 'width 1s ease',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </BentoCard>
        </div>
      </section>

      {/* ════════════════════════════════════════════════
          SECTION 03 — STICKY PIPELINE STACK
          ════════════════════════════════════════════════ */}
      <section style={{
        borderBottom: 'var(--border)',
        overflow:     'hidden',
      }}>

        {/* Section header */}
        <div style={{
          padding:       'var(--space-12) var(--space-8) var(--space-8)',
          borderBottom:  'var(--border)',
        }}>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color:         'var(--accent-primary)',
            marginBottom:  'var(--space-3)',
          }}>
            // 03. LEARNING PIPELINE
          </div>
          <h2 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h2)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            HOW THE<br />
            <span style={{ color: 'var(--accent-primary)' }}>ENGINE</span> WORKS
          </h2>
        </div>

        {/* Stack cards */}
        <div className="stack-section">
          {[
            {
              num:    '01',
              tag:    'INGESTION',
              title:  'KNOWLEDGE MAPPING & DOCUMENT PARSING',
              desc:   'Upload PDFs, images, or documents. Our OCR and text extraction pipeline processes every word, position, and structure. Vector embeddings are generated and stored in ChromaDB for semantic retrieval.',
              detail: 'OCR_ENGINE: Tesseract + PyMuPDF → Vector store: ChromaDB → Embedding: sentence-transformers',
            },
            {
              num:    '02',
              tag:    'PERSONALIZATION',
              title:  'REAL-TIME ADAPTIVE GUIDANCE SYSTEM',
              desc:   'The LLM analyzes student performance patterns, detects knowledge gaps, and dynamically adjusts difficulty, tone, and teaching style. Every response is pedagogically optimized for maximum retention.',
              detail: 'LLM: Groq LLaMA 3.3-70B → Fallback: Gemini 1.5F → Context window: 128K tokens',
            },
            {
              num:    '03',
              tag:    'INTERACTION',
              title:  'VOICE AI SANDBOX & SOCRATIC ENGINE',
              desc:   'Students speak naturally. Silero VAD detects speech, Whisper transcribes, LLaMA responds, Edge TTS speaks back — all under 500ms total latency. Interruption supported instantly.',
              detail: 'VAD: Silero → STT: Groq Whisper → LLM: LLaMA → TTS: Edge TTS → Latency: <500ms',
            },
            {
              num:    '04',
              tag:    'VERIFICATION',
              title:  'CONTINUOUS KNOWLEDGE ASSESSMENT',
              desc:   'Every answer is evaluated across four dimensions: correctness, relevance, completeness and clarity. The AI provides detailed feedback, identifies missing concepts, and suggests targeted improvements.',
              detail: 'Semantic similarity → Concept extraction → Subject rubric → Score aggregation → Audit log',
            },
          ].map((step, i) => (
            <StackCard key={step.num} index={i} {...step} />
          ))}
        </div>
      </section>

      {/* ════════════════════════════════════════════════
          SECTION 04 — GOVERNANCE
          ════════════════════════════════════════════════ */}
      <section style={{
        padding:      'var(--space-12) var(--space-8)',
        borderBottom: 'var(--border)',
        background:   'var(--surface)',
      }}>
        <div style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-widest)',
          color:         'var(--accent-primary)',
          marginBottom:  'var(--space-3)',
        }}>
          // 04. AI GOVERNANCE
        </div>
        <h2 style={{
          fontFamily:    'var(--font-heading)',
          fontSize:      'var(--fs-h2)',
          fontWeight:    700,
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-tight)',
          lineHeight:    0.92,
          marginBottom:  'var(--space-10)',
        }}>
          7-PILLAR GOVERNANCE<br />
          <span style={{ color: 'var(--accent-cyber)' }}>FRAMEWORK</span>
        </h2>

        <div style={{
          display:             'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap:                 'var(--space-4)',
        }}>
          {[
            { num: '01', label: 'CONTENT SAFETY',    desc: 'Input + output filtering, jailbreak prevention, PII protection',           color: 'var(--accent-primary)' },
            { num: '02', label: 'AUDIT TRAIL',        desc: 'Every AI decision logged with model version, timestamp, and confidence',    color: 'var(--accent-cyber)'   },
            { num: '03', label: 'HUMAN OVERSIGHT',    desc: 'Low-confidence results flagged for teacher review with approval workflow',   color: 'var(--term-green)'     },
            { num: '04', label: 'BIAS DETECTION',     desc: 'Statistical bias reports across demographics, multi-model voting',          color: 'var(--term-amber)'     },
            { num: '05', label: 'RATE LIMITING',      desc: '100 req/hr per IP, burst protection, abuse detection + auto-block',        color: 'var(--accent-primary)' },
            { num: '06', label: 'DATA PRIVACY',       desc: 'Raw data never stored permanently, GDPR-inspired retention policies',       color: 'var(--accent-cyber)'   },
            { num: '07', label: 'MODEL VERSIONING',   desc: 'Groq → Gemini → Together → Ollama fallback chain with full tracking',      color: 'var(--term-green)'     },
          ].map((pillar) => (
            <div
              key={pillar.num}
              style={{
                background:  'var(--base)',
                border:      'var(--border)',
                boxShadow:   'var(--shadow)',
                padding:     'var(--space-6)',
                transition:  'transform 0.12s ease, box-shadow 0.12s ease',
                cursor:      'default',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translate(-3px,-3px)'
                e.currentTarget.style.boxShadow = `6px 6px 0px ${pillar.color}`
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translate(0,0)'
                e.currentTarget.style.boxShadow = 'var(--shadow)'
              }}
            >
              <div style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h2)',
                fontWeight:    700,
                color:         pillar.color,
                letterSpacing: 'var(--ls-tight)',
                lineHeight:    1,
                marginBottom:  'var(--space-3)',
              }}>
                {pillar.num}
              </div>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                fontWeight:    700,
                color:         'var(--ink)',
                marginBottom:  'var(--space-3)',
              }}>
                {pillar.label}
              </div>
              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   'var(--fs-nano)',
                color:      'var(--muted)',
                lineHeight: 1.6,
              }}>
                {pillar.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ════════════════════════════════════════════════
          SECTION 05 — FINAL CTA
          ════════════════════════════════════════════════ */}
      <section style={{
        padding:    'var(--space-20) var(--space-8)',
        textAlign:  'center',
        position:   'relative',
        overflow:   'hidden',
        borderBottom: 'var(--border)',
      }}>
        <div className="coord-grid" />
        <div style={{ position: 'relative', zIndex: 2 }}>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color:         'var(--accent-primary)',
            marginBottom:  'var(--space-4)',
          }}>
            // READY TO DEPLOY
          </div>

          <h2 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-display)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.9,
            marginBottom:  'var(--space-8)',
          }}>
            LAUNCH THE<br />
            <span style={{ color: 'var(--accent-primary)' }}>KNOWLEDGE</span><br />
            ENGINE NOW
          </h2>

          <div style={{
            display:        'flex',
            gap:            'var(--space-4)',
            justifyContent: 'center',
            flexWrap:       'wrap',
          }}>
            <Link
              to="/dashboard"
              style={{
                fontFamily:    'var(--font-mono)',
                fontWeight:    700,
                fontSize:      'var(--fs-body)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wide)',
                padding:       '1.2rem 2.8rem',
                border:        'var(--border)',
                background:    'var(--accent-primary)',
                color:         '#ffffff',
                boxShadow:     'var(--shadow-accent)',
                textDecoration:'none',
                display:       'inline-flex',
                alignItems:    'center',
                gap:           'var(--space-2)',
                transition:    'transform 0.12s ease, box-shadow 0.12s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translate(-4px,-4px)'
                e.currentTarget.style.boxShadow = '12px 12px 0px var(--accent-primary)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translate(0,0)'
                e.currentTarget.style.boxShadow = 'var(--shadow-accent)'
              }}
            >
              ▶ ACCESS PLATFORM
            </Link>

            <Link
              to="/admin/governance"
              style={{
                fontFamily:    'var(--font-mono)',
                fontWeight:    700,
                fontSize:      'var(--fs-body)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wide)',
                padding:       '1.2rem 2.8rem',
                border:        'var(--border)',
                background:    'transparent',
                color:         'var(--ink)',
                boxShadow:     'var(--shadow)',
                textDecoration:'none',
                display:       'inline-flex',
                alignItems:    'center',
                gap:           'var(--space-2)',
                transition:    'transform 0.12s ease, box-shadow 0.12s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translate(-4px,-4px)'
                e.currentTarget.style.boxShadow = 'var(--shadow-lg)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translate(0,0)'
                e.currentTarget.style.boxShadow = 'var(--shadow)'
              }}
            >
              ◈ VIEW GOVERNANCE
            </Link>
          </div>

          {/* Zero cost badge */}
          <div style={{
            marginTop:     'var(--space-8)',
            display:       'flex',
            gap:           'var(--space-4)',
            justifyContent:'center',
            flexWrap:      'wrap',
          }}>
            {[
              '₹0 / MONTH',
              '5 AI ENGINES',
              '7 GOVERNANCE PILLARS',
              'PRODUCTION READY',
            ].map((badge) => (
              <span
                key={badge}
                style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  padding:       '0.35rem 0.8rem',
                  border:        'var(--border-thin)',
                  color:         'var(--muted)',
                  background:    'var(--surface)',
                }}
              >
                {badge}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════
          FOOTER
          ════════════════════════════════════════════════ */}
      <footer style={{
        padding:  'var(--space-6) var(--space-8)',
        display:  'flex',
        alignItems:'center',
        justifyContent:'space-between',
        borderTop: 'var(--border)',
        flexWrap: 'wrap',
        gap:      'var(--space-4)',
      }}>
        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
        }}>
          © 2024 EDUMIND AI — AUTONOMOUS KNOWLEDGE SYNTHESIS ENGINE
        </span>
        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--term-green)',
          letterSpacing: 'var(--ls-wide)',
        }}>
          {time}
        </span>
      </footer>
    </div>
  )
}
