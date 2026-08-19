/* ============================================================
   EDUMIND AI — SESSION HISTORY PAGE
   ============================================================ */

import React from 'react'
import { Link } from 'react-router-dom'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'

export default function SessionHistoryPage() {
  return (
    <div style={{ padding: 'var(--space-8)' }}>
      <div style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-widest)',
        color:         'var(--term-green)',
        marginBottom:  'var(--space-3)',
      }}>
        // CH-04 — SESSION LOGS
      </div>
      <div style={{
        display:        'flex',
        alignItems:     'flex-start',
        justifyContent: 'space-between',
        marginBottom:   'var(--space-8)',
        paddingBottom:  'var(--space-6)',
        borderBottom:   'var(--border)',
      }}>
        <h1 style={{
          fontFamily:    'var(--font-heading)',
          fontSize:      'var(--fs-h1)',
          fontWeight:    700,
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-tight)',
          lineHeight:    0.92,
        }}>
          SESSION<br />
          <span style={{ color: 'var(--term-green)' }}>HISTORY</span>
        </h1>
        <Link to="/voice-tutor">
          <Button variant="green" size="sm">
            + NEW SESSION
          </Button>
        </Link>
      </div>

      <div style={{
        padding:    'var(--space-20)',
        textAlign:  'center',
        border:     'var(--border-dashed)',
        background: 'var(--surface)',
      }}>
        <div style={{
          fontFamily:    'var(--font-heading)',
          fontSize:      'var(--fs-h2)',
          fontWeight:    700,
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-tight)',
          color:         'var(--muted)',
          marginBottom:  'var(--space-4)',
        }}>
          NO SESSIONS YET
        </div>
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize:   'var(--fs-data)',
          color:      'var(--muted)',
          marginBottom:'var(--space-6)',
        }}>
          Start a voice session to see your history here
        </p>
        <Link to="/voice-tutor">
          <Button variant="green">
            ▶ START VOICE SESSION
          </Button>
        </Link>
      </div>
    </div>
  )
}
