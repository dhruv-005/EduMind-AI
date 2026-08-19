/* ============================================================
   EDUMIND AI — SPELLING REPORT PAGE
   Detailed report view with annotation viewer
   ============================================================ */

import React from 'react'
import { Link } from 'react-router-dom'
import { useSpellingStore } from '@store/spellingStore'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'

export default function SpellingReportPage() {
  const { report, reset } = useSpellingStore()

  if (!report) {
    return (
      <div style={{ padding: 'var(--space-8)' }}>
        <div style={{
          padding:     'var(--space-20)',
          textAlign:   'center',
          border:      'var(--border-dashed)',
          background:  'var(--surface)',
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
            NO REPORT AVAILABLE
          </div>
          <Link to="/spelling">
            <Button variant="primary">
              ← BACK TO SPELL CHECK
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  const byPage = report.errors?.reduce((acc, err) => {
    const pg = err.page || 1
    if (!acc[pg]) acc[pg] = []
    acc[pg].push(err)
    return acc
  }, {}) || {}

  return (
    <div style={{ padding: 'var(--space-8)' }}>

      {/* Header */}
      <div style={{
        display:        'flex',
        alignItems:     'flex-start',
        justifyContent: 'space-between',
        marginBottom:   'var(--space-8)',
        paddingBottom:  'var(--space-6)',
        borderBottom:   'var(--border)',
        flexWrap:       'wrap',
        gap:            'var(--space-4)',
      }}>
        <div>
          <div style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-widest)',
            color:         'var(--term-amber)',
            marginBottom:  'var(--space-3)',
          }}>
            // CH-03 — DETAILED REPORT
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            SPELL REPORT
          </h1>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <Link to="/spelling">
            <Button variant="primary" size="sm"
              style={{ background: 'var(--term-amber)', borderColor: 'var(--term-amber)' }}>
              + NEW CHECK
            </Button>
          </Link>
        </div>
      </div>

      {/* Page-by-page breakdown */}
      {Object.entries(byPage).map(([page, errors]) => (
        <div key={page} style={{
          background:   'var(--base)',
          border:       'var(--border)',
          boxShadow:    'var(--shadow)',
          marginBottom: 'var(--space-6)',
        }}>
          <div style={{
            padding:      'var(--space-4) var(--space-6)',
            borderBottom: 'var(--border)',
            background:   'var(--surface)',
            display:      'flex',
            alignItems:   'center',
            gap:          'var(--space-4)',
          }}>
            <span style={{
              fontFamily:    'var(--font-heading)',
              fontSize:      'var(--fs-h4)',
              fontWeight:    700,
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-tight)',
            }}>
              PAGE {page}
            </span>
            <Badge variant="red">
              {errors.length} ERROR{errors.length !== 1 ? 'S' : ''}
            </Badge>
          </div>

          <div style={{ padding: 'var(--space-5)' }}>
            {errors.map((err, i) => (
              <div key={i} style={{
                display:        'flex',
                alignItems:     'center',
                gap:            'var(--space-6)',
                padding:        'var(--space-3) 0',
                borderBottom:   i < errors.length - 1
                  ? 'var(--border-thin)'
                  : 'none',
              }}>
                <span style={{
                  fontFamily:     'var(--font-mono)',
                  fontSize:       'var(--fs-data)',
                  color:          'var(--term-red)',
                  textDecoration: 'line-through',
                  fontWeight:     700,
                  minWidth:       '120px',
                }}>
                  {err.word}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize:   'var(--fs-nano)',
                  color:      'var(--muted)',
                }}>
                  →
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize:   'var(--fs-data)',
                  color:      'var(--term-green)',
                  fontWeight: 700,
                  minWidth:   '120px',
                }}>
                  {err.correction}
                </span>
                <div style={{ flex: 1 }}>
                  <ProgressBar
                    value={(err.confidence || 1) * 100}
                    max={100}
                    color="var(--term-green)"
                    showValue={false}
                    height="3px"
                  />
                </div>
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--muted)',
                  textTransform: 'uppercase',
                }}>
                  {Math.round((err.confidence || 1) * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
