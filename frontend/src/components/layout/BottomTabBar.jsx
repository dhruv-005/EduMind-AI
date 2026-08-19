import React from 'react'
import { NavLink } from 'react-router-dom'
import { FiHome, FiCheckSquare, FiMic, FiShoppingBag, FiGrid } from 'react-icons/fi'

const TABS = [
  { path: '/dashboard',  icon: FiHome,        label: 'Home',    color: '#6366f1' },
  { path: '/evaluator',  icon: FiCheckSquare, label: 'Evaluate',color: '#10b981' },
  { path: '/voice-tutor',icon: FiMic,         label: 'Tutor',   color: '#06b6d4' },
  { path: '/sales',      icon: FiShoppingBag, label: 'Sales',   color: '#ec4899' },
  { path: '/generator',  icon: FiGrid,        label: 'More',    color: '#8b5cf6' },
]

export default function BottomTabBar() {
  return (
    <nav
      className="bottom-tabs hide-desktop"
      aria-label="Mobile navigation"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      {TABS.map(tab => (
        <NavLink
          key={tab.path}
          to={tab.path}
          aria-label={tab.label}
          className={({ isActive }) => `bottom-tab${isActive ? ' active' : ''}`}
          style={({ isActive }) => ({
            color: isActive ? tab.color : 'var(--ink-muted)',
          })}
        >
          {({ isActive }) => (
            <>
              <div style={{ position: 'relative' }}>
                {isActive && (
                  <div style={{
                    position: 'absolute',
                    inset: -4,
                    borderRadius: '50%',
                    background: `${tab.color}20`,
                    filter: 'blur(4px)',
                  }} />
                )}
                <tab.icon
                  size={21}
                  strokeWidth={isActive ? 2.5 : 1.5}
                  style={{ position: 'relative', zIndex: 1, color: isActive ? tab.color : 'var(--ink-muted)' }}
                />
              </div>
              <span style={{ fontSize: 9, fontWeight: isActive ? 700 : 500 }}>
                {tab.label}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  )
}
