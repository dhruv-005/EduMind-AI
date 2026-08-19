/* ============================================================
   EDUMIND AI — VALIDATION UTILITIES
   ============================================================ */

// Required field check
export function required(value, label = 'Field') {
  if (!value || String(value).trim() === '') {
    return `${label} is required`
  }
  return null
}

// Min length
export function minLength(value, min, label = 'Field') {
  if (!value || value.length < min) {
    return `${label} must be at least ${min} characters`
  }
  return null
}

// Max length
export function maxLength(value, max, label = 'Field') {
  if (value && value.length > max) {
    return `${label} must be under ${max} characters`
  }
  return null
}

// Number range
export function inRange(value, min, max, label = 'Value') {
  const num = Number(value)
  if (isNaN(num) || num < min || num > max) {
    return `${label} must be between ${min} and ${max}`
  }
  return null
}

// Email
export function isEmail(value) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!re.test(value)) return 'Invalid email address'
  return null
}

// File size
export function maxFileSize(file, maxBytes, label = 'File') {
  if (file && file.size > maxBytes) {
    const mb = (maxBytes / 1024 / 1024).toFixed(0)
    return `${label} must be under ${mb}MB`
  }
  return null
}

// File type
export function allowedFileType(file, allowedTypes = []) {
  if (!file) return null
  const ext = file.name.split('.').pop().toLowerCase()
  if (!allowedTypes.includes(ext)) {
    return `File type .${ext} is not supported`
  }
  return null
}

// Validate evaluator form
export function validateEvaluatorForm(data) {
  const errors = {}

  const qErr = required(data.question, 'Question')
  if (qErr) errors.question = qErr

  const raErr = required(data.reference_answer, 'Reference Answer')
  if (raErr) errors.reference_answer = raErr

  const saErr = required(data.student_answer, 'Student Answer')
  if (saErr) errors.student_answer = saErr

  const saMin = minLength(data.student_answer, 5, 'Student Answer')
  if (saMin) errors.student_answer = saMin

  const scoreErr = inRange(data.max_score, 1, 100, 'Max Score')
  if (scoreErr) errors.max_score = scoreErr

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  }
}

// Validate generator config
export function validateGeneratorConfig(config) {
  const errors = {}

  const subjErr = required(config.subject, 'Subject')
  if (subjErr) errors.subject = subjErr

  const numErr = inRange(config.numQuestions, 1, 50, 'Number of Questions')
  if (numErr) errors.numQuestions = numErr

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  }
}

// Run multiple validators
export function runValidators(value, validators) {
  for (const validator of validators) {
    const error = validator(value)
    if (error) return error
  }
  return null
}
