import React from 'react'
import Badge from '@components/ui/Badge'
import { formatDateTime, formatProcessingTime } from '@utils/formatters'
import { TableSkeleton } from '@components/ui/Skeleton'

const CH_GRAD = {
  challenge1: 'linear-gradient(135deg,#10b981,#06b6d4)',
  challenge2: 'linear-gradient(135deg,#8b5cf6,#ec4899)',
  challenge3: 'linear-gradient(135deg,#f59e0b,#f43f5e)',
  challenge4: 'linear-gradient(135deg,#06b6d4,#6366f1)',
  challenge5: 'linear-gradient(135deg,#ec4899,#8b5cf6)',
}

const STATUS_VARIANT = { passed:'emerald', flagged:'amber', blocked:'rose' }

export default function AuditLogTable({ logs, isLoading }) {
  if (isLoading) return <TableSkeleton rows={5} />

  if (!logs || logs.length === 0) {
    return (
      <div style={{ padding: '48px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 40, marginBottom: 12 }}>📋</div>
        <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 14, fontWeight: 600, color: 'var(--ink-muted)', fontStyle: 'italic', margin: 0 }}>
          No audit logs found
        </p>
      </div>
    )
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13 }}>
        <thead>
          <tr>
            {['Time','Challenge','Model','Confidence','Status','Time(ms)'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '12px 16px', fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 11, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--ink-muted)', borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap', background: 'var(--bg-secondary)' }}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => (
            <tr key={log.id || i}
              style={{ transition: 'background 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(99,102,241,0.04)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <td data-label="Time" style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', color: 'var(--ink-muted)', whiteSpace: 'nowrap', fontFamily: 'Inter, sans-serif', fontSize: 12 }}>
                {formatDateTime(log.timestamp)}
              </td>
              <td data-label="Challenge" style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
                <span style={{
                  display: 'inline-flex', alignItems: 'center',
                  padding: '3px 10px', borderRadius: 'var(--radius-full)',
                  background: CH_GRAD[log.challenge] || 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                  color: '#ffffff',
                  fontFamily: '"Plus Jakarta Sans", sans-serif',
                  fontSize: 10, fontWeight: 800,
                  boxShadow: '0 2px 8px rgba(99,102,241,0.3)',
                }}>
                  {log.challenge?.replace('challenge','Ch')}
                </span>
              </td>
              <td data-label="Model" style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', color: 'var(--ink-muted)', maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: 'Inter, sans-serif', fontSize: 12 }}>
                {log.model_used}
              </td>
              <td data-label="Confidence" style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
                <span style={{
                  fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 800,
                  background: log.confidence_score >= 0.8 ? 'linear-gradient(135deg,#10b981,#06b6d4)' : log.confidence_score >= 0.6 ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'linear-gradient(135deg,#f43f5e,#ec4899)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                  letterSpacing: '-0.02em',
                }}>
                  {log.confidence_score ? `${Math.round(log.confidence_score * 100)}%` : '—'}
                </span>
              </td>
              <td data-label="Status" style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
                <Badge variant={STATUS_VARIANT[log.governance_status] || 'gray'} size="sm" dot>
                  {log.governance_status}
                </Badge>
              </td>
              <td data-label="Time(ms)" style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', color: 'var(--ink-muted)', fontFamily: 'Inter, sans-serif', fontSize: 12 }}>
                {formatProcessingTime(log.processing_time_ms)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
