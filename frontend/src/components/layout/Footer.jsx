/* ============================================================
   EDUMIND AI — FOOTER COMPONENT
   Full brand breakdown with system specs
   ============================================================ */

import React from 'react'
import { Link } from 'react-router-dom'
import { useUTCClock } from '@hooks/useUTCClock'
import { APP_VERSION } from '@utils/constants'

const FOOTER_LINKS = {
  ENGINES: [
    { label: 'AI Evaluator',    path: '/evaluator'   },
    { label: 'Q Generator',     path: '/generator'   },
    { label: 'Spell Check',     path: '/spelling'    },
    { label: 'Voice Tutor',     path: '/voice-tutor' },
    { label: 'Sales AI',        path: '/sales'       },
  ],
  GOVERNANCE: [
    { label: 'Content Policy',  path: '/admin/governance' },
    { label: 'Audit Logs',      path: '/admin/audit'      },
    { label: 'Admin Panel',     path: '/admin'            },
  ],
  SYSTEM: [
    { label: 'Dashboard',  path: '/dashboard' },
    { label: 'Login',      path: '/login'     },
  ],
}

const TECH_STACK = [
  { label: 'FRONTEND',  value: 'React 18 + Vite'     },
  { label: 'BACKEND',   value: 'FastAPI + Python'     },
  { label: 'LLM',       value: 'Groq LLaMA 3.3-70B'  },
  { label: 'STT',       value: 'Groq Whisper'         },
  { label: 'TTS',       value: 'Edge TTS'             },
  { label: 'VECTOR DB', value: 'ChromaDB'             },
  { label: 'CACHE',     value: 'Redis'                },
  { label: 'DATABASE',  value: 'Supabase'             },
]

export default function Footer() {
  const { time, date } = useUTCClock()

  return (
    <footer style={{
      borderTop: 'var(--border)',
      background: 'var(--surface)',
      marginTop: 'auto',
    }}>

      {/* ── MARQUEE TICKER ────────────────────────────── */}
      <div className="marquee-track">
        <div className="marquee-inner">
          {[...Array(2)].map((_, i) => (
            <React.Fragment key={i}>
              {[
                'AUTONOMOUS KNOWLEDGE SYNTHESIS',
                'AI EVALUATOR ENGINE ACTIVE',
                'QUESTION GENERATOR READY',
                'SPELL DETECTION ONLINE',
                'VOICE TUTOR CONNECTED',
                'SALES AI OPERATIONAL',
                'GOVERNANCE PILLARS ACTIVE',
                'ZERO HALLUCINATION GUARANTEED',
              ].map((text) => (
                <span key={text} className="marquee-item">
                  {text}
                </span>
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* ── MAIN FOOTER CONTENT ───────────────────────── */}
      <div style={{
        padding: 'var(--space-12) var(--space-8)',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--space-8)',
        borderBottom: 'var(--border)',
      }}>

        {/* Brand column */}
        <div>
          <div style={{
            fontFamily: 'var(--font-heading)',
            fontSize: 'var(--fs-h3)',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            marginBottom: 'var(--space-2)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
          }}>
            <span style={{
              background: 'var(--accent-primary)',
              color: '#fff',
              padding: '0.1rem 0.4rem',
              fontSize: 'var(--fs-nano)',
              fontFamily: 'var(--font-mono)',
            }}>
              E
            </span>
            EDUMIND
          </div>

          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--fs-nano)',
            color: 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
            marginBottom: 'var(--space-4)',
          }}>
            AUTONOMOUS KNOWLEDGE SYNTHESIS ENGINE
          </div>

          <p style={{
            fontSize: 'var(--fs-data)',
            color: 'var(--muted)',
            lineHeight: 1.7,
            maxWidth: '260px',
          }}>
            One platform, five AI powers, zero cost.
            The most intelligent educational and sales
            AI system built for production.
          </p>

          {/* Status */}
          <div style={{
            marginTop: 'var(--space-6)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
          }}>
            <span className="status-dot status-dot--online" />
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--fs-nano)',
              color: 'var(--term-green)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wide)',
            }}>
              ALL SYSTEMS OPERATIONAL
            </span>
          </div>
        </div>

        {/* Nav columns */}
        {Object.entries(FOOTER_LINKS).map(([section, links]) => (
          <div key={section}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-widest)',
              color: 'var(--muted)',
              marginBottom: 'var(--space-4)',
              paddingBottom: 'var(--space-3)',
              borderBottom: 'var(--border-thin)',
            }}>
              {section}
            </div>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-2)',
            }}>
              {links.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 'var(--fs-data)',
                    color: 'var(--muted)',
                    textDecoration: 'none',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                    transition: 'color var(--transition)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.color = 'var(--accent-primary)')
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.color = 'var(--muted)')
                  }
                >
                  <span style={{ color: 'var(--accent-primary)', opacity: 0.5 }}>
                    →
                  </span>
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        ))}

        {/* Tech stack column */}
        <div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color: 'var(--muted)',
            marginBottom: 'var(--space-4)',
            paddingBottom: 'var(--space-3)',
            borderBottom: 'var(--border-thin)',
          }}>
            ARCHITECTURE
          </div>

          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-2)',
          }}>
            {TECH_STACK.map((item) => (
              <div key={item.label} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--fs-nano)',
                  color: 'var(--muted)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                }}>
                  {item.label}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--fs-nano)',
                  color: 'var(--ink)',
                  fontWeight: 700,
                }}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── BOTTOM BAR ────────────────────────────────── */}
      <div style={{
        padding: 'var(--space-4) var(--space-8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-4)',
      }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--fs-nano)',
          color: 'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
        }}>
          © 2024 EDUMIND AI — ALL RIGHTS RESERVED
        </span>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-6)',
        }}>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--fs-nano)',
            color: 'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
          }}>
            BUILD {APP_VERSION}
          </span>

          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--fs-nano)',
            color: 'var(--term-green)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
          }}>
            {time}
          </span>
        </div>
      </div>
    </footer>
  )
}
