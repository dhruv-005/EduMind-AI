/* ============================================================
   EDUMIND AI — WEBSOCKET HOOK
   ============================================================ */

import { useEffect, useRef, useCallback, useState } from 'react'
import { devLog } from '@utils/helpers'

export const WS_STATUS = {
  CONNECTING: 0,
  OPEN:       1,
  CLOSING:    2,
  CLOSED:     3,
}

export function useWebSocket({
  url            = null,
  onMessage      = null,
  onOpen         = null,
  onClose        = null,
  onError        = null,
  autoConnect    = false,
  reconnect      = true,
  reconnectDelay = 3000,
  maxReconnects  = 3,
} = {}) {
  const wsRef          = useRef(null)
  const reconnectCount = useRef(0)
  const reconnectTimer = useRef(null)
  const isMounted      = useRef(true)
  const currentUrl     = useRef(null)

  const [status,      setStatus]      = useState(WS_STATUS.CLOSED)
  const [lastMessage, setLastMessage] = useState(null)
  const [error,       setError]       = useState(null)

  const connect = useCallback((wsUrl) => {
    const target = wsUrl || url

    if (!target || target.includes('undefined') || target.includes('null')) {
      devLog('WS: Invalid URL — not connecting:', target)
      return
    }

    if (wsRef.current) {
      try { wsRef.current.close() } catch (_) {}
      wsRef.current = null
    }

    currentUrl.current = target
    devLog('WS: Connecting to', target)
    setStatus(WS_STATUS.CONNECTING)
    setError(null)

    let ws
    try {
      ws = new WebSocket(target)
    } catch (err) {
      devLog('WS: Failed to create WebSocket:', err)
      setError('Failed to create WebSocket connection')
      setStatus(WS_STATUS.CLOSED)
      return
    }

    wsRef.current = ws

    ws.onopen = (event) => {
      if (!isMounted.current) return
      devLog('WS: Connected to', target)
      setStatus(WS_STATUS.OPEN)
      reconnectCount.current = 0
      if (onOpen) onOpen(event)
    }

    ws.onmessage = (event) => {
      if (!isMounted.current) return
      let data = event.data
      try { data = JSON.parse(event.data) } catch { }
      setLastMessage({ data, timestamp: Date.now() })
      if (onMessage) onMessage(data, event)
    }

    ws.onclose = (event) => {
      if (!isMounted.current) return
      devLog('WS: Closed', event.code, event.reason)
      setStatus(WS_STATUS.CLOSED)
      wsRef.current = null
      if (onClose) onClose(event)

      if (
        reconnect &&
        event.code !== 1000 &&
        reconnectCount.current < maxReconnects &&
        currentUrl.current
      ) {
        reconnectCount.current += 1
        devLog(`WS: Reconnecting ${reconnectCount.current}/${maxReconnects}...`)
        reconnectTimer.current = setTimeout(
          () => connect(currentUrl.current),
          reconnectDelay
        )
      }
    }

    ws.onerror = (event) => {
      if (!isMounted.current) return
      devLog('WS: Error')
      setError('WebSocket connection error')
      if (onError) onError(event)
    }
  }, [url, onMessage, onOpen, onClose, onError, reconnect, reconnectDelay, maxReconnects])

  const disconnect = useCallback((code = 1000, reason = 'User closed') => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current)
      reconnectTimer.current = null
    }
    reconnectCount.current = maxReconnects
    currentUrl.current     = null

    if (wsRef.current) {
      try { wsRef.current.close(code, reason) } catch (_) {}
      wsRef.current = null
    }
    setStatus(WS_STATUS.CLOSED)
  }, [maxReconnects])

  const send = useCallback((data) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      devLog('WS: Cannot send — not connected')
      return false
    }
    const payload = typeof data === 'string' ? data : JSON.stringify(data)
    try {
      wsRef.current.send(payload)
      return true
    } catch (err) {
      devLog('WS: Send failed:', err)
      return false
    }
  }, [])

  const sendBinary = useCallback((buffer) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return false
    try {
      wsRef.current.send(buffer)
      return true
    } catch { return false }
  }, [])

  useEffect(() => {
    if (autoConnect && url && !url.includes('undefined')) {
      connect(url)
    }
    return () => {
      isMounted.current = false
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current) {
        try { wsRef.current.close(1000) } catch (_) {}
      }
    }
  }, []) // eslint-disable-line

  return {
    status,
    lastMessage,
    error,
    isConnected:  status === WS_STATUS.OPEN,
    isConnecting: status === WS_STATUS.CONNECTING,
    connect,
    disconnect,
    send,
    sendBinary,
  }
}

export default useWebSocket
