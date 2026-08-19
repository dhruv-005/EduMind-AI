/* ============================================================
   EDUMIND AI — UTC CLOCK HOOK
   ============================================================ */

import { useState, useEffect } from 'react'
import { formatUTC } from '@utils/formatters'

export function useUTCClock(interval = 1000) {
  const [time, setTime] = useState(formatUTC())
  const [date, setDate] = useState('')

  useEffect(() => {
    function update() {
      const now = new Date()

      // Time string — HH:MM:SS UTC
      setTime(formatUTC(now))

      // Date string — MON DD YYYY
      setDate(
        now.toLocaleDateString('en-US', {
          weekday: 'short',
          month:   'short',
          day:     'numeric',
          year:    'numeric',
          timeZone: 'UTC',
        }).toUpperCase()
      )
    }

    update()
    const timer = setInterval(update, interval)
    return () => clearInterval(timer)
  }, [interval])

  return { time, date }
}

export default useUTCClock
