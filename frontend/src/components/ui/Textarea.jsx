/* ============================================================
   EDUMIND AI — TEXTAREA COMPONENT
   ============================================================ */

import React, { useState, forwardRef } from 'react'

const Textarea = forwardRef(function Textarea({
  label       = '',
  placeholder = '',
  value,
  onChange,
  onBlur,
  onFocus,
  error       = '',
  hint        = '',
  disabled    = false,
  required    = false,
  rows        = 5,
  maxLength,
  resize      = 'vertical',
  fullWidth   = true,
  style       = {},
  id,
  name,
  ...props
}, ref) {
  const [isFocused, setIsFocused] = useState(false)
  const inputId = id || name || label?.toLowerCase().replace(/\s+/g, '-')

  const charCount = value ? value.length : 0

  const borderColor = error
    ? 'var(--term-red)'
    : isFocused
      ? 'var(--accent-primary)'
      : 'var(--ink)'

  const boxShadow = error
    ? '3px 3px 0px var(--term-red)'
    : isFocused
      ? '3px 3px 0px var(--accent-primary)'
      : 'none'

  return (
    <div style={{
      display:       'flex',
      flexDirection: 'column',
      gap:           'var(--space-2)',
      width:         fullWidth ? '100%' : 'auto',
      ...style,
    }}>

      {/* Label row */}
      {label && (
        <div style={{
          display:        'flex',
          justifyContent: 'space-between',
          alignItems:     'center',
        }}>
          <label
            htmlFor={inputId}
            style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      'var(--fs-nano)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-wider)',
              color:         error ? 'var(--term-red)' : 'var(--muted)',
              display:       'flex',
              alignItems:    'center',
              gap:           'var(--space-1)',
            }}
          >
            {label}
            {required && (
              <span style={{ color: 'var(--accent-primary)' }}>*</span>
            )}
          </label>

          {maxLength && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize:   'var(--fs-nano)',
              color: charCount > maxLength * 0.9
                ? 'var(--term-amber)'
                : 'var(--muted)',
            }}>
              {charCount}/{maxLength}
            </span>
          )}
        </div>
      )}

      {/* Textarea */}
      <textarea
        ref={ref}
        id={inputId}
        name={name}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        placeholder={placeholder}
        rows={rows}
        maxLength={maxLength}
        onFocus={(e) => {
          setIsFocused(true)
          if (onFocus) onFocus(e)
        }}
        onBlur={(e) => {
          setIsFocused(false)
          if (onBlur) onBlur(e)
        }}
        style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-data)',
          color:         'var(--ink)',
          background:    disabled ? 'var(--surface)' : 'var(--base)',
          border:        `var(--border-width-thin) solid ${borderColor}`,
          boxShadow,
          outline:       'none',
          padding:       '0.75rem 1rem',
          width:         fullWidth ? '100%' : 'auto',
          resize,
          lineHeight:    1.6,
          minHeight:     `${rows * 1.6 + 1.5}rem`,
          cursor:        disabled ? 'not-allowed' : 'text',
          opacity:       disabled ? 0.6 : 1,
          transition:    'border-color 0.12s ease, box-shadow 0.12s ease',
        }}
        {...props}
      />

      {/* Error */}
      {error && (
        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--term-red)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
        }}>
          ✕ {error}
        </span>
      )}

      {/* Hint */}
      {hint && !error && (
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize:   'var(--fs-nano)',
          color:      'var(--muted)',
          opacity:    0.7,
        }}>
          {hint}
        </span>
      )}
    </div>
  )
})

export default Textarea
