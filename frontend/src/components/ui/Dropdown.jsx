import React, { useState, useRef, useEffect } from 'react'
import { m, AnimatePresence, useReducedMotion } from 'framer-motion'

export default function Dropdown({ trigger, items = [], align = 'right' }) {
  const [open, setOpen] = useState(false)
  const ref             = useRef(null)
  const shouldReduce    = useReducedMotion()

  useEffect(() => {
    const h = e => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  return (
    <div
      ref={ref}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <div onClick={() => setOpen(!open)}>{trigger}</div>

      <AnimatePresence>
        {open && (
          <m.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.08 }}
            style={{
              position:   'absolute',
              zIndex:     200,
              top:        'calc(100% + 2px)',
              [align === 'right' ? 'right' : 'left']: 0,
              minWidth:   180,
              background: '#ffffff',
              border:     '1px solid #0a0a0a',
              overflow:   'hidden',
            }}
          >
            {/* Top rule */}
            <div style={{ height: 3, background: '#0a0a0a' }} />

            {items.map((item, i) =>
              item.divider ? (
                <div
                  key={i}
                  style={{ height: 1, background: 'rgba(0,0,0,0.1)' }}
                />
              ) : (
                <button
                  key={i}
                  onClick={() => { item.onClick?.(); setOpen(false) }}
                  style={{
                    width:      '100%',
                    display:    'flex',
                    alignItems: 'center',
                    gap:        10,
                    padding:    '10px 16px',
                    background: 'none',
                    border:     'none',
                    cursor:     'pointer',
                    fontFamily: 'var(--font)',
                    fontSize:   13,
                    color:      '#0a0a0a',
                    textAlign:  'left',
                    transition: 'background 0.1s, color 0.1s',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = '#0a0a0a'
                    e.currentTarget.style.color      = '#ffffff'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = 'none'
                    e.currentTarget.style.color      = '#0a0a0a'
                  }}
                >
                  {item.icon && (
                    <item.icon size={13} strokeWidth={1.5} />
                  )}
                  {item.label}
                </button>
              )
            )}
          </m.div>
        )}
      </AnimatePresence>
    </div>
  )
}
