/* ============================================================
   EDUMIND AI — TOOLTIP COMPONENT
   ============================================================ */

import React, { useState } from 'react'

export default function Tooltip({
  children,
  content,
  position = 'top',
  style    = {},
}) {
  const [visible, setVisible] = useState(false)

  const positions = {
    top:    { bottom: 'calc(100% + 8px)', left: '50%', transform: 'translateX(-50%)' },
    bottom: { top:    'calc(100% + 8px)', left: '50%', transform: 'translateX(-50%)' },
    left:   { right:  'calc(100% + 8px)', top:  '50%', transform: 'translateY(-50%)' },
    right:  { left:   'calc(100% + 8px)', top:  '50%', transform: 'translateY(-50%)' },
  }

  return (
    <div
      style={{ position: 'relative', display: 'inline-flex', ...style }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}

      {visible && content && (
        <div style={{
          position:      'absolute',
          ...positions[position],
          background:    'var(--term-bg)',
          color:         'var(--term-text)',
          border:        '1px solid var(--term-border)',
          padding:       '0.3rem 0.6rem',
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
          whiteSpace:    'nowrap',
          zIndex:        'var(--z-toast)',
          pointerEvents: 'none',
          boxShadow:     '4px 4px 0px #000',
        }}>
          {content}
        </div>
      )}
    </div>
  )
}
