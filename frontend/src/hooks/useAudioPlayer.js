/* ============================================================
   EDUMIND AI — AUDIO PLAYER HOOK
   For TTS playback with instant interruption
   ============================================================ */

import { useState, useRef, useCallback, useEffect } from 'react'
import { base64ToBlob } from '@utils/audioUtils'

export function useAudioPlayer({
  onPlayStart = null,
  onPlayEnd   = null,
  onInterrupt = null,
} = {}) {
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef    = useRef(null)
  const audioUrlRef = useRef(null)

  const clearAudio = useCallback(() => {
    if (audioRef.current) {
      try {
        audioRef.current.pause()
        audioRef.current.src = ''
      } catch (_) {}
      audioRef.current = null
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current)
      audioUrlRef.current = null
    }
    setIsPlaying(false)
  }, [])

  const playBase64 = useCallback(async (base64String, mimeType = 'audio/mpeg') => {
    if (!base64String || typeof base64String !== 'string') return

    clearAudio()

    try {
      const blob = base64ToBlob(base64String, mimeType)
      if (blob.size === 0) return

      const url = URL.createObjectURL(blob)
      audioUrlRef.current = url

      const audio = new Audio(url)
      audioRef.current = audio

      audio.onplay = () => {
        setIsPlaying(true)
        if (onPlayStart) onPlayStart()
      }

      audio.onended = () => {
        clearAudio()
        if (onPlayEnd) onPlayEnd()
      }

      audio.onerror = () => {
        clearAudio()
      }

      await audio.play()
    } catch (err) {
      console.warn('Audio playback error / blocked by autoplay policy:', err)
      clearAudio()
    }
  }, [clearAudio, onPlayStart, onPlayEnd])

  const interrupt = useCallback(() => {
    if (isPlaying) {
      clearAudio()
      if (onInterrupt) onInterrupt()
    }
  }, [isPlaying, clearAudio, onInterrupt])

  useEffect(() => {
    return () => clearAudio()
  }, [clearAudio])

  return {
    isPlaying,
    playBase64,
    interrupt,
    stop: clearAudio,
  }
}

export default useAudioPlayer
