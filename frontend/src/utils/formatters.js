/* ============================================================
   EDUMIND AI — FORMATTER UTILITIES
   ============================================================ */

import { GRADE_THRESHOLDS } from './constants'

// Format score to display string
export function formatScore(score, maxScore = 10) {
  const normalized = (score / maxScore) * 10
  return normalized.toFixed(1)
}

// Get grade from score
export function getGrade(score, maxScore = 10) {
  const normalized = (score / maxScore) * 10
  const threshold = GRADE_THRESHOLDS.find(
    (t) => normalized >= t.min && normalized <= t.max
  )
  return threshold || GRADE_THRESHOLDS[GRADE_THRESHOLDS.length - 1]
}

// Format percentage
export function formatPercent(value, decimals = 1) {
  return `${(value * 100).toFixed(decimals)}%`
}

// Format bytes to human readable
export function formatBytes(bytes, decimals = 1) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`
}

// Format duration in seconds to mm:ss
export function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

// Format UTC time
export function formatUTC(date = new Date()) {
  return (
    String(date.getUTCHours()).padStart(2, '0') +
    ':' +
    String(date.getUTCMinutes()).padStart(2, '0') +
    ':' +
    String(date.getUTCSeconds()).padStart(2, '0') +
    ' UTC'
  )
}

// Format timestamp to readable
export function formatTimestamp(isoString) {
  const date = new Date(isoString)
  return date.toLocaleString('en-US', {
    month:  'short',
    day:    'numeric',
    hour:   '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

// Format relative time
export function formatRelative(isoString) {
  const now  = Date.now()
  const then = new Date(isoString).getTime()
  const diff = Math.floor((now - then) / 1000)

  if (diff < 60)   return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

// Truncate text
export function truncate(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// Capitalize first letter
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

// Format currency
export function formatCurrency(amount, currency = 'INR') {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
  }).format(amount)
}

// Lead tier display
export function formatLeadTier(tier) {
  const map = {
    HOT:  { label: 'HOT',  emoji: '🔥' },
    WARM: { label: 'WARM', emoji: '⚡' },
    COOL: { label: 'COOL', emoji: '🌊' },
    COLD: { label: 'COLD', emoji: '❄️' },
  }
  return map[tier] || map.COLD
}

// File extension
export function getFileExtension(filename) {
  return filename.split('.').pop().toLowerCase()
}

// Pad number
export function padNum(num, size = 2) {
  return String(num).padStart(size, '0')
}

// Format number with commas
export function formatNumber(num) {
  return new Intl.NumberFormat('en-US').format(num)
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
