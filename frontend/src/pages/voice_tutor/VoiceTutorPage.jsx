/* ============================================================
   EDUMIND AI — VOICE TUTOR PAGE (Challenge 4)
   Real-time voice AI tutor with VAD + multilingual support
   ============================================================ */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useVoiceTutorStore, VAD_STATE } from '@store/voiceTutorStore'
import { useVoiceRecorder } from '@hooks/useVoiceRecorder'
import { useAudioPlayer } from '@hooks/useAudioPlayer'
import { useWebSocket, WS_STATUS } from '@hooks/useWebSocket'
import { voiceTutorService } from '@services/voiceTutorService'
import { SUBJECTS, GRADE_LEVELS } from '@utils/constants'
import { formatDuration } from '@utils/formatters'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import Select from '@components/ui/Select'
import toast from 'react-hot-toast'

const LANGUAGES = [
  { value: "en", label: "English (US)" },
  { value: "es", label: "Español (Spanish)" },
  { value: "fr", label: "Français (French)" },
  { value: "de", label: "Deutsch (German)" },
  { value: "hi", label: "हिन्दी (Hindi)" },
  { value: "ar", label: "العربية (Arabic)" },
  { value: "zh", label: "中文 (Chinese)" }
]

/* ── WAVEFORM VISUALIZER ────────────────────────────────────── */
function Waveform({ audioLevel, isActive, color = 'var(--term-green)', bars = 32 }) {
  const [heights, setHeights] = useState(Array.from({ length: bars }, () => 8))
  const animRef = useRef(null)

  useEffect(() => {
    if (!isActive) {
      setHeights(Array.from({ length: bars }, () => 8))
      return
    }
    const animate = () => {
      setHeights(prev => prev.map((_, i) => {
        const wave = Math.sin(Date.now() / 200 + i * 0.4) * 0.5 + 0.5
        const base = (audioLevel || 0.1) * 60
        const variation = (Math.random() - 0.5) * 15
        return Math.max(4, Math.min(64, base * wave + variation + 8))
      }))
      animRef.current = requestAnimationFrame(animate)
    }
    animRef.current = requestAnimationFrame(animate)
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current) }
  }, [isActive, audioLevel, bars])

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '3px', height: '80px' }}>
      {heights.map((h, i) => (
        <div key={i} style={{
          flex: 1, height: `${h}px`, background: color,
          opacity: isActive ? 0.4 + (i / bars) * 0.6 : 0.15,
          transition: 'height 0.05s ease', borderRadius: '1px', minWidth: '2px',
        }} />
      ))}
    </div>
  )
}

/* ── VAD STATUS ─────────────────────────────────────────────── */
function VADStatus({ state }) {
  const states = {
    [VAD_STATE.IDLE]:       { label: 'IDLE — PRESS START', color: 'var(--muted)',        dot: 'var(--muted)',        pulse: false },
    [VAD_STATE.LISTENING]:  { label: 'LISTENING...',        color: 'var(--term-green)',   dot: 'var(--term-green)',   pulse: true  },
    [VAD_STATE.PROCESSING]: { label: 'PROCESSING...',       color: 'var(--term-amber)',   dot: 'var(--term-amber)',   pulse: true  },
    [VAD_STATE.SPEAKING]:   { label: 'TUTOR SPEAKING',      color: 'var(--accent-cyber)', dot: 'var(--accent-cyber)', pulse: true  },
    [VAD_STATE.ERROR]:      { label: 'CONNECTION ERROR',    color: 'var(--term-red)',     dot: 'var(--term-red)',     pulse: false },
  }
  const s = states[state] || states[VAD_STATE.IDLE]
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
      <span style={{
        width: '10px', height: '10px', borderRadius: '50%',
        background: s.dot, boxShadow: s.pulse ? `0 0 8px ${s.dot}` : 'none',
        animation: s.pulse ? 'pulseDot 1.5s ease-in-out infinite' : 'none',
        display: 'inline-block', flexShrink: 0,
      }} />
      <span style={{
        fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
        textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: s.color,
      }}>
        {s.label}
      </span>
    </div>
  )
}

/* ── TRANSCRIPT BUBBLE ──────────────────────────────────────── */
function TranscriptBubble({ entry }) {
  const isUser   = entry.role === 'user'
  const isSystem = entry.role === 'system'

  if (isSystem) {
    return (
      <div style={{ textAlign: 'center', margin: 'var(--space-4) 0' }}>
        <span style={{
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
          color: 'var(--muted)', padding: '0.25rem 0.75rem',
          border: 'var(--border-thin)', background: 'var(--surface)',
        }}>
          {entry.text}
        </span>
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 'var(--space-4)', gap: 'var(--space-3)', alignItems: 'flex-start',
    }}>
      {!isUser && (
        <div style={{
          width: '32px', height: '32px', background: 'var(--term-bg)',
          border: '2px solid var(--accent-cyber)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          color: 'var(--accent-cyber)', fontWeight: 700,
        }}>AI</div>
      )}

      <div style={{
        maxWidth: '75%', display: 'flex', flexDirection: 'column',
        gap: 'var(--space-1)', alignItems: isUser ? 'flex-end' : 'flex-start',
      }}>
        <span style={{
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
          color: isUser ? 'var(--accent-primary)' : 'var(--accent-cyber)',
        }}>
          {isUser ? 'YOU' : 'AI TUTOR'}
        </span>

        <div style={{
          padding: 'var(--space-4) var(--space-5)',
          background: isUser ? 'var(--accent-primary)' : 'var(--surface)',
          border: isUser ? '2px solid var(--accent-primary)' : '2px solid var(--accent-cyber)',
          boxShadow: isUser ? '4px 4px 0px rgba(255,62,0,0.3)' : '4px 4px 0px rgba(0,240,255,0.2)',
          color: isUser ? '#fff' : 'var(--ink)',
        }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', lineHeight: 1.7 }}>
            {entry.text}
          </p>
        </div>

        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', opacity: 0.5 }}>
          {new Date(entry.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
        </span>
      </div>

      {isUser && (
        <div style={{
          width: '32px', height: '32px', background: 'var(--accent-primary)',
          border: '2px solid var(--accent-primary)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          color: '#fff', fontWeight: 700,
        }}>U</div>
      )}
    </div>
  )
}

/* ── SESSION SUMMARY ────────────────────────────────────────── */
function SessionSummary({ stats, onClose }) {
  return (
    <div style={{
      padding: 'var(--space-8)', background: 'var(--term-bg)',
      border: '3px solid var(--term-green)', boxShadow: '8px 8px 0px var(--term-green)',
    }}>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-widest)', color: 'var(--term-green)', marginBottom: 'var(--space-4)' }}>
        ● SESSION COMPLETE
      </div>
      <div style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h2)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', color: '#fff', lineHeight: 0.92, marginBottom: 'var(--space-6)' }}>
        LEARNING<br /><span style={{ color: 'var(--term-green)' }}>SUMMARY</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
        {[
          { label: 'QUESTIONS ASKED',  value: stats.questionsAsked || 0 },
          { label: 'SESSION DURATION', value: formatDuration(stats.sessionDuration || 0) },
          { label: 'TOPICS COVERED',   value: stats.topicsCovered?.length || 0 },
          { label: 'INTERACTIONS',     value: (stats.questionsAsked || 0) * 2 },
        ].map((s) => (
          <div key={s.label} style={{ padding: 'var(--space-4)', border: '1px solid rgba(0,230,91,0.2)', background: 'rgba(0,230,91,0.05)' }}>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h2)', fontWeight: 700, letterSpacing: 'var(--ls-tight)', color: 'var(--term-green)', lineHeight: 1, marginBottom: 'var(--space-1)' }}>
              {s.value}
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'rgba(255,255,255,0.4)' }}>
              {s.label}
            </div>
          </div>
        ))}
      </div>
      <Button variant="green" onClick={onClose} fullWidth>START NEW SESSION</Button>
    </div>
  )
}

/* ── DEMO TEXT INPUT ────────────────────────────────────────── */
function DemoTextInput({ onSend }) {
  const [text, setText] = useState('')
  const handleSend = () => {
    if (!text.trim()) return
    onSend(text.trim())
    setText('')
  }
  return (
    <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
      <input
        type="text" value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        placeholder="TYPE A QUESTION..."
        style={{
          flex: 1, fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
          color: 'var(--ink)', background: 'var(--surface)',
          border: 'var(--border-thin)', outline: 'none', padding: '0.5rem 0.75rem',
        }}
      />
      <Button variant="green" size="sm" onClick={handleSend} disabled={!text.trim()}>→</Button>
    </div>
  )
}

/* ── MAIN VOICE TUTOR COMPONENT ─────────────────────────────── */
export default function VoiceTutorPage() {
  const {
    sessionId, subject, gradeLevel, isSessionActive,
    vadState, transcript, isPlaying, wsConnected, sessionStats,
    setSubject, setGradeLevel, setVadState, setWsConnected,
    addTranscript, startSession, endSession, incrementQuestions, addTopic, reset,
  } = useVoiceTutorStore()

  const [language, setLanguage] = useState('en')
  const transcriptEndRef = useRef(null)
  const [showSummary,  setShowSummary]  = useState(false)
  const [sessionTimer, setSessionTimer] = useState(0)
  const sessionTimerRef = useRef(null)
  const sessionActiveRef = useRef(isSessionActive)

  useEffect(() => {
    sessionActiveRef.current = isSessionActive
  }, [isSessionActive])

  /* ── AUDIO PLAYER WITH CALLBACKS ──────────────────────────── */
  const { isPlaying: audioPlaying, playBase64, interrupt } = useAudioPlayer({
    onPlayStart: () => {
      useVoiceTutorStore.getState().setIsPlaying(true)
      useVoiceTutorStore.getState().setVadState(VAD_STATE.SPEAKING)
    },
    onPlayEnd: () => {
      useVoiceTutorStore.getState().setIsPlaying(false)
      if (sessionActiveRef.current) {
        useVoiceTutorStore.getState().setVadState(VAD_STATE.LISTENING)
      }
    },
    onInterrupt: () => {
      useVoiceTutorStore.getState().setIsPlaying(false)
      if (sessionActiveRef.current) {
        useVoiceTutorStore.getState().setVadState(VAD_STATE.LISTENING)
      }
    },
  })

  /* ── WEBSOCKET CONNECTION ─────────────────────────────────── */
  const { connect, disconnect, send, status: wsStatus } = useWebSocket({
    autoConnect: false,
    reconnect: true,
    maxReconnects: 5,
    onOpen: () => {
      setWsConnected(true)
      setVadState(VAD_STATE.LISTENING)
    },
    onClose: () => {
      setWsConnected(false)
      if (sessionActiveRef.current) {
        setVadState(VAD_STATE.ERROR)
      }
    },
    onMessage: async (data) => {
      if (data.type === 'connected') {
        if (data.text) {
          addTranscript({ role: 'tutor', text: data.text })
        }
        if (data.audio) {
          await playBase64(data.audio, 'audio/mpeg')
        }
      } else if (data.type === 'transcript') {
        addTranscript({ role: 'user', text: data.text })
      } else if (data.type === 'response') {
        setVadState(VAD_STATE.SPEAKING)
        addTranscript({ role: 'tutor', text: data.text })
        if (data.topic) addTopic(data.topic)
        if (data.audio) {
          await playBase64(data.audio, 'audio/mpeg')
        } else {
          setVadState(VAD_STATE.LISTENING)
        }
      } else if (data.type === 'error') {
        toast.error(`[ TUTOR ] ${data.message}`)
        setVadState(VAD_STATE.LISTENING)
      }
    },
    onError: () => {
      setVadState(VAD_STATE.ERROR)
    },
  })

  /* ── VOICE RECORDER (VAD + BASE64) ────────────────────────── */
  const { isRecording, audioLevel, startRecording, stopRecording, hasPermission } = useVoiceRecorder({
    autoStop: true,
    onRecordingComplete: async ({ base64, format }) => {
      if (!sessionActiveRef.current || !base64) return

      setVadState(VAD_STATE.PROCESSING)
      incrementQuestions()

      send({
        type: 'audio',
        audio: base64,
        format: format?.ext || 'webm',
        session_id: sessionId,
      })
    },
  })

  /* ── AUTO SCROLL ──────────────────────────────────────────── */
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript])

  /* ── SESSION DURATION TIMER ───────────────────────────────── */
  useEffect(() => {
    if (isSessionActive) {
      sessionTimerRef.current = setInterval(() => setSessionTimer(t => t + 1), 1000)
    } else {
      clearInterval(sessionTimerRef.current)
    }
    return () => clearInterval(sessionTimerRef.current)
  }, [isSessionActive])

  /* ── SYNC VAD + RECORDING ─────────────────────────────── */
  useEffect(() => {
    if (!isSessionActive) return
    if (vadState === VAD_STATE.LISTENING && !isRecording && !audioPlaying) {
      startRecording()
    } else if ((vadState === VAD_STATE.PROCESSING || vadState === VAD_STATE.SPEAKING) && isRecording) {
      stopRecording()
    }
  }, [vadState, isSessionActive, isRecording, audioPlaying, startRecording, stopRecording])

  /* ── INTERRUPT HANDLER ────────────────────────────────────── */
  const handleInterrupt = useCallback(() => {
    if (audioPlaying) {
      interrupt()
      stopRecording()
      setVadState(VAD_STATE.LISTENING)
      toast('[ INTERRUPT ] Tutor stopped — listening', { icon: '🎤' })
    }
  }, [audioPlaying, interrupt, stopRecording, setVadState])

  /* ── START SESSION HANDLER ────────────────────────────────── */
  const handleStartSession = async () => {
    toast.loading('[ INIT ] Starting voice session...', { id: 'session-toast' })

    let activeSessionId = null

    try {
      const res = await voiceTutorService.createSession({ subject, grade_level: gradeLevel })
      activeSessionId = res?.data?.session_id || res?.session_id
    } catch (_) {}

    if (!activeSessionId) {
      activeSessionId = `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
    }

    startSession(activeSessionId)
    setSessionTimer(0)

    // Build absolute WebSocket URL with selected language parameter
    const rawWsBase = import.meta.env.VITE_WS_BASE_URL || 'wss://edumind-ai-cwjx.onrender.com'
    const wsBase = rawWsBase.replace(/^http/, 'ws')
    const wsUrl = `${wsBase}/api/v1/voice-tutor/ws/${activeSessionId}?language=${language}`

    addTranscript({
      role: 'system',
      text: `SESSION STARTED — ${subject.toUpperCase()} / ${gradeLevel.toUpperCase()}`,
    })

    connect(wsUrl)
    toast.success('[ READY ] Voice session active! Speak now.', { id: 'session-toast' })
  }

  /* ── END SESSION HANDLER ──────────────────────────────────── */
  const handleEndSession = () => {
    stopRecording()
    interrupt()
    disconnect()
    endSession()
    setShowSummary(true)
  }

  /* ── SEND MESSAGE ─────────────────────────────────────────── */
  const sendDemoMessage = (text) => {
    if (!text) return
    incrementQuestions()
    if (wsStatus === WS_STATUS.OPEN) {
      send({ type: 'text', text, session_id: sessionId })
    } else {
      addTranscript({ role: 'user', text })
      setTimeout(() => {
        addTranscript({
          role: 'tutor',
          text: `That is a thoughtful point about "${text.slice(0, 30)}...". What principle or rule would you apply to investigate further?`
        })
      }, 1000)
    }
  }

  return (
    <div style={{
      minHeight: 'calc(100vh - var(--header-h))',
      display: 'grid',
      gridTemplateColumns: isSessionActive ? '1fr 360px' : '1fr',
      gridTemplateRows: 'auto 1fr',
      background: 'var(--base)',
    }}>

      {/* PAGE HEADER */}
      <div style={{
        gridColumn: '1 / -1',
        padding: 'var(--space-6) var(--space-8)', borderBottom: 'var(--border)',
        background: 'var(--surface)', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)',
      }}>
        <div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-widest)', color: 'var(--term-green)', marginBottom: 'var(--space-2)' }}>
            // CH-04 — VOICE AI TUTOR
          </div>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h2)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', lineHeight: 0.92, display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            VOICE TUTOR
            {isSessionActive && <Badge variant="green" dot pulse>LIVE SESSION</Badge>}
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {isSessionActive && (
            <>
              <VADStatus state={vadState} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--term-green)', fontWeight: 700, letterSpacing: 'var(--ls-wide)' }}>
                {formatDuration(sessionTimer)}
              </span>
              <Button variant="danger" size="sm" onClick={handleEndSession}>■ END SESSION</Button>
            </>
          )}
        </div>
      </div>

      {/* MAIN BODY */}
      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {!isSessionActive && !showSummary && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-12) var(--space-8)', gap: 'var(--space-8)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-display)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', lineHeight: 0.88, marginBottom: 'var(--space-6)' }}>
                24/7<br /><span style={{ color: 'var(--term-green)' }}>AI</span><br />TUTOR
              </div>
              <div style={{ width: '300px', margin: '0 auto var(--space-6)' }}>
                <Waveform audioLevel={0.1} isActive={false} color="var(--term-green)" bars={24} />
              </div>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--muted)', maxWidth: '500px', lineHeight: 1.7 }}>
                Speak naturally. Your AI tutor uses the Socratic method — guiding you with questions and hints. VAD auto-detects your voice.
              </p>
            </div>

            <div style={{ width: '100%', maxWidth: '500px', background: 'var(--base)', border: 'var(--border)', boxShadow: 'var(--shadow)' }}>
              <div style={{ padding: 'var(--space-5) var(--space-6)', borderBottom: 'var(--border)', background: 'var(--surface)' }}>
                <span style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)' }}>
                  SESSION SETUP
                </span>
              </div>
              <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                <Select label="SUBJECT" options={SUBJECTS} value={subject} onChange={(e) => setSubject(e.target.value)} />
                <Select label="GRADE LEVEL" options={GRADE_LEVELS} value={gradeLevel} onChange={(e) => setGradeLevel(e.target.value)} />
                
                {/* Brand-new Language Selector primitive */}
                <Select label="TUTOR LANGUAGE" options={LANGUAGES} value={language} onChange={(e) => setLanguage(e.target.value)} />

                {hasPermission === false && (
                  <div style={{ padding: 'var(--space-3)', background: 'var(--term-red-dim)', border: '1px solid var(--term-red)', borderLeft: '3px solid var(--term-red)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--term-red)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)' }}>
                    ✕ MICROPHONE PERMISSION REQUIRED FOR VOICE INPUT
                  </div>
                )}

                <Button variant="green" size="lg" fullWidth onClick={handleStartSession}>
                  ▶ START VOICE SESSION
                </Button>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', paddingTop: 'var(--space-2)' }}>
                  {['VAD DETECTION', 'GROQ WHISPER', 'AI TUTOR', 'EDGE TTS', 'INTERRUPTION', 'SOCRATIC'].map(tag => (
                    <span key={tag} style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', padding: '0.2rem 0.5rem', border: '1px solid var(--term-green)', color: 'var(--term-green)', background: 'var(--term-green-dim)' }}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {showSummary && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-8)' }}>
            <div style={{ width: '100%', maxWidth: '500px' }}>
              <SessionSummary stats={sessionStats} onClose={() => { setShowSummary(false); reset(); setSessionTimer(0) }} />
            </div>
          </div>
        )}

        {isSessionActive && (
          <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-6) var(--space-8)' }}>
            {transcript.length === 0 && (
              <div style={{ textAlign: 'center', padding: 'var(--space-16)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)' }}>
                SESSION ACTIVE — START SPEAKING OR TYPE BELOW
              </div>
            )}
            {transcript.map((entry, idx) => <TranscriptBubble key={entry.id || idx} entry={entry} />)}
            <div ref={transcriptEndRef} />
          </div>
        )}
      </div>

      {/* RIGHT SIDEBAR */}
      {isSessionActive && (
        <div style={{ borderLeft: 'var(--border)', display: 'flex', flexDirection: 'column', background: 'var(--surface)', overflow: 'hidden' }}>

          <div style={{ padding: 'var(--space-6)', borderBottom: 'var(--border)', background: 'var(--term-bg)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: vadState === VAD_STATE.SPEAKING ? 'var(--accent-cyber)' : 'var(--term-green)', marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', justifycontent: 'space-between' }}>
              <span>{vadState === VAD_STATE.SPEAKING ? 'TUTOR SPEAKING' : isRecording ? 'MIC RECORDING' : 'LISTENING'}</span>
              <VADStatus state={vadState} />
            </div>
            <Waveform
              audioLevel={audioLevel}
              isActive={isRecording || vadState === VAD_STATE.SPEAKING}
              color={vadState === VAD_STATE.SPEAKING ? 'var(--accent-cyber)' : vadState === VAD_STATE.PROCESSING ? 'var(--term-amber)' : 'var(--term-green)'}
              bars={24}
            />
            {audioPlaying && (
              <button onClick={handleInterrupt} style={{ width: '100%', marginTop: 'var(--space-4)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', padding: 'var(--space-3)', background: 'var(--term-red)', color: '#fff', border: '2px solid var(--term-red)', cursor: 'pointer', animation: 'pulseDot 1.5s ease-in-out infinite', boxShadow: '4px 4px 0px rgba(255,45,85,0.4)' }}>
                ■ INTERRUPT TUTOR
              </button>
            )}

            <div style={{ marginTop: 'var(--space-3)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', color: wsStatus === WS_STATUS.OPEN ? 'var(--term-green)' : 'rgba(255,255,255,0.3)' }}>
              ● WS: {wsStatus === WS_STATUS.OPEN ? 'CONNECTED (LIVE)' : wsStatus === WS_STATUS.CONNECTING ? 'CONNECTING...' : 'DISCONNECTED'}
            </div>
          </div>

          <div style={{ padding: 'var(--space-5)', borderBottom: 'var(--border)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--space-3)' }}>
              {[
                { label: 'SUBJECT',   value: subject.toUpperCase() },
                { label: 'LEVEL',     value: gradeLevel.toUpperCase() },
                { label: 'QUESTIONS', value: sessionStats.questionsAsked || 0 },
                { label: 'DURATION',  value: formatDuration(sessionTimer) },
              ].map(s => (
                <div key={s.label} style={{ padding: 'var(--space-3)', background: 'var(--base)', border: 'var(--border-thin)' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--muted)', marginBottom: '2px' }}>{s.label}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', fontWeight: 700, color: 'var(--ink)', textTransform: 'uppercase', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ padding: 'var(--space-5)', flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--muted)', marginBottom: 'var(--space-3)' }}>
              TOPICS DISCUSSED
            </div>
            {sessionStats.topicsCovered?.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {sessionStats.topicsCovered.map(t => <Badge key={t} variant="green">{t}</Badge>)}
              </div>
            ) : (
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', textTransform: 'uppercase' }}>NONE YET</span>
            )}
          </div>

          <div style={{ padding: 'var(--space-4)', borderTop: 'var(--border)', background: 'var(--base)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', marginBottom: 'var(--space-2)' }}>
              TEXT INPUT (OPTIONAL)
            </div>
            <DemoTextInput onSend={sendDemoMessage} />
          </div>
        </div>
      )}

      <style>{`
        @media (max-width: 900px) {
          div[style*="grid-template-columns: 1fr 360px"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
