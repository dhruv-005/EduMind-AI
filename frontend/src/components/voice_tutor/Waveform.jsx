import React, { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from 'framer-motion'

const BAR_COUNT = 32

export default function Waveform({ active = false, isSpeaking = false, analyser = null, height = 64 }) {
  const shouldReduce = useReducedMotion()
  const frameRef     = useRef(null)
  const [bars, setBars] = useState(Array(BAR_COUNT).fill(0.06))

  useEffect(() => {
    if (!active || shouldReduce) { setBars(Array(BAR_COUNT).fill(0.06)); return }
    let dataArray = null
    if (analyser) { analyser.fftSize = BAR_COUNT * 2; dataArray = new Uint8Array(analyser.frequencyBinCount) }
    const tick = () => {
      if (analyser && dataArray) {
        analyser.getByteFrequencyData(dataArray)
        setBars(Array.from({ length: BAR_COUNT }, (_, i) => Math.max(0.04, dataArray[Math.floor(i * dataArray.length / BAR_COUNT)] / 255)))
      } else {
        setBars(prev => prev.map(v => Math.min(1, Math.max(0.04, v + (Math.random() - 0.5) * 0.3))))
      }
      frameRef.current = requestAnimationFrame(tick)
    }
    frameRef.current = requestAnimationFrame(tick)
    return () => { if (frameRef.current) cancelAnimationFrame(frameRef.current) }
  }, [active, analyser, shouldReduce])

  const barGrad = isSpeaking
    ? 'linear-gradient(180deg, #8b5cf6, #ec4899)'
    : 'linear-gradient(180deg, #6366f1, #06b6d4)'

  return (
    <div aria-hidden="true" style={{ display: 'flex', alignItems: 'center', gap: 3, height, width: '100%', justifyContent: 'center' }}>
      {bars.map((amplitude, i) => {
        const barHeight = Math.round(amplitude * height * 0.88)
        const center    = Math.abs(i - BAR_COUNT / 2) / (BAR_COUNT / 2)
        const scale     = active ? (1 - center * 0.3) : 1
        return (
          <div
            key={i}
            style={{
              width:         3,
              height:        Math.max(3, barHeight * scale),
              minHeight:     3,
              borderRadius:  'var(--radius-full)',
              background:    active ? barGrad : 'var(--border)',
              flexShrink:    0,
              transition:    shouldReduce ? 'none' : 'height 0.06s ease, background 0.3s ease',
              boxShadow:     active ? (isSpeaking ? '0 0 6px rgba(139,92,246,0.4)' : '0 0 6px rgba(99,102,241,0.4)') : 'none',
            }}
          />
        )
      })}
    </div>
  )
}
