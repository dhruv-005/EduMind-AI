/* ============================================================
   EDUMIND AI — LEADS PAGE
   View and manage all captured leads
   ============================================================ */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { formatLeadTier, formatRelative } from '@utils/formatters'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'

const DEMO_LEADS = [
  { id: 1, name: 'Customer #001', score: 87, tier: 'HOT',  budget: '₹10,000',  intent: 'Purchase laptop for coding', time: new Date(Date.now() - 300000).toISOString()  },
  { id: 2, name: 'Customer #002', score: 63, tier: 'WARM', budget: '₹5,000',   intent: 'Educational software subscription', time: new Date(Date.now() - 900000).toISOString() },
  { id: 3, name: 'Customer #003', score: 41, tier: 'COOL', budget: '₹2,500',   intent: 'Online course platform', time: new Date(Date.now() - 1800000).toISOString() },
  { id: 4, name: 'Customer #004', score: 18, tier: 'COLD', budget: 'Unknown', intent: 'Just browsing options', time: new Date(Date.now() - 3600000).toISOString() },
  { id: 5, name: 'Customer #005', score: 92, tier: 'HOT',  budget: '₹25,000',  intent: 'Enterprise learning suite', time: new Date(Date.now() - 120000).toISOString()  },
]

const tierColors = {
  HOT:  'var(--term-red)',
  WARM: 'var(--term-amber)',
  COOL: 'var(--accent-cyber)',
  COLD: 'var(--muted)',
}

export default function LeadsPage() {
  const [filter, setFilter] = useState('ALL')

  const filtered = filter === 'ALL'
    ? DEMO_LEADS
    : DEMO_LEADS.filter((l) => l.tier === filter)

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
            color:         'var(--accent-purple)',
            marginBottom:  'var(--space-3)',
          }}>
            // CH-05 — LEAD MANAGEMENT
          </div>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            LEADS<br />
            <span style={{ color: 'var(--accent-purple)' }}>PIPELINE</span>
          </h1>
        </div>

        <Link to="/sales">
          <Button variant="primary"
            style={{ background: 'var(--accent-purple)', borderColor: 'var(--accent-purple)' }}>
            + NEW CHAT
          </Button>
        </Link>
      </div>

      {/* Stats row */}
      <div style={{
        display:             'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap:                 'var(--space-4)',
        marginBottom:        'var(--space-6)',
      }}>
        {[
          { tier: 'HOT',  count: 2, color: 'var(--term-red)'   },
          { tier: 'WARM', count: 1, color: 'var(--term-amber)'  },
          { tier: 'COOL', count: 1, color: 'var(--accent-cyber)'},
          { tier: 'COLD', count: 1, color: 'var(--muted)'       },
        ].map((s) => {
          const info = formatLeadTier(s.tier)
          return (
            <button
              key={s.tier}
              onClick={() => setFilter(filter === s.tier ? 'ALL' : s.tier)}
              style={{
                background:  filter === s.tier
                  ? `color-mix(in srgb, ${s.color} 10%, var(--base))`
                  : 'var(--base)',
                border:      filter === s.tier
                  ? `2px solid ${s.color}`
                  : 'var(--border)',
                boxShadow:   filter === s.tier
                  ? `4px 4px 0px ${s.color}`
                  : 'var(--shadow-sm)',
                padding:     'var(--space-5)',
                cursor:      'pointer',
                textAlign:   'left',
                transition:  'all 0.12s ease',
              }}
            >
              <div style={{
                fontFamily:    'var(--font-heading)',
                fontSize:      'var(--fs-h2)',
                fontWeight:    700,
                letterSpacing: 'var(--ls-tight)',
                color:         s.color,
                lineHeight:    1,
                marginBottom:  'var(--space-1)',
              }}>
                {s.count}
              </div>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color:         s.color,
              }}>
                {info.emoji} {info.label} LEADS
              </div>
            </button>
          )
        })}
      </div>

      {/* Leads table */}
      <div style={{
        background: 'var(--base)',
        border:     'var(--border)',
        boxShadow:  'var(--shadow)',
      }}>
        {/* Table header */}
        <div style={{
          display:             'grid',
          gridTemplateColumns: '60px 1fr 120px 200px 100px 120px 100px',
          gap:                 'var(--space-4)',
          padding:             'var(--space-3) var(--space-5)',
          borderBottom:        'var(--border)',
          background:          'var(--surface)',
        }}>
          {['#', 'CUSTOMER', 'TIER', 'INTENT', 'BUDGET', 'TIME', 'ACTION'].map((h) => (
            <span
              key={h}
              style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color:         'var(--muted)',
              }}
            >
              {h}
            </span>
          ))}
        </div>

        {/* Lead rows */}
        {filtered.map((lead, i) => {
          const info  = formatLeadTier(lead.tier)
          const color = tierColors[lead.tier] || 'var(--muted)'

          return (
            <div
              key={lead.id}
              style={{
                display:             'grid',
                gridTemplateColumns: '60px 1fr 120px 200px 100px 120px 100px',
                gap:                 'var(--space-4)',
                padding:             'var(--space-4) var(--space-5)',
                borderBottom:        i < filtered.length - 1
                  ? 'var(--border-thin)'
                  : 'none',
                alignItems:          'center',
                transition:          'background 0.12s ease',
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background = 'var(--surface)')
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.background = 'transparent')
              }
            >
              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                color:         'var(--muted)',
                textAlign:     'center',
              }}>
                {String(i + 1).padStart(2, '0')}
              </span>

              <div>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-data)',
                  fontWeight:    700,
                  color:         'var(--ink)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                }}>
                  {lead.name}
                </div>
                <div style={{ marginTop: '4px', maxWidth: '200px' }}>
                  <ProgressBar
                    value={lead.score}
                    max={100}
                    color={color}
                    showValue={false}
                    height="3px"
                  />
                </div>
              </div>

              <Badge style={{
                color,
                borderColor: color,
                background:  'transparent',
              }}>
                {info.emoji} {info.label}
              </Badge>

              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                color:         'var(--muted)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wide)',
                overflow:      'hidden',
                textOverflow:  'ellipsis',
                whiteSpace:    'nowrap',
              }}>
                {lead.intent}
              </span>

              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-data)',
                fontWeight:    700,
                color:         'var(--ink)',
              }}>
                {lead.budget}
              </span>

              <span style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                color:         'var(--muted)',
                textTransform: 'uppercase',
              }}>
                {formatRelative(lead.time)}
              </span>

              <Link to="/sales">
                <Button variant="ghost" size="sm">
                  CHAT →
                </Button>
              </Link>
            </div>
          )
        })}
      </div>

      {/* Responsive */}
      <style>{`
        @media (max-width: 900px) {
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          div[style*="60px 1fr 120px 200px 100px 120px 100px"] {
            grid-template-columns: 40px 1fr 80px 80px !important;
          }
        }
      `}</style>
    </div>
  )
}
