/* ============================================================
   EDUMIND AI — AUDIO UTILITIES (Voice Tutor)
   ============================================================ */

export async function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      if (typeof reader.result === 'string') {
        const base64 = reader.result.split(',')[1] || ''
        resolve(base64)
      } else {
        resolve('')
      }
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

export function base64ToBlob(base64, mimeType = 'audio/mpeg') {
  if (!base64 || typeof base64 !== 'string') {
    return new Blob([], { type: mimeType })
  }
  try {
    // Strip data prefix and whitespace
    const cleanB64 = base64.replace(/^data:audio\/[^;]+;base64,/, '').replace(/\s/g, '')
    const bytes = atob(cleanB64)
    const buffer = new ArrayBuffer(bytes.length)
    const view = new Uint8Array(buffer)
    for (let i = 0; i < bytes.length; i++) {
      view[i] = bytes.charCodeAt(i)
    }
    return new Blob([buffer], { type: mimeType })
  } catch (err) {
    console.error('base64ToBlob error:', err)
    return new Blob([], { type: mimeType })
  }
}

export function calculateRMS(floatArray) {
  if (!floatArray || floatArray.length === 0) return 0
  let sum = 0
  for (let i = 0; i < floatArray.length; i++) {
    sum += floatArray[i] * floatArray[i]
  }
  return Math.sqrt(sum / floatArray.length)
}

export async function checkMicPermission() {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return false
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach((t) => t.stop())
    return true
  } catch {
    return false
  }
}

export function normalizeLevel(rms, min = 0, max = 0.25) {
  return Math.min(1, Math.max(0, (rms - min) / (max - min)))
}

export function formatAudioTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export function getSupportedAudioFormat() {
  if (typeof window === 'undefined') return { type: 'audio/webm', ext: 'webm' }
  const types = [
    { type: 'audio/webm; codecs=opus', ext: 'webm' },
    { type: 'audio/webm',              ext: 'webm' },
    { type: 'audio/mp4',               ext: 'mp4'  },
    { type: 'audio/ogg; codecs=opus',  ext: 'ogg'  },
    { type: 'audio/wav',               ext: 'wav'  },
  ]
  for (const t of types) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(t.type)) {
      return t
    }
  }
  return { type: 'audio/webm', ext: 'webm' }
}
