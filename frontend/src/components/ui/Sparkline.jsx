/* ============================================================
   EDUMIND AI — SPARKLINE CHART COMPONENT
   Live animated bar sparkline
   ============================================================ */

import React from 'react'
import { useSparkline } from '@hooks/useSparkline'

export function Sparkline({
  bars     = 20,
  minVal   = 20,
  maxVal   = 100,
  interval = 2000,
  live     = true,
  color    = 'var(--accent-primary)',
  height   = 60,
  style    = {},
}) {
  const { normalized } = useSparkline({ bars, minVal, maxVal, interval, live })

  return (
    <div style={{
      display:    'flex',
      alignItems: 'flex-end',
      gap:        '2px',
      height:     `${height}px`,
      ...style,
    }}>
      {normalized.map((val, i) => (
        <div
          key={i}
          style={{
            flex:       1,
            height:     `${Math.max(4, val)}%`,
            background: color,
            opacity:    0.4 + (i / bars) * 0.6,
            transition: 'height 0.5s ease',
            minWidth:   '2px',
          }}
        />
      ))}
    </div>
  )
}

export function SparklineLine({
  data   = [],
  width  = 120,
  height = 40,
  color  = 'var(--accent-primary)',
  style  = {},
}) {
  if (!data || data.length < 2) return null

  const min   = Math.min(...data)
  const max   = Math.max(...data)
  const range = max - min || 1

  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width
    const y = height - ((v - min) / range) * height
    return `${x},${y}`
  })

  const polyline = points.join(' ')

  return (
    <svg
      width={width}
      height={height}
      style={{ overflow: 'visible', ...style }}
    >
      <polyline
        points={polyline}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {points.length > 0 && (() => {
        const last = points[points.length - 1].split(',')
        return (
          <circle
            cx={last[0]}
            cy={last[1]}
            r="3"
            fill={color}
          />
        )
      })()}
    </svg>
  )
}

export default Sparkline
