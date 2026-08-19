import React from 'react'
import { useNavigate } from 'react-router-dom'
export default function BatchEvaluatorPage() {
  const navigate = useNavigate()
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center', paddingTop: '3rem' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e293b', margin: '0 0 0.75rem' }}>Batch Evaluator</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Evaluate multiple student answers at once.</p>
      <button onClick={() => navigate('/evaluator')} style={{ padding: '0.75rem 2rem', borderRadius: '0.75rem', border: 'none', background: '#6366f1', color: '#fff', fontWeight: 700, cursor: 'pointer', fontSize: '0.9rem' }}>
        ← Back to Evaluator
      </button>
    </div>
  )
}
