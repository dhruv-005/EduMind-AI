import React, { useState, useRef, useEffect } from 'react'
import { FiSend } from 'react-icons/fi'

export default function ChatInterface({ messages, onSend, isLoading, placeholder = "What are you looking for today?" }) {
  const [input, setInput] = useState('')
  const bottomRef         = useRef(null)
  const inputRef          = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = () => {
    if (!input.trim() || isLoading) return
    onSend(input.trim()); setInput(''); inputRef.current?.focus()
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((msg, i) => {
          const isCust = msg.role === 'customer'
          return (
            <div key={i} style={{ display: 'flex', gap: 10, flexDirection: isCust ? 'row-reverse' : 'row', alignItems: 'flex-end' }}>
              <div style={{
                width: 30, height: 30, borderRadius: '50%', flexShrink: 0, fontSize: 14,
                background: isCust ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'linear-gradient(135deg,#ec4899,#8b5cf6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: isCust ? '0 4px 12px rgba(99,102,241,0.3)' : '0 4px 12px rgba(236,72,153,0.3)',
              }}>
                {isCust ? '👤' : '🤖'}
              </div>
              <div style={{
                maxWidth: '72%', padding: '11px 15px',
                borderRadius: isCust
                  ? 'var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg)'
                  : 'var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm)',
                background: isCust ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'var(--bg-card)',
                border: isCust ? 'none' : '1px solid var(--border)',
                boxShadow: isCust ? '0 4px 16px rgba(99,102,241,0.25)' : 'var(--shadow-card)',
              }}>
                <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 13.5, lineHeight: 1.6, color: isCust ? '#ffffff' : 'var(--ink)', margin: 0 }}>
                  {msg.text}
                </p>
              </div>
            </div>
          )
        })}
        {isLoading && (
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'linear-gradient(135deg,#ec4899,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, boxShadow: '0 4px 12px rgba(236,72,153,0.3)', flexShrink: 0 }}>🤖</div>
            <div style={{ padding: '11px 16px', borderRadius: 'var(--radius-lg) var(--radius-lg) var(--radius-lg) var(--radius-sm)', background: 'var(--bg-card)', border: '1px solid var(--border)', display: 'flex', gap: 5, alignItems: 'center' }}>
              {[0,1,2].map(j => <div key={j} className="ai-dot" style={{ animationDelay: `${j * 0.15}s` }} />)}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '12px 16px', borderTop: '1px solid var(--border)',
        display: 'flex', gap: 10, alignItems: 'flex-end',
        background: 'var(--bg-secondary)', flexShrink: 0,
      }}>
        <textarea
          ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
          placeholder={placeholder} rows={1} disabled={isLoading}
          style={{
            flex: 1, padding: '10px 14px',
            background: 'var(--bg-card)', border: '1.5px solid var(--border)',
            borderRadius: 'var(--radius-md)', fontFamily: 'Inter, sans-serif',
            fontSize: 13.5, color: 'var(--ink)', outline: 'none',
            resize: 'none', maxHeight: 100, overflow: 'auto',
            transition: 'border-color 0.2s ease', lineHeight: 1.5,
          }}
          onFocus={e => e.target.style.borderColor = '#6366f1'}
          onBlur={e  => e.target.style.borderColor = 'var(--border)'}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          style={{
            width: 42, height: 42, borderRadius: 'var(--radius-md)',
            background: (!input.trim() || isLoading) ? 'var(--bg-tertiary)' : 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            border: 'none', cursor: (!input.trim() || isLoading) ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'all 0.2s ease', flexShrink: 0,
            boxShadow: (!input.trim() || isLoading) ? 'none' : '0 4px 12px rgba(99,102,241,0.4)',
          }}
        >
          <FiSend size={16} strokeWidth={1.5} style={{ color: (!input.trim() || isLoading) ? 'var(--ink-muted)' : '#ffffff' }} />
        </button>
      </div>
    </div>
  )
}
