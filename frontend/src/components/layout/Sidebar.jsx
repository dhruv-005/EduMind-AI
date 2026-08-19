/* ============================================================
   EDUMIND AI — NAV SIDEBAR COMPONENT
   Left navigation panel with challenge links
   ============================================================ */

import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { NAV_ITEMS } from '@utils/constants'

// Icons map (using simple text symbols — no dependency needed)
const ICONS = {
  '/dashboard':        '◈',
  '/evaluator':        '◉',
  '/generator':        '◎',
  '/spelling':         '◍',
  '/voice-tutor':      '◐',
  '/sales':            '◑',
  '/admin':            '▣',
  '/admin/governance': '▤',
  '/admin/audit':      '▥',
}

export default function Sidebar() {
  const location = useLocation()

  const isActive = (path) => {
    if (path === '/dashboard') return location.pathname === path
    return location.pathname.startsWith(path)
  }

  return (
    <aside className="nav-sidebar">

      {/* ── SYSTEM INFO ───────────────────────────────── */}
      <div style={{
        padding: 'var(--space-4)',
        borderBottom: 'var(--border-thin)',
        background: 'var(--surface-elevated)',
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--fs-nano)',
          color: 'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wider)',
          marginBottom: 'var(--space-2)',
        }}>
          SYSTEM v2.0.0
        </div>
        <div style={{
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
            5 ENGINES ACTIVE
          </span>
        </div>
      </div>

      {/* ── NAV SECTIONS ──────────────────────────────── */}
      {NAV_ITEMS.map((section) => (
        <div
          key={section.section}
          className="nav-sidebar__section"
        >
          <div className="nav-sidebar__label">
            {section.section}
          </div>

          {section.items.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-sidebar__item ${
                isActive(item.path) ? 'active' : ''
              }`}
            >
              {/* Number */}
              <span className="nav-sidebar__item-num">
                {item.num}
              </span>

              {/* Icon */}
              <span style={{
                fontSize: '0.85rem',
                opacity: 0.7,
                flexShrink: 0,
              }}>
                {ICONS[item.path] || '◇'}
              </span>

              {/* Label */}
              <span style={{ flex: 1 }}>{item.label}</span>

              {/* Active indicator */}
              {isActive(item.path) && (
                <span style={{
                  width: '6px',
                  height: '6px',
                  background: 'var(--accent-primary)',
                  display: 'block',
                  flexShrink: 0,
                }} />
              )}
            </Link>
          ))}
        </div>
      ))}

      {/* ── BOTTOM INFO ───────────────────────────────── */}
      <div style={{
        marginTop: 'auto',
        padding: 'var(--space-4)',
        borderTop: 'var(--border-thin)',
      }}>
        {/* Governance status */}
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--fs-nano)',
          color: 'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
          marginBottom: 'var(--space-3)',
        }}>
          GOVERNANCE
        </div>

        {[
          { label: 'CONTENT FILTER', status: 'ON' },
          { label: 'AUDIT TRAIL',    status: 'ON' },
          { label: 'RATE LIMIT',     status: 'ON' },
        ].map((item) => (
          <div
            key={item.label}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 'var(--space-2)',
            }}
          >
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
              color: 'var(--term-green)',
              background: 'var(--term-green-dim)',
              padding: '0.1rem 0.4rem',
              border: '1px solid var(--term-green)',
            }}>
              {item.status}
            </span>
          </div>
        ))}

        {/* Version */}
        <div style={{
          marginTop: 'var(--space-4)',
          paddingTop: 'var(--space-3)',
          borderTop: '1px solid var(--border-subtle)',
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--fs-nano)',
          color: 'var(--muted)',
          opacity: 0.5,
        }}>
          EDUMIND AI © 2024
        </div>
      </div>
    </aside>
  )
}
