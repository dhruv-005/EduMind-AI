/* ============================================================
   EDUMIND AI — TERMINAL SIDEBAR COMPONENT
   Live AI inference log stream + metrics panel
   ============================================================ */

import React, { useState, useRef, useEffect } from 'react'
import { useTerminalLogs } from '@hooks/useTerminalLogs'
import { useUTCClock } from '@hooks/useUTCClock'

// Tag color mapping
const TAG_COLORS = {
  SYS:  'var(--accent-cyber)',
  OK:   'var(--term-green)',
  WARN: 'var(--term-amber)',
  ERR:  'var(--term-red)',
}

// Metric items
const METRICS = [
  { label: 'LATENCY',  getValue: () => `${(Math.random() * 2 + 0.8).toFixed(1)}ms` },
  { label: 'TOKENS',   getValue: () => `${Math.floor(Math.random() * 500 + 100)}/s` },
  { label: 'NODES',    getValue: () => `${Math.floor(Math.random() * 5 + 1)}` },
  { label: 'UPTIME',   getValue: () => '99.9%' },
]

export default function TerminalSidebar() {
  const { logs } = useTerminalLogs(true, 2500)
  const { time } = useUTCClock()
  const logBodyRef = useRef(null)

  const [activeTab, setActiveTab] = useState('LOGS')
  const [metrics, setMetrics]     = useState(
    METRICS.map((m) => ({ ...m, value: m.getValue() }))
  )

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (logBodyRef.current && activeTab === 'LOGS') {
      logBodyRef.current.scrollTop = logBodyRef.current.scrollHeight
    }
  }, [logs, activeTab])

  // Update metrics every 3s
  useEffect(() => {
    const timer = setInterval(() => {
      setMetrics(METRICS.map((m) => ({ ...m, value: m.getValue() })))
    }, 3000)
    return () => clearInterval(timer)
  }, [])

  return (
    <aside className="terminal-sidebar">

      {/* ── HEADER ──────────────────────────────────────── */}
      <div className="terminal-sidebar__header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            width: '6px',
            height: '6px',
            background: 'var(--term-green)',
            borderRadius: '50%',
            animation: 'pulseDot 2s ease-in-out infinite',
            display: 'inline-block',
            boxShadow: '0 0 6px var(--term-green)',
          }} />
          <span className="terminal-sidebar__title">
            NEURAL CORE TERMINAL
          </span>
        </div>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--fs-nano)',
          color: 'rgba(255,255,255,0.25)',
          letterSpacing: 'var(--ls-wide)',
        }}>
          {time}
        </span>
      </div>

      {/* ── TABS ────────────────────────────────────────── */}
      <div className="terminal-sidebar__tabs">
        {['LOGS', 'METRICS', 'INFO'].map((tab) => (
          <button
            key={tab}
            className={`terminal-sidebar__tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ── BODY ────────────────────────────────────────── */}
      <div
        className="terminal-sidebar__body terminal-scroll"
        ref={logBodyRef}
      >

        {/* LOGS TAB */}
        {activeTab === 'LOGS' && (
          <div>
            {/* Prompt line */}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--fs-nano)',
              color: 'var(--term-green)',
              marginBottom: 'var(--space-3)',
              letterSpacing: 'var(--ls-wide)',
            }}>
              {'>'} EDUMIND_CORE --stream-mode active
              <span style={{
                animation: 'blink 1s step-end infinite',
                display: 'inline-block',
                marginLeft: '2px',
              }}>_</span>
            </div>

            {/* Log entries */}
            {logs.map((log) => (
              <div
                key={log.id}
                className="terminal-sidebar__log-line"
                style={{
                  animation: 'fadeInUp 0.2s ease forwards',
                }}
              >
                <span className="terminal-sidebar__log-time">
                  {log.time}
                </span>
                <span
                  className="terminal-sidebar__log-tag"
                  style={{
                    color: TAG_COLORS[log.tag] || 'var(--accent-cyber)',
                    minWidth: '36px',
                  }}
                >
                  [{log.tag}]
                </span>
                <span className="terminal-sidebar__log-text">
                  {log.message}
                </span>
              </div>
            ))}

            {/* Cursor */}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--fs-nano)',
              color: 'var(--term-green)',
              marginTop: 'var(--space-2)',
            }}>
              {'>'}{' '}
              <span style={{
                animation: 'blink 1s step-end infinite',
                display: 'inline-block',
              }}>
                █
              </span>
            </div>
          </div>
        )}

        {/* METRICS TAB */}
        {activeTab === 'METRICS' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>

            {/* Header */}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--fs-nano)',
              color: 'var(--term-green)',
              marginBottom: 'var(--space-2)',
            }}>
              {'>'} SYSTEM_TELEMETRY --realtime
            </div>

            {/* Metric grid */}
            {metrics.map((m) => (
              <div key={m.label} style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
                padding: 'var(--space-3)',
              }}>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--fs-nano)',
                  color: 'rgba(255,255,255,0.3)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  marginBottom: 'var(--space-1)',
                }}>
                  {m.label}
                </div>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--fs-data)',
                  fontWeight: 700,
                  color: 'var(--term-green)',
                }}>
                  {m.value}
                </div>

                {/* Progress bar */}
                <div style={{
                  marginTop: 'var(--space-2)',
                  height: '3px',
                  background: 'rgba(255,255,255,0.06)',
                }}>
                  <div style={{
                    height: '100%',
                    width: `${Math.random() * 60 + 40}%`,
                    background: 'var(--term-green)',
                    transition: 'width 1s ease',
                  }} />
                </div>
              </div>
            ))}

            {/* Model info */}
            <div style={{
              marginTop: 'var(--space-4)',
              padding: 'var(--space-3)',
              border: '1px solid rgba(0, 240, 255, 0.15)',
            }}>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--fs-nano)',
                color: 'var(--accent-cyber)',
                textTransform: 'uppercase',
                marginBottom: 'var(--space-2)',
              }}>
                ACTIVE MODELS
              </div>
              {[
                'LLaMA 3.3-70B   ● PRIMARY',
                'Gemini 1.5F     ● STANDBY',
                'Whisper Large   ● STT',
                'Edge TTS        ● TTS',
              ].map((model) => (
                <div key={model} style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.6rem',
                  color: 'rgba(255,255,255,0.4)',
                  marginBottom: 'var(--space-1)',
                  letterSpacing: 'var(--ls-wide)',
                }}>
                  {model}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* INFO TAB */}
        {activeTab === 'INFO' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>

            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--fs-nano)',
              color: 'var(--term-green)',
            }}>
              {'>'} EDUMIND --info
            </div>

            {/* Info blocks */}
            {[
              {
                title: 'PLATFORM',
                items: [
                  ['VERSION',     'v2.0.0'],
                  ['BUILD',       'PRODUCTION'],
                  ['CHALLENGES',  '5 ACTIVE'],
                  ['GOVERNANCE',  '7 PILLARS'],
                ],
              },
              {
                title: 'STACK',
                items: [
                  ['FRONTEND',  'React + Vite'],
                  ['BACKEND',   'FastAPI'],
                  ['LLM',       'Groq LLaMA'],
                  ['VECTOR DB', 'ChromaDB'],
                  ['CACHE',     'Redis'],
                ],
              },
              {
                title: 'GOVERNANCE',
                items: [
                  ['CONTENT FILTER', 'ACTIVE'],
                  ['AUDIT LOG',      'ACTIVE'],
                  ['BIAS CHECK',     'ACTIVE'],
                  ['RATE LIMIT',     'ACTIVE'],
                  ['PRIVACY GUARD',  'ACTIVE'],
                ],
              },
            ].map((block) => (
              <div key={block.title} style={{
                border: '1px solid rgba(255,255,255,0.06)',
                padding: 'var(--space-3)',
              }}>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--fs-nano)',
                  color: 'var(--accent-cyber)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  marginBottom: 'var(--space-3)',
                  borderBottom: '1px solid rgba(255,255,255,0.06)',
                  paddingBottom: 'var(--space-2)',
                }}>
                  {block.title}
                </div>
                {block.items.map(([key, val]) => (
                  <div key={key} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--space-1)',
                  }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.6rem',
                      color: 'rgba(255,255,255,0.3)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wide)',
                    }}>
                      {key}
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.6rem',
                      color: 'rgba(255,255,255,0.6)',
                      fontWeight: 700,
                    }}>
                      {val}
                    </span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── BOTTOM METRICS BAR ──────────────────────────── */}
      <div className="terminal-sidebar__metrics">
        <div className="terminal-metric">
          <span className="terminal-metric__label">LATENCY</span>
          <span className="terminal-metric__value">1.4ms</span>
        </div>
        <div className="terminal-metric">
          <span className="terminal-metric__label">UPTIME</span>
          <span className="terminal-metric__value">99.9%</span>
        </div>
        <div className="terminal-metric">
          <span className="terminal-metric__label">ERRORS</span>
          <span className="terminal-metric__value" style={{ color: 'var(--term-green)' }}>
            0
          </span>
        </div>
        <div className="terminal-metric">
          <span className="terminal-metric__label">CALLS</span>
          <span className="terminal-metric__value">8.2K</span>
        </div>
      </div>
    </aside>
  )
}
