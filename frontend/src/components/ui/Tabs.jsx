/* ============================================================
   EDUMIND AI — TABS COMPONENT
   ============================================================ */

import React, { useState } from 'react'

export default function Tabs({
  tabs      = [],
  defaultTab = null,
  onChange,
  variant   = 'underline',
  style     = {},
}) {
  const [active, setActive] = useState(
    defaultTab || (tabs[0]?.id ?? tabs[0]?.label)
  )

  const handleChange = (id) => {
    setActive(id)
    if (onChange) onChange(id)
  }

  const activeTab = tabs.find(
    (t) => (t.id ?? t.label) === active
  )

  return (
    <div style={style}>
      {/* Tab List */}
      <div style={{
        display:      'flex',
        borderBottom: variant === 'underline' ? 'var(--border)' : 'none',
        gap:          variant === 'boxed' ? 'var(--space-2)' : 0,
        marginBottom: 'var(--space-6)',
      }}>
        {tabs.map((tab) => {
          const id       = tab.id ?? tab.label
          const isActive = id === active

          if (variant === 'boxed') {
            return (
              <button
                key={id}
                onClick={() => handleChange(id)}
                disabled={tab.disabled}
                style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wider)',
                  padding:       'var(--space-2) var(--space-5)',
                  border:        isActive ? 'var(--border)' : 'var(--border-thin)',
                  background:    isActive ? 'var(--ink)' : 'var(--base)',
                  color:         isActive ? 'var(--base)' : 'var(--muted)',
                  cursor:        tab.disabled ? 'not-allowed' : 'pointer',
                  opacity:       tab.disabled ? 0.4 : 1,
                  boxShadow:     isActive ? 'var(--shadow-sm)' : 'none',
                  transition:    'background-color 0.12s ease, color 0.12s ease',
                  display:       'flex',
                  alignItems:    'center',
                  gap:           'var(--space-2)',
                }}
              >
                {tab.icon && <span>{tab.icon}</span>}
                {tab.label}
                {tab.count !== undefined && (
                  <span style={{
                    background: isActive ? 'var(--accent-primary)' : 'var(--surface)',
                    color:      isActive ? '#fff' : 'var(--muted)',
                    padding:    '0 0.3rem',
                    fontSize:   'var(--fs-nano)',
                    border:     '1px solid currentColor',
                    marginLeft: '4px',
                  }}>
                    {tab.count}
                  </span>
                )}
              </button>
            )
          }

          // Underline variant (default)
          return (
            <button
              key={id}
              onClick={() => handleChange(id)}
              disabled={tab.disabled}
              style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                padding:       'var(--space-3) var(--space-6)',
                border:        'none',
                borderBottom:  isActive
                  ? '3px solid var(--accent-primary)'
                  : '3px solid transparent',
                background:    'none',
                color:         isActive ? 'var(--accent-primary)' : 'var(--muted)',
                cursor:        tab.disabled ? 'not-allowed' : 'pointer',
                opacity:       tab.disabled ? 0.4 : 1,
                marginBottom:  '-3px',
                transition:    'color 0.12s ease, border-color 0.12s ease',
                display:       'flex',
                alignItems:    'center',
                gap:           'var(--space-2)',
              }}
            >
              {tab.icon && <span>{tab.icon}</span>}
              {tab.label}
              {tab.count !== undefined && (
                <span style={{
                  background: isActive ? 'var(--accent-primary)' : 'var(--surface)',
                  color:      isActive ? '#fff' : 'var(--muted)',
                  padding:    '0 0.3rem',
                  fontSize:   'var(--fs-nano)',
                  border:     '1px solid currentColor',
                }}>
                  {tab.count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      {activeTab?.content && (
        <div>{activeTab.content}</div>
      )}
    </div>
  )
}
