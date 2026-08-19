/* ============================================================
   EDUMIND AI — SPARKLINE DATA HOOK
   Generates animated sparkline bar data
   ============================================================ */

import { useState, useEffect, useCallback } from 'react'
import { randomInt } from '@utils/helpers'

export function useSparkline({
  bars      = 20,
  minVal    = 20,
  maxVal    = 100,
  interval  = 2000,
  live      = true,
} = {}) {
  // Generate initial data
  const generateData = useCallback(
    () =>
      Array.from({ length: bars }, () => randomInt(minVal, maxVal)),
    [bars, minVal, maxVal]
  )

  const [data, setData] = useState(generateData)

  useEffect(() => {
    if (!live) return

    const timer = setInterval(() => {
      setData((prev) => {
        // Shift left and add new value
        const next = [...prev.slice(1), randomInt(minVal, maxVal)]
        return next
      })
    }, interval)

    return () => clearInterval(timer)
  }, [live, interval, minVal, maxVal])

  // Normalize to 0-100 range for CSS height %
  const max       = Math.max(...data)
  const min       = Math.min(...data)
  const range     = max - min || 1
  const normalized = data.map(
    (v) => Math.round(((v - min) / range) * 100)
  )

  return { data, normalized }
}

export default useSparkline
