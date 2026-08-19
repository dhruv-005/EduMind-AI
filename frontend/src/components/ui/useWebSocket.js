/* ============================================================
   EDUMIND AI — WEBSOCKET HOOK (Voice Tutor)
   ============================================================ */

import { useEffect, useRef, useCallback, useState } from 'react'
import { devLog } from '@utils/helpers'

export const WS_STATUS = {
  CONNECTING:  0,
  OPEN:        1,
  CLOSING:     2,
  CLOSED:      3,
}

export function useWebSocket({
  url,
  onMessage  = null,
  onOpen     = null,
  onClose    = null,
  onError    = null,
  autoConnect = false,
  reconnect   = true,
  reconnectDelay = 3000,
  maxReconnects  = 5,
} = {}) {
  const wsRef            = useRef(null)
  const reconnectCount   = useRef(0)
  const reconnectTimer   = useRef(null)
  const isMountedRef     = useRef(true)

  const [status, setStatus]   = useState(WS_STATUS.CLOSED)
  const [lastMessage, setLastMessage] = useState(null)
  const [error, setError]     = useState(null)

  // Connect
  const connect = useCallback(
    (wsUrl) => {
      const target = wsUrl || url
      if (!target) return

      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close()
      }

      devLog('WS: Connecting to', target)
      setStatus(WS_STATUS.CONNECTING)
      setError(null)

      const ws = new WebSocket(target)
      wsRef.current = ws

      ws.onopen = (event) => {
        if (!isMountedRef.current) return
        devLog('WS: Connected')
        setStatus(WS_STATUS.OPEN)
        reconnectCount.current = 0
        if (onOpen) onOpen(event)
      }

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return
        let data = event.data

        // Try JSON parse
        try {
          data = JSON.parse(event.data)
        } catch {
          // Raw string
        }

        setLastMessage({ data, timestamp: Date.now() })
        if (onMessage) onMessage(data, event)
      }

      ws.onclose = (event) => {
        if (!isMountedRef.current) return
        devLog('WS: Closed', event.code, event.reason)
        setStatus(WS_STATUS.CLOSED)
        wsRef.current = null

        if (onClose) onClose(event)

        // Auto-reconnect logic
        if (
          reconnect &&
          event.code !== 1000 &&
          reconnectCount.current < maxReconnects
        ) {
          reconnectCount.current += 1
          devLog(
            `WS: Reconnecting (${reconnectCount.current}/${maxReconnects})...`
          )
          reconnectTimer.current = setTimeout(
            () => connect(target),
            reconnectDelay
          )
        }
      }

      ws.onerror = (event) => {
        if (!isMountedRef.current) return
        devLog('WS: Error', event)
        setError('WebSocket connection error')
        if (onError) onError(event)
      }
    },
    [url, onMessage, onOpen, onClose, onError, reconnect,
     reconnectDelay, maxReconnects]
  )

  // Disconnect
  const disconnect = useCallback((code = 1000, reason = 'User closed') => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current)
    }
    reconnectCount.current = maxReconnects // prevent reconnect
    if (wsRef.current) {
      wsRef.current.close(code, reason)
      wsRef.current = null
    }
    setStatus(WS_STATUS.CLOSED)
  }, [maxReconnects])

  // Send message
  const send = useCallback((data) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      devLog('WS: Cannot send — not connected')
      return false
    }

    const payload = typeof data === 'string'
      ? data
      : JSON.stringify(data)

    wsRef.current.send(payload)
    return true
  }, [])

  // Send binary (audio)
  const sendBinary = useCallback((buffer) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return false
    }
    wsRef.current.send(buffer)
    return true
  }, [])

  // Auto-connect if enabled
  useEffect(() => {
    if (autoConnect && url) {
      connect(url)
    }
    return () => {
      isMountedRef.current = false
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current) wsRef.current.close(1000)
    }
  }, [autoConnect, url, connect])

  return {
    status,
    lastMessage,
    error,
    isConnected: status === WS_STATUS.OPEN,
    isConnecting: status === WS_STATUS.CONNECTING,
    connect,
    disconnect,
    send,
    sendBinary,
  }
}

export default useWebSocket
