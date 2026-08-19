/* ============================================================
   EDUMIND AI — COUNT UP ANIMATION HOOK
   For telemetry stats and score reveals
   ============================================================ */

import { useState, useEffect, useRef } from 'react'

export function useCountUp({
  end,
  start      = 0,
  duration   = 1500,
  decimals   = 0,
  prefix     = '',
  suffix     = '',
  trigger    = true,
} = {}) {
  const [value, setValue]       = useState(start)
  const [isRunning, setIsRunning] = useState(false)
  const frameRef = useRef(null)
  const startRef = useRef(null)

  useEffect(() => {
    if (!trigger || end === undefined || end === null) return

    setIsRunning(true)
    startRef.current = null

    const startVal = Number(start)
    const endVal   = Number(end)
    const range    = endVal - startVal

    const step = (timestamp) => {
      if (!startRef.current) startRef.current = timestamp

      const elapsed  = timestamp - startRef.current
      const progress = Math.min(elapsed / duration, 1)

      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = startVal + range * eased

      setValue(Number(current.toFixed(decimals)))

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(step)
      } else {
        setValue(Number(endVal.toFixed(decimals)))
        setIsRunning(false)
      }
    }

    frameRef.current = requestAnimationFrame(step)

    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current)
    }
  }, [end, start, duration, decimals, trigger])

  const displayValue = `${prefix}${value}${suffix}`

  return { value, displayValue, isRunning }
}

export default useCountUp
