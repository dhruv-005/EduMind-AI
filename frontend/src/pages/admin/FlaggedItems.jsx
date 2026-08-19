import React from 'react'
export default function FlaggedItems() {
  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e293b', margin: '0 0 1.5rem' }}>🚩 Flagged Items</h1>
      <div style={{ background: '#fff', borderRadius: '1rem', padding: '3rem', textAlign: 'center', border: '1px solid #e2e8f0', color: '#94a3b8' }}>
        Items flagged for human review will appear here.
      </div>
    </div>
  )
}
