/* ============================================================
   EDUMIND AI — BREADCRUMB COMPONENT
   ============================================================ */

import React from 'react'
import { Link, useLocation } from 'react-router-dom'

// Map path segments to labels
const SEGMENT_LABELS = {
  dashboard:    'Dashboard',
  evaluator:    'Evaluator',
  generator:    'Generator',
  spelling:     'Spell Check',
  'voice-tutor': 'Voice Tutor',
  sales:        'Sales AI',
  admin:        'Admin',
  governance:   'Governance',
  audit:        'Audit Logs',
  history:      'History',
  upload:       'Upload',
  report:       'Report',
  catalogue:    'Catalogue',
  leads:        'Leads',
}

export default function Breadcrumb() {
  const location = useLocation()

  const segments = location.pathname
    .split('/')
    .filter(Boolean)

  if (segments.length === 0) return null

  const crumbs = [
    { label: 'EDUMIND', path: '/dashboard' },
    ...segments.map((seg, i) => ({
      label: (SEGMENT_LABELS[seg] || seg).toUpperCase(),
      path: '/' + segments.slice(0, i + 1).join('/'),
    })),
  ]

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--space-2)',
      padding: 'var(--space-3) var(--space-8)',
      borderBottom: 'var(--border-thin)',
      background: 'var(--surface)',
    }}>
      {crumbs.map((crumb, i) => {
        const isLast = i === crumbs.length - 1
        return (
          <React.Fragment key={crumb.path}>
            {isLast ? (
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color: 'var(--accent-primary)',
                fontWeight: 700,
              }}>
                {crumb.label}
              </span>
            ) : (
              <Link
                to={crumb.path}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  color: 'var(--muted)',
                  textDecoration: 'none',
                  transition: 'color var(--transition)',
                }}
                onMouseEnter={(e) =>
                  (e.target.style.color = 'var(--ink)')
                }
                onMouseLeave={(e) =>
                  (e.target.style.color = 'var(--muted)')
                }
              >
                {crumb.label}
              </Link>
            )}

            {/* Separator */}
            {!isLast && (
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--fs-nano)',
                color: 'var(--muted)',
                opacity: 0.4,
              }}>
                /
              </span>
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}
