/* ============================================================
   EDUMIND AI — NAVBAR COMPONENT
   Neo-Brutalist Top Navigation with UTC Clock & Theme Toggle
   ============================================================ */

import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTheme } from '@hooks/useTheme'
import { useUTCClock } from '@hooks/useUTCClock'
import { HEADER_NAV } from '@utils/constants'

export default function Navbar() {
  const { theme, toggleTheme } = useTheme()
  const { time } = useUTCClock()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <>
      <header className="header">
        <div className="header__inner">

          {/* ── LOGO ─────────────────────────────────────── */}
          <Link to="/" className="header__logo" style={{ textDecoration: 'none', color: 'var(--ink)' }}>
            <div className="header__logo-mark">E</div>
            <span>EDUMIND</span>
            <span className="header__badge">AI</span>
          </Link>

          {/* ── DESKTOP NAV ──────────────────────────────── */}
          <nav className="header__nav" style={{ display: 'flex' }}>
            {HEADER_NAV.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`header__nav-link ${
                  location.pathname.startsWith(item.path) ? 'active' : ''
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* ── RIGHT CONTROLS ───────────────────────────── */}
          <div className="header__status">

            {/* Status dot + label */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}>
              <span className="status-dot status-dot--online" />
              <span style={{
                fontSize: 'var(--fs-nano)',
                fontFamily: 'var(--font-mono)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color: 'var(--term-green)',
              }}>
                CORE ONLINE
              </span>
            </div>

            {/* UTC Clock */}
            <span className="header__clock">{time}</span>

            {/* Theme Toggle */}
            <button
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? '[ LIGHT ]' : '[ DARK ]'}
            </button>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              style={{
                display: 'none',
                background: 'none',
                border: 'var(--border-thin)',
                color: 'var(--ink)',
                padding: '0.3rem 0.6rem',
                fontSize: 'var(--fs-data)',
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
              }}
              className="mobile-menu-btn"
              aria-label="Toggle menu"
            >
              {mobileOpen ? '✕' : '☰'}
            </button>
          </div>
        </div>
      </header>

      {/* ── MOBILE DROPDOWN NAV ──────────────────────────── */}
      {mobileOpen && (
        <div style={{
          position: 'fixed',
          top: 'var(--header-h)',
          left: 0,
          right: 0,
          background: 'var(--base)',
          borderBottom: 'var(--border)',
          zIndex: 'var(--z-dropdown)',
          display: 'flex',
          flexDirection: 'column',
        }}>
          {HEADER_NAV.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              style={{
                padding: '1rem 1.5rem',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--fs-data)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                borderBottom: 'var(--border-thin)',
                color: location.pathname.startsWith(item.path)
                  ? 'var(--accent-primary)'
                  : 'var(--ink)',
                textDecoration: 'none',
              }}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}

      {/* Mobile styles injected */}
      <style>{`
        @media (max-width: 768px) {
          .header__nav { display: none !important; }
          .header__status .header__clock { display: none; }
          .mobile-menu-btn { display: flex !important; }
        }
      `}</style>
    </>
  )
}
