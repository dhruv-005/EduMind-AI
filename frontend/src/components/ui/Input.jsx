/* ============================================================
   EDUMIND AI — INPUT COMPONENT
   ============================================================ */

import React, { useState, forwardRef } from 'react'

const Input = forwardRef(function Input({
  label       = '',
  placeholder = '',
  value,
  onChange,
  onBlur,
  onFocus,
  error       = '',
  hint        = '',
  type        = 'text',
  disabled    = false,
  required    = false,
  prefix      = null,
  suffix      = null,
  fullWidth   = true,
  style       = {},
  inputStyle  = {},
  id,
  name,
  ...props
}, ref) {
  const [isFocused, setIsFocused] = useState(false)
  const inputId = id || name || label?.toLowerCase().replace(/\s+/g, '-')

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
      display:   'flex',
      flexDirection: 'column',
      gap:       'var(--space-2)',
      width:     fullWidth ? '100%' : 'auto',
      ...style,
    }}>

      {/* Label */}
      {label && (
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
      )}

      {/* Input wrapper */}
      <div style={{
        display:  'flex',
        alignItems: 'stretch',
        border:   `var(--border-width-thin) solid ${borderColor}`,
        boxShadow,
        transition: 'border-color 0.12s ease, box-shadow 0.12s ease',
        background: disabled ? 'var(--surface)' : 'var(--base)',
      }}>

        {/* Prefix */}
        {prefix && (
          <div style={{
            padding:       '0 var(--space-3)',
            display:       'flex',
            alignItems:    'center',
            borderRight:   `1px solid ${borderColor}`,
            background:    'var(--surface)',
            color:         'var(--muted)',
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-data)',
            flexShrink:    0,
            transition:    'border-color 0.12s ease',
          }}>
            {prefix}
          </div>
        )}

        {/* Input */}
        <input
          ref={ref}
          id={inputId}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          placeholder={placeholder}
          onFocus={(e) => {
            setIsFocused(true)
            if (onFocus) onFocus(e)
          }}
          onBlur={(e) => {
            setIsFocused(false)
            if (onBlur) onBlur(e)
          }}
          style={{
            flex:          1,
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-data)',
            color:         'var(--ink)',
            background:    'transparent',
            border:        'none',
            outline:       'none',
            padding:       '0.75rem 1rem',
            width:         '100%',
            cursor:        disabled ? 'not-allowed' : 'text',
            opacity:       disabled ? 0.6 : 1,
            ...inputStyle,
          }}
          {...props}
        />

        {/* Suffix */}
        {suffix && (
          <div style={{
            padding:     '0 var(--space-3)',
            display:     'flex',
            alignItems:  'center',
            borderLeft:  `1px solid ${borderColor}`,
            background:  'var(--surface)',
            color:       'var(--muted)',
            fontFamily:  'var(--font-mono)',
            fontSize:    'var(--fs-data)',
            flexShrink:  0,
            transition:  'border-color 0.12s ease',
          }}>
            {suffix}
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <span style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--term-red)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-wide)',
          display:       'flex',
          alignItems:    'center',
          gap:           'var(--space-1)',
        }}>
          <span>✕</span> {error}
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

export default Input
