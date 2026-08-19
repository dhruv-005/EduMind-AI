/* ============================================================
   EDUMIND AI — GENERAL HELPER UTILITIES
   ============================================================ */

// Generate unique ID
export function generateId(prefix = 'edm') {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

// Deep clone object
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj))
}

// Debounce
export function debounce(fn, delay = 300) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

// Throttle
export function throttle(fn, limit = 100) {
  let inThrottle
  return (...args) => {
    if (!inThrottle) {
      fn(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// Sleep / delay
export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// Copy to clipboard
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // Fallback
    const el = document.createElement('textarea')
    el.value = text
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
    return true
  }
}

// Download blob as file
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href    = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// Parse query string
export function parseQuery(search) {
  return Object.fromEntries(new URLSearchParams(search))
}

// Check if mobile viewport
export function isMobile() {
  return window.innerWidth < 768
}

// Clamp number
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

// Random int between
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

// Shuffle array
export function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// Group array by key
export function groupBy(arr, key) {
  return arr.reduce((acc, item) => {
    const group = item[key]
    if (!acc[group]) acc[group] = []
    acc[group].push(item)
    return acc
  }, {})
}

// Flatten nested array
export function flatten(arr) {
  return arr.reduce(
    (acc, val) => acc.concat(Array.isArray(val) ? flatten(val) : val),
    []
  )
}

// Check environment
export const isDev  = import.meta.env.DEV
export const isProd = import.meta.env.PROD

// Local log — only in dev
export function devLog(...args) {
  if (isDev) console.log('[EduMind]', ...args)
}
