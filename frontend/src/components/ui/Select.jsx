/* ============================================================
   EDUMIND AI — SELECT COMPONENT
   ============================================================ */

import React, { useState, forwardRef } from 'react'

const Select = forwardRef(function Select({
  label     = '',
  options   = [],
  value,
  onChange,
  error     = '',
  hint      = '',
  disabled  = false,
  required  = false,
  placeholder = 'SELECT OPTION',
  fullWidth = true,
  style     = {},
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
      display:       'flex',
      flexDirection: 'column',
      gap:           'var(--space-2)',
      width:         fullWidth ? '100%' : 'auto',
      ...style,
    }}>

      {label && (
        <label
          htmlFor={inputId}
          style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-nano)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wider)',
            color:         error ? 'var(--term-red)' : 'var(--muted)',
          }}
        >
          {label}
          {required && (
            <span style={{ color: 'var(--accent-primary)', marginLeft: '4px' }}>*</span>
          )}
        </label>
      )}

      {/* Select wrapper */}
      <div style={{ position: 'relative' }}>
        <select
          ref={ref}
          id={inputId}
          name={name}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          style={{
            fontFamily:    'var(--font-mono)',
            fontSize:      'var(--fs-data)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
            color:         'var(--ink)',
            background:    disabled ? 'var(--surface)' : 'var(--base)',
            border:        `var(--border-width-thin) solid ${borderColor}`,
            boxShadow,
            outline:       'none',
            padding:       '0.75rem 2.5rem 0.75rem 1rem',
            width:         fullWidth ? '100%' : 'auto',
            cursor:        disabled ? 'not-allowed' : 'pointer',
            opacity:       disabled ? 0.6 : 1,
            appearance:    'none',
            transition:    'border-color 0.12s ease, box-shadow 0.12s ease',
          }}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option
              key={opt.value}
              value={opt.value}
              disabled={opt.disabled}
            >
              {opt.label}
            </option>
          ))}
        </select>

        {/* Custom arrow */}
        <div style={{
          position:      'absolute',
          right:         '1rem',
          top:           '50%',
          transform:     'translateY(-50%)',
          pointerEvents: 'none',
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         'var(--muted)',
        }}>
          ▼
        </div>
      </div>

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

export default Select
