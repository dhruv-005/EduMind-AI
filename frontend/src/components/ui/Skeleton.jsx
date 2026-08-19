/* ============================================================
   EDUMIND AI — SKELETON LOADER COMPONENT
   ============================================================ */

import React from 'react'

export default function Skeleton({
  width   = '100%',
  height  = '1rem',
  style   = {},
  count   = 1,
  gap     = 'var(--space-3)',
}) {
  const skeletonStyle = {
    width,
    height,
    background: `linear-gradient(
      90deg,
      var(--surface) 25%,
      var(--surface-elevated) 50%,
      var(--surface) 75%
    )`,
    backgroundSize: '200% 100%',
    animation: 'shimmer 1.5s infinite',
    border: 'var(--border-thin)',
    ...style,
  }

  if (count === 1) {
    return <div style={skeletonStyle} />
  }

  return (
    <div style={{
      display:       'flex',
      flexDirection: 'column',
      gap,
    }}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          style={{
            ...skeletonStyle,
            width: i === count - 1 && count > 1 ? '70%' : width,
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  )
}

/* Card skeleton */
export function CardSkeleton() {
  return (
    <div style={{
      border:     'var(--border)',
      padding:    'var(--space-8)',
      background: 'var(--base)',
    }}>
      <Skeleton height="0.65rem" width="30%" style={{ marginBottom: 'var(--space-4)' }} />
      <Skeleton height="1.4rem" width="70%" style={{ marginBottom: 'var(--space-6)' }} />
      <Skeleton count={3} gap="var(--space-2)" style={{ marginBottom: 'var(--space-6)' }} />
      <Skeleton height="2.5rem" width="40%" />
    </div>
  )
}
