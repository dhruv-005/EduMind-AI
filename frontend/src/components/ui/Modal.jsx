/* ============================================================
   EDUMIND AI — MODAL COMPONENT
   ============================================================ */

import React, { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Button from './Button'

export default function Modal({
  isOpen    = false,
  onClose,
  title     = '',
  children,
  footer    = null,
  size      = 'md',
  closable  = true,
  style     = {},
}) {
  const sizes = {
    sm: '420px',
    md: '640px',
    lg: '860px',
    xl: '1100px',
    full: '95vw',
  }

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => {
      if (e.key === 'Escape' && closable) onClose?.()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, closable, onClose])

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={closable ? onClose : undefined}
            style={{
              position:   'fixed',
              inset:      0,
              background: 'rgba(10, 11, 14, 0.88)',
              zIndex:     'var(--z-modal)',
              display:    'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding:    'var(--space-8)',
            }}
          >
            {/* Modal panel */}
            <motion.div
              initial={{ opacity: 0, y: 16, scale: 0.97 }}
              animate={{ opacity: 1, y: 0,  scale: 1 }}
              exit={{ opacity: 0, y: 8,     scale: 0.98 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: 'var(--base)',
                border:     'var(--border)',
                boxShadow:  'var(--shadow-lg)',
                width:      '100%',
                maxWidth:   sizes[size] || sizes.md,
                maxHeight:  '90vh',
                display:    'flex',
                flexDirection: 'column',
                ...style,
              }}
            >
              {/* Header */}
              {(title || closable) && (
                <div style={{
                  padding:        'var(--space-5) var(--space-6)',
                  borderBottom:   'var(--border)',
                  display:        'flex',
                  alignItems:     'center',
                  justifyContent: 'space-between',
                  flexShrink:     0,
                }}>
                  {title && (
                    <span style={{
                      fontFamily:    'var(--font-heading)',
                      fontSize:      'var(--fs-h4)',
                      fontWeight:    700,
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-tight)',
                    }}>
                      {title}
                    </span>
                  )}

                  {closable && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={onClose}
                      style={{ marginLeft: 'auto' }}
                    >
                      ✕ CLOSE
                    </Button>
                  )}
                </div>
              )}

              {/* Body */}
              <div style={{
                flex:       1,
                overflowY:  'auto',
                padding:    'var(--space-6)',
              }}>
                {children}
              </div>

              {/* Footer */}
              {footer && (
                <div style={{
                  padding:        'var(--space-5) var(--space-6)',
                  borderTop:      'var(--border)',
                  display:        'flex',
                  gap:            'var(--space-4)',
                  justifyContent: 'flex-end',
                  flexShrink:     0,
                }}>
                  {footer}
                </div>
              )}
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
