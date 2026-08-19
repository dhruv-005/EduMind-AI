/* ============================================================
   EDUMIND AI — PAPER UPLOAD PAGE
   Dedicated upload page that redirects to generator
   ============================================================ */

import React from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '@components/ui/Button'

export default function PaperUploadPage() {
  const navigate = useNavigate()

  return (
    <div style={{ padding: 'var(--space-8)' }}>
      <div style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-widest)',
        color:         'var(--accent-cyber)',
        marginBottom:  'var(--space-3)',
      }}>
        // CH-02 — UPLOAD
      </div>
      <h1 style={{
        fontFamily:    'var(--font-heading)',
        fontSize:      'var(--fs-h1)',
        fontWeight:    700,
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-tight)',
        lineHeight:    0.92,
        marginBottom:  'var(--space-8)',
      }}>
        UPLOAD<br />
        <span style={{ color: 'var(--accent-cyber)' }}>PAPERS</span>
      </h1>
      <Button
        variant="cyber"
        size="lg"
        onClick={() => navigate('/generator')}
      >
        ▶ GO TO GENERATOR
      </Button>
    </div>
  )
}
