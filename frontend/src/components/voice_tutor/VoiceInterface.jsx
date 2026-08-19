import React from 'react'
import { m, useReducedMotion } from 'framer-motion'
import { FiMic, FiSquare, FiZap } from 'react-icons/fi'
import Waveform from './Waveform'
import StatusIndicator from './StatusIndicator'

export default function VoiceInterface({ status, isConnected, onStart, onStop, onInterrupt, transcript, isSpeaking, isListening, isProcessing, analyser = null }) {
  const shouldReduce = useReducedMotion()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22, padding: '8px 0' }}>
      <StatusIndicator status={status} isConnected={isConnected} />

      <div style={{ width: '100%', maxWidth: 300 }}>
        <Waveform active={isListening || isProcessing || isSpeaking} isSpeaking={isSpeaking} analyser={analyser} height={64} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {!isConnected ? (
          <m.button
            onClick={onStart}
            whileHover={shouldReduce ? undefined : { scale: 1.06 }}
            whileTap={shouldReduce  ? undefined : { scale: 0.95 }}
            aria-label="Start voice session"
            style={{
              width: 80, height: 80, borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: '#ffffff', border: 'none', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 8px 32px rgba(99,102,241,0.45)',
              position: 'relative',
            }}
          >
            {!shouldReduce && (
              <>
                <m.span
                  animate={{ scale: [1, 1.6], opacity: [0.4, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut' }}
                  style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                />
                <m.span
                  animate={{ scale: [1, 1.3], opacity: [0.3, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut', delay: 0.5 }}
                  style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
                />
              </>
            )}
            <FiMic size={30} strokeWidth={1.5} style={{ position: 'relative', zIndex: 1 }} />
          </m.button>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            {isSpeaking && (
              <m.button
                onClick={onInterrupt}
                whileHover={shouldReduce ? undefined : { scale: 1.1 }}
                whileTap={shouldReduce   ? undefined : { scale: 0.94 }}
                aria-label="Interrupt AI"
                style={{
                  width: 50, height: 50, borderRadius: '50%',
                  background: 'linear-gradient(135deg, #f59e0b, #f43f5e)',
                  color: '#ffffff', border: 'none', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 4px 16px rgba(245,158,11,0.4)',
                }}
              >
                <FiZap size={22} strokeWidth={1.5} />
              </m.button>
            )}
            <m.button
              onClick={onStop}
              whileHover={shouldReduce ? undefined : { scale: 1.06 }}
              whileTap={shouldReduce   ? undefined : { scale: 0.95 }}
              aria-label="End session"
              style={{
                width: 68, height: 68, borderRadius: '50%',
                background: 'linear-gradient(135deg, #f43f5e, #ec4899)',
                color: '#ffffff', border: 'none', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 8px 24px rgba(244,63,94,0.4)',
              }}
            >
              <FiSquare size={24} strokeWidth={1.5} />
            </m.button>
          </div>
        )}
      </div>

      <p style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 12, fontWeight: 600, color: 'var(--ink-muted)', textAlign: 'center', maxWidth: 240, lineHeight: 1.5, margin: 0, fontStyle: 'italic' }}>
        {!isConnected ? 'Tap the mic to start your AI tutoring session'
          : isSpeaking ? 'Tap ⚡ or speak to interrupt the tutor'
          : isListening ? 'Listening — ask your question'
          : isProcessing ? 'Processing your question…'
          : 'Session active — tap ⏹ to end'
        }
      </p>

      {transcript && isConnected && (
        <div style={{
          width: '100%', padding: '12px 16px',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.06))',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(99,102,241,0.15)',
          fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'var(--ink-soft)',
          lineHeight: 1.5, fontStyle: 'italic',
        }}>
          "{transcript}"
        </div>
      )}
    </div>
  )
}
