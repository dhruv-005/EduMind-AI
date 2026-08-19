/* ============================================================
   EDUMIND AI — AUDIO UTILITIES (Voice Tutor)
   ============================================================ */

// Convert blob to base64
export async function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result.split(',')[1])
    reader.onerror   = reject
    reader.readAsDataURL(blob)
  })
}

// Convert base64 to blob
export function base64ToBlob(base64, mimeType = 'audio/wav') {
  const bytes  = atob(base64)
  const buffer = new ArrayBuffer(bytes.length)
  const view   = new Uint8Array(buffer)
  for (let i = 0; i < bytes.length; i++) {
    view[i] = bytes.charCodeAt(i)
  }
  return new Blob([buffer], { type: mimeType })
}

// Get audio duration from blob
export function getAudioDuration(blob) {
  return new Promise((resolve) => {
    const audio = new Audio()
    const url   = URL.createObjectURL(blob)
    audio.addEventListener('loadedmetadata', () => {
      resolve(audio.duration)
      URL.revokeObjectURL(url)
    })
    audio.src = url
  })
}

// Calculate RMS audio level from Float32Array
export function calculateRMS(floatArray) {
  const sum = floatArray.reduce((acc, val) => acc + val * val, 0)
  return Math.sqrt(sum / floatArray.length)
}

// Check microphone permission
export async function checkMicPermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach((t) => t.stop())
    return true
  } catch {
    return false
  }
}

// Create audio context
export function createAudioContext() {
  const AudioContext =
    window.AudioContext || window.webkitAudioContext
  if (!AudioContext) throw new Error('AudioContext not supported')
  return new AudioContext()
}

// Normalize audio level to 0-1 range
export function normalizeLevel(rms, min = 0, max = 0.3) {
  return Math.min(1, Math.max(0, (rms - min) / (max - min)))
}

// Format audio time
export function formatAudioTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

// Supported audio formats check
export function getSupportedAudioFormat() {
  const audio   = document.createElement('audio')
  const formats = [
    { type: 'audio/webm; codecs=opus', ext: 'webm' },
    { type: 'audio/ogg; codecs=opus',  ext: 'ogg'  },
    { type: 'audio/mp4',               ext: 'mp4'  },
    { type: 'audio/wav',               ext: 'wav'  },
  ]
  for (const fmt of formats) {
    if (audio.canPlayType(fmt.type) !== '') return fmt
  }
  return { type: 'audio/wav', ext: 'wav' }
}
