/* ============================================================
   EDUMIND AI — SCORE GAUGE COMPONENT
   SVG circular progress with animated fill
   ============================================================ */

import React, { useEffect, useState } from 'react'
import { getGrade } from '@utils/formatters'

export default function ScoreGauge({
  score     = 0,
  maxScore  = 10,
  size      = 180,
  animated  = true,
  showGrade = true,
  style     = {},
}) {
  const [displayScore, setDisplayScore] = useState(0)

  const normalizedScore = Math.min(maxScore, Math.max(0, score))
  const percent         = (normalizedScore / maxScore) * 100
  const gradeInfo       = getGrade(normalizedScore, maxScore)

  // Animate counter
  useEffect(() => {
    if (!animated) {
      setDisplayScore(normalizedScore)
      return
    }

    let start     = 0
    const end     = normalizedScore
    const duration = 1200
    const step    = 16

    const timer = setInterval(() => {
      start += (end - start) * 0.12
      setDisplayScore(Number(start.toFixed(1)))
      if (Math.abs(start - end) < 0.05) {
        setDisplayScore(end)
        clearInterval(timer)
      }
    }, step)

    return () => clearInterval(timer)
  }, [normalizedScore, animated])

  // SVG circle math
  const strokeWidth = size * 0.072
  const radius      = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percent / 100) * circumference

  // Color based on score
  const scoreColor =
    percent >= 80 ? 'var(--term-green)'
    : percent >= 50 ? 'var(--term-amber)'
    : 'var(--term-red)'

  return (
    <div style={{
      display:        'flex',
      flexDirection:  'column',
      alignItems:     'center',
      gap:            'var(--space-4)',
      ...style,
    }}>

      {/* SVG Gauge */}
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg
          width={size}
          height={size}
          style={{ transform: 'rotate(-90deg)' }}
        >
          {/* Background track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--surface)"
            strokeWidth={strokeWidth}
          />

          {/* Score arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={scoreColor}
            strokeWidth={strokeWidth}
            strokeLinecap="square"
            strokeDasharray={circumference}
            strokeDashoffset={animated ? strokeDashoffset : strokeDashoffset}
            style={{
              transition: animated
                ? 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease'
                : 'none',
            }}
          />
        </svg>

        {/* Center content */}
        <div style={{
          position:       'absolute',
          inset:          0,
          display:        'flex',
          flexDirection:  'column',
          alignItems:     'center',
          justifyContent: 'center',
          gap:            '2px',
        }}>
          {/* Score number */}
          <span style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      `${size * 0.22}px`,
            fontWeight:    700,
            lineHeight:    1,
            color:         scoreColor,
            letterSpacing: 'var(--ls-tight)',
          }}>
            {displayScore.toFixed(1)}
          </span>

          {/* Out of */}
          <span style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      `${size * 0.07}px`,
            color:         'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
          }}>
            / {maxScore}
          </span>
        </div>
      </div>

      {/* Grade badge */}
      {showGrade && gradeInfo && (
        <div style={{
          display:       'flex',
          flexDirection: 'column',
          alignItems:    'center',
          gap:           'var(--space-1)',
        }}>
          <span style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h3)',
            fontWeight:    700,
            color:         scoreColor,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
          }}>
            {gradeInfo.grade}
          </span>
          <span style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            color:         'var(--muted)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wider)',
          }}>
            {gradeInfo.label}
          </span>
        </div>
      )}

      {/* Percent bar */}
      <div style={{
        width:      '100%',
        maxWidth:   `${size}px`,
      }}>
        <div style={{
          height:     '4px',
          background: 'var(--surface)',
          border:     '1px solid var(--border-subtle)',
          overflow:   'hidden',
        }}>
          <div style={{
            height:     '100%',
            width:      `${percent}%`,
            background: scoreColor,
            transition: 'width 1.2s ease',
          }} />
        </div>
        <div style={{
          marginTop:      'var(--space-1)',
          fontFamily:     'var(--font-mono)',
          fontSize:       'var(--fs-nano)',
          color:          'var(--muted)',
          textAlign:      'right',
          textTransform:  'uppercase',
          letterSpacing:  'var(--ls-wide)',
        }}>
          {Math.round(percent)}%
        </div>
      </div>
    </div>
  )
}
