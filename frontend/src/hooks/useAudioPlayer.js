/* ============================================================
   EDUMIND AI — AUDIO PLAYER HOOK
   For TTS response playback with interruption support
   ============================================================ */

import { useState, useRef, useCallback, useEffect } from 'react'
import { base64ToBlob } from '@utils/audioUtils'
import { devLog } from '@utils/helpers'

export function useAudioPlayer({
  onPlayStart    = null,
  onPlayEnd      = null,
  onInterrupt    = null,
} = {}) {
  const [isPlaying, setIsPlaying]   = useState(false)
  const [duration, setDuration]     = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const [error, setError]           = useState(null)

  const audioRef      = useRef(null)
  const audioUrlRef   = useRef(null)
  const timeTimerRef  = useRef(null)

  // Clear current audio
  const clearAudio = useCallback(() => {
    if (timeTimerRef.current) {
      clearInterval(timeTimerRef.current)
      timeTimerRef.current = null
    }

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ''
      audioRef.current = null
    }

    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current)
      audioUrlRef.current = null
    }

    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
  }, [])

  // Play from base64 string
  const playBase64 = useCallback(
    async (base64, mimeType = 'audio/mpeg') => {
      setError(null)

      // Stop any current playback
      clearAudio()

      try {
        const blob = base64ToBlob(base64, mimeType)
        const url  = URL.createObjectURL(blob)
        audioUrlRef.current = url

        const audio = new Audio(url)
        audioRef.current = audio

        // Events
        audio.onloadedmetadata = () => {
          setDuration(audio.duration)
        }

        audio.onplay = () => {
          devLog('Audio: Playing')
          setIsPlaying(true)
          if (onPlayStart) onPlayStart()

          // Track current time
          timeTimerRef.current = setInterval(() => {
            setCurrentTime(audio.currentTime)
          }, 200)
        }

        audio.onended = () => {
          devLog('Audio: Ended')
          clearAudio()
          if (onPlayEnd) onPlayEnd()
        }

        audio.onerror = (e) => {
          devLog('Audio: Error', e)
          setError('Audio playback error')
          clearAudio()
        }

        await audio.play()
      } catch (err) {
        setError(err.message || 'Playback failed')
        clearAudio()
      }
    },
    [clearAudio, onPlayStart, onPlayEnd]
  )

  // Play from URL
  const playUrl = useCallback(
    async (url) => {
      setError(null)
      clearAudio()

      try {
        const audio = new Audio(url)
        audioRef.current = audio

        audio.onloadedmetadata = () => setDuration(audio.duration)

        audio.onplay = () => {
          setIsPlaying(true)
          if (onPlayStart) onPlayStart()
          timeTimerRef.current = setInterval(() => {
            setCurrentTime(audio.currentTime)
          }, 200)
        }

        audio.onended = () => {
          clearAudio()
          if (onPlayEnd) onPlayEnd()
        }

        audio.onerror = () => {
          setError('Audio playback error')
          clearAudio()
        }

        await audio.play()
      } catch (err) {
        setError(err.message)
        clearAudio()
      }
    },
    [clearAudio, onPlayStart, onPlayEnd]
  )

  // Interrupt playback immediately
  const interrupt = useCallback(() => {
    if (isPlaying) {
      devLog('Audio: Interrupted by user')
      clearAudio()
      if (onInterrupt) onInterrupt()
    }
  }, [isPlaying, clearAudio, onInterrupt])

  // Pause
  const pause = useCallback(() => {
    if (audioRef.current && isPlaying) {
      audioRef.current.pause()
      setIsPlaying(false)
      if (timeTimerRef.current) {
        clearInterval(timeTimerRef.current)
        timeTimerRef.current = null
      }
    }
  }, [isPlaying])

  // Resume
  const resume = useCallback(() => {
    if (audioRef.current && !isPlaying) {
      audioRef.current.play()
    }
  }, [isPlaying])

  // Set volume
  const setVolume = useCallback((vol) => {
    if (audioRef.current) {
      audioRef.current.volume = Math.min(1, Math.max(0, vol))
    }
  }, [])

  // Cleanup
  useEffect(() => {
    return () => clearAudio()
  }, [clearAudio])

  // Progress percentage
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return {
    isPlaying,
    duration,
    currentTime,
    progress,
    error,
    playBase64,
    playUrl,
    interrupt,
    pause,
    resume,
    setVolume,
    stop: clearAudio,
  }
}

export default useAudioPlayer
