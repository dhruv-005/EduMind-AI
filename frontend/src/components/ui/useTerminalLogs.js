/* ============================================================
   EDUMIND AI — TERMINAL LOGS HOOK
   Live AI stream log simulator
   ============================================================ */

import { useState, useEffect, useRef, useCallback } from 'react'
import { LOG_MESSAGES } from '@utils/constants'
import { randomInt } from '@utils/helpers'

const MAX_LOGS = 40

export function useTerminalLogs(
  active = true,
  intervalMs = 2500
) {
  const [logs, setLogs] = useState([])
  const timerRef = useRef(null)
  const counterRef = useRef(0)

  // Generate a single log entry
  const generateLog = useCallback(() => {
    const source = LOG_MESSAGES[randomInt(0, LOG_MESSAGES.length - 1)]
    return {
      id:        Date.now() + Math.random(),
      time:      new Date().toISOString().substring(11, 19),
      tag:       source.tag,
      message:   source.msg,
      index:     counterRef.current++,
    }
  }, [])

  // Add a log entry
  const addLog = useCallback((log) => {
    setLogs((prev) => {
      const next = [...prev, log]
      // Keep only last MAX_LOGS entries
      return next.length > MAX_LOGS
        ? next.slice(next.length - MAX_LOGS)
        : next
    })
  }, [])

  // Push a custom log entry from outside
  const pushLog = useCallback(
    (message, tag = 'SYS') => {
      addLog({
        id:      Date.now() + Math.random(),
        time:    new Date().toISOString().substring(11, 19),
        tag,
        message,
        index:   counterRef.current++,
      })
    },
    [addLog]
  )

  // Clear all logs
  const clearLogs = useCallback(() => {
    setLogs([])
    counterRef.current = 0
  }, [])

  // Auto-generate logs on interval
  useEffect(() => {
    if (!active) {
      if (timerRef.current) clearInterval(timerRef.current)
      return
    }

    // Seed with a few initial logs
    const initial = Array.from({ length: 5 }, generateLog)
    setLogs(initial)

    timerRef.current = setInterval(() => {
      addLog(generateLog())
    }, intervalMs)

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [active, intervalMs, generateLog, addLog])

  return { logs, pushLog, clearLogs }
}

export default useTerminalLogs
