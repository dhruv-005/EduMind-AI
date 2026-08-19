/* ============================================================
   EDUMIND AI — LOGIN PAGE
   ============================================================ */

import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTheme } from '@hooks/useTheme'
import { useUTCClock } from '@hooks/useUTCClock'
import { useAuthStore } from '@store/authStore'
import { useTerminalLogs } from '@hooks/useTerminalLogs'
import Input from '@components/ui/Input'
import Button from '@components/ui/Button'
import toast from 'react-hot-toast'

export default function Login() {
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const { time } = useUTCClock()
  const { login } = useAuthStore()
  const { logs } = useTerminalLogs(true, 2000)

  const [form, setForm] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  const validate = () => {
    const errs = {}
    if (!form.email)    errs.email    = 'Email required'
    if (!form.password) errs.password = 'Password required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      // Demo login — replace with real API call
      await new Promise((r) => setTimeout(r, 1200))
      login(
        { id: '1', email: form.email, name: 'Admin User', role: 'admin' },
        'demo-token-xyz'
      )
      toast.success('[ AUTH ] Access granted')
      navigate('/dashboard')
    } catch {
      toast.error('[ AUTH ERROR ] Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight:           '100vh',
      display:             'grid',
      gridTemplateColumns: '1fr 420px',
      background:          'var(--base)',
    }}>

      {/* ── LEFT — HERO PANEL ──────────────────────────── */}
      <div style={{
        background:    'var(--term-bg)',
        borderRight:   'var(--border)',
        display:       'flex',
        flexDirection: 'column',
        padding:       'var(--space-8)',
        position:      'relative',
        overflow:      'hidden',
      }}>

        {/* Coord grid */}
        <div style={{
          position:       'absolute',
          inset:          0,
          backgroundImage:`linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          pointerEvents:  'none',
        }} />

        {/* Radar rings */}
        {[200, 400, 600].map((d) => (
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
              border:       '1px solid rgba(255,255,255,0.04)',
              borderRadius: '50%',
              pointerEvents:'none',
            }}
          />
        ))}

        {/* Sweep */}
        <div style={{
          position:        'absolute',
          top:             '50%',
          left:            '50%',
          width:           '300px',
          height:          '1px',
          background:      'linear-gradient(90deg, var(--accent-primary), transparent)',
          transformOrigin: '0 0',
          animation:       'radarSweep 8s linear infinite',
          opacity:         0.3,
          pointerEvents:   'none',
        }} />

        {/* Logo */}
        <div style={{
          position: 'relative',
          zIndex:   2,
        }}>
          <Link
            to="/"
            style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      '1rem',
              fontWeight:    700,
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-tight)',
              display:       'inline-flex',
              alignItems:    'center',
              gap:           'var(--space-2)',
              color:         '#fff',
              textDecoration:'none',
            }}
          >
            <div style={{
              width:      '28px',
              height:     '28px',
              background: 'var(--accent-primary)',
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
            }}>
              AI
            </span>
          </Link>
        </div>

        {/* Center content */}
        <div style={{
          flex:           1,
          display:        'flex',
          flexDirection:  'column',
          justifyContent: 'center',
          position:       'relative',
          zIndex:         2,
        }}>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'clamp(2rem, 4vw, 4rem)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.9,
            color:         '#fff',
            marginBottom:  'var(--space-6)',
          }}>
            ACCESS THE<br />
            <span style={{ color: 'var(--accent-primary)' }}>NEURAL</span><br />
            CORE
          </h1>

          <p style={{
            fontFamily:  'var(--font-mono)',
            fontSize:    'var(--fs-data)',
            color:       'rgba(255,255,255,0.4)',
            lineHeight:  1.7,
            maxWidth:    '360px',
            marginBottom:'var(--space-8)',
          }}>
            5 AI engines. Production-grade governance.
            Zero cost deployment. Enter your credentials
            to access the knowledge synthesis platform.
          </p>

          {/* Terminal log */}
          <div style={{
            background:   'rgba(255,255,255,0.03)',
            border:       '1px solid rgba(255,255,255,0.06)',
            padding:      'var(--space-4)',
            maxHeight:    '180px',
            overflowY:    'auto',
          }}>
            {logs.slice(-8).map((log) => (
              <div key={log.id} style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   '0.6rem',
                display:    'flex',
                gap:        'var(--space-2)',
                marginBottom:'var(--space-1)',
              }}>
                <span style={{ color: 'rgba(255,255,255,0.2)' }}>
                  {log.time}
                </span>
                <span style={{
                  color: log.tag === 'OK'
                    ? 'var(--term-green)'
                    : log.tag === 'WARN'
                      ? 'var(--term-amber)'
                      : 'var(--accent-cyber)',
                }}>
                  [{log.tag}]
                </span>
                <span style={{ color: 'rgba(255,255,255,0.4)' }}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom */}
        <div style={{
          position:      'relative',
          zIndex:        2,
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'rgba(255,255,255,0.2)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wider)',
        }}>
          {time} — ALL SYSTEMS OPERATIONAL
        </div>
      </div>

      {/* ── RIGHT — LOGIN FORM ─────────────────────────── */}
      <div style={{
        display:        'flex',
        flexDirection:  'column',
        justifyContent: 'center',
        padding:        'var(--space-10) var(--space-8)',
        borderLeft:     'var(--border)',
      }}>

        {/* Header */}
        <div style={{ marginBottom: 'var(--space-10)' }}>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color:         'var(--accent-primary)',
            marginBottom:  'var(--space-3)',
          }}>
            // AUTH NODE
          </div>
          <h2 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h2)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
            marginBottom:  'var(--space-2)',
          }}>
            SYSTEM<br />LOGIN
          </h2>
          <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-data)',
            color:      'var(--muted)',
          }}>
            Enter credentials to access EduMind AI
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{
          display:       'flex',
          flexDirection: 'column',
          gap:           'var(--space-6)',
        }}>

          <Input
            label="Email Address"
            type="email"
            placeholder="admin@edumind.ai"
            value={form.email}
            onChange={handleChange('email')}
            error={errors.email}
            required
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={form.password}
            onChange={handleChange('password')}
            error={errors.password}
            required
          />

          <Button
            type="submit"
            variant="primary"
            fullWidth
            loading={loading}
            size="lg"
          >
            {loading ? 'AUTHENTICATING...' : '▶ ACCESS PLATFORM'}
          </Button>
        </form>

        {/* Demo note */}
        <div style={{
          marginTop:   'var(--space-8)',
          padding:     'var(--space-4)',
          background:  'var(--surface)',
          border:      'var(--border-thin)',
          borderLeft:  '3px solid var(--term-amber)',
        }}>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            color:         'var(--term-amber)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wider)',
            marginBottom:  'var(--space-2)',
          }}>
            ⚡ DEMO MODE
          </div>
          <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize:   'var(--fs-nano)',
            color:      'var(--muted)',
          }}>
            Any email + password works in demo mode.
            Connect real auth backend via the API.
          </p>
        </div>

        {/* Theme toggle */}
        <div style={{
          marginTop:      'var(--space-8)',
          display:        'flex',
          justifyContent: 'space-between',
          alignItems:     'center',
        }}>
          <Link
            to="/"
            style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              color:         'var(--muted)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wide)',
              textDecoration:'none',
            }}
          >
            ← BACK TO HOME
          </Link>
          <button
            onClick={toggleTheme}
            style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              padding:       '0.3rem 0.7rem',
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

      {/* Mobile styles */}
      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns: 1fr 420px"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="background: var(--term-bg)"] {
            display: none !important;
          }
        }
      `}</style>
    </div>
  )
}
