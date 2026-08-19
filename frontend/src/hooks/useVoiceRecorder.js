/* ============================================================
   EDUMIND AI — VOICE RECORDER HOOK
   MediaRecorder + VAD-ready audio capture
   ============================================================ */

import { useState, useRef, useCallback, useEffect } from 'react'
import {
  checkMicPermission,
  calculateRMS,
  normalizeLevel,
  getSupportedAudioFormat,
  blobToBase64,
} from '@utils/audioUtils'
import { devLog } from '@utils/helpers'
import toast from 'react-hot-toast'

const SILENCE_THRESHOLD = 0.015
const SILENCE_DURATION  = 1500   // ms of silence before auto-stop
const MIN_RECORD_DURATION = 300  // ms minimum recording

export function useVoiceRecorder({
  onRecordingComplete = null,
  onAudioLevel        = null,
  autoStop            = true,   // auto-stop on silence
} = {}) {
  const [isRecording, setIsRecording]     = useState(false)
  const [isPreparing, setIsPreparing]     = useState(false)
  const [audioLevel, setAudioLevel]       = useState(0)
  const [hasPermission, setHasPermission] = useState(null)
  const [error, setError]                 = useState(null)
  const [duration, setDuration]           = useState(0)

  const mediaRecorderRef  = useRef(null)
  const audioContextRef   = useRef(null)
  const analyserRef       = useRef(null)
  const streamRef         = useRef(null)
  const chunksRef         = useRef([])
  const silenceTimerRef   = useRef(null)
  const startTimeRef      = useRef(null)
  const durationTimerRef  = useRef(null)
  const animFrameRef      = useRef(null)
  const formatRef         = useRef(getSupportedAudioFormat())

  // Check permission on mount
  useEffect(() => {
    checkMicPermission().then(setHasPermission)
  }, [])

  // Monitor audio level via Web Audio API
  const startLevelMonitor = useCallback(() => {
    if (!analyserRef.current) return

    const bufferLength = analyserRef.current.fftSize
    const dataArray    = new Float32Array(bufferLength)

    const monitor = () => {
      if (!analyserRef.current) return
      analyserRef.current.getFloatTimeDomainData(dataArray)

      const rms   = calculateRMS(dataArray)
      const level = normalizeLevel(rms)

      setAudioLevel(level)
      if (onAudioLevel) onAudioLevel(level)

      // Silence detection for auto-stop
      if (autoStop && isRecording) {
        if (rms < SILENCE_THRESHOLD) {
          if (!silenceTimerRef.current) {
            silenceTimerRef.current = setTimeout(() => {
              const elapsed = Date.now() - (startTimeRef.current || 0)
              if (elapsed > MIN_RECORD_DURATION) {
                devLog('VAD: Silence detected — stopping')
                stopRecording()
              }
            }, SILENCE_DURATION)
          }
        } else {
          // Reset silence timer if speech detected
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current)
            silenceTimerRef.current = null
          }
        }
      }

      animFrameRef.current = requestAnimationFrame(monitor)
    }

    animFrameRef.current = requestAnimationFrame(monitor)
  }, [autoStop, onAudioLevel, isRecording])

  // Start recording
  const startRecording = useCallback(async () => {
    setError(null)
    setIsPreparing(true)

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount:      1,
          sampleRate:        16000,
          echoCancellation:  true,
          noiseSuppression:  true,
          autoGainControl:   true,
        },
      })

      setHasPermission(true)
      streamRef.current = stream

      // Setup Web Audio API for level monitoring
      const AudioCtx = window.AudioContext || window.webkitAudioContext
      audioContextRef.current = new AudioCtx({ sampleRate: 16000 })
      analyserRef.current = audioContextRef.current.createAnalyser()
      analyserRef.current.fftSize = 256

      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)

      // Setup MediaRecorder
      const mimeType = formatRef.current.type
      const options  = MediaRecorder.isTypeSupported(mimeType)
        ? { mimeType }
        : {}

      mediaRecorderRef.current = new MediaRecorder(stream, options)
      chunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(chunksRef.current, {
          type: formatRef.current.type,
        })

        devLog('Recorder: Blob size', blob.size, 'type', blob.type)

        if (onRecordingComplete && blob.size > 0) {
          const base64 = await blobToBase64(blob)
          onRecordingComplete({ blob, base64, format: formatRef.current })
        }

        // Cleanup stream
        stream.getTracks().forEach((t) => t.stop())
        streamRef.current = null

        if (audioContextRef.current) {
          audioContextRef.current.close()
          audioContextRef.current = null
        }

        setAudioLevel(0)
      }

      mediaRecorderRef.current.start(100) // collect every 100ms
      startTimeRef.current = Date.now()

      // Duration counter
      durationTimerRef.current = setInterval(() => {
        setDuration(
          Math.floor((Date.now() - startTimeRef.current) / 1000)
        )
      }, 1000)

      setIsRecording(true)
      setIsPreparing(false)

      // Start level monitoring
      startLevelMonitor()

    } catch (err) {
      setIsPreparing(false)
      setHasPermission(false)

      const msg = err.name === 'NotAllowedError'
        ? 'Microphone permission denied'
        : err.message || 'Could not start recording'

      setError(msg)
      toast.error(`[ MIC ERROR ] ${msg}`)
    }
  }, [onRecordingComplete, startLevelMonitor])

  // Stop recording
  const stopRecording = useCallback(() => {
    // Cancel silence timer
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current)
      silenceTimerRef.current = null
    }

    // Cancel animation frame
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current)
      animFrameRef.current = null
    }

    // Clear duration timer
    if (durationTimerRef.current) {
      clearInterval(durationTimerRef.current)
      durationTimerRef.current = null
    }

    // Stop MediaRecorder
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== 'inactive'
    ) {
      mediaRecorderRef.current.stop()
    }

    setIsRecording(false)
    setDuration(0)
    analyserRef.current = null
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording()
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop())
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [stopRecording])

  return {
    isRecording,
    isPreparing,
    audioLevel,
    hasPermission,
    error,
    duration,
    startRecording,
    stopRecording,
  }
}

export default useVoiceRecorder
