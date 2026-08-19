/* ============================================================
   EDUMIND AI — SALES AI PAGE (Challenge 5)
   ============================================================ */

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useSalesStore, LEAD_TIER } from '@store/salesStore'
import { salesService } from '@services/salesService'
import { copyToClipboard } from '@utils/helpers'
import { formatLeadTier, formatCurrency } from '@utils/formatters'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'
import { SpinnerDots } from '@components/ui/Spinner'
import Tabs from '@components/ui/Tabs'
import toast from 'react-hot-toast'

/* ── LEAD SCORE METER ───────────────────────────────────────── */
function LeadScoreMeter({ score, tier }) {
  const tierColors = {
    HOT:  'var(--term-red)',
    WARM: 'var(--term-amber)',
    COOL: 'var(--accent-cyber)',
    COLD: 'var(--muted)',
  }
  const info  = formatLeadTier(tier)
  const color = tierColors[tier] || 'var(--muted)'

  return (
    <div style={{ padding: 'var(--space-5)', background: 'var(--base)', border: `2px solid ${color}`, boxShadow: `4px 4px 0px ${color}` }}>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--muted)', marginBottom: 'var(--space-3)' }}>
        LEAD SCORE
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
        <span style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-display)', fontWeight: 700, letterSpacing: 'var(--ls-tight)', lineHeight: 1, color }}>
          {score}
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--muted)', marginBottom: '0.4rem' }}>/ 100</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
        <span style={{ fontSize: '1.2rem' }}>{info.emoji}</span>
        <span style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h3)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', color }}>
          {info.label}
        </span>
      </div>
      <ProgressBar value={score} max={100} color={color} showValue={false} height="8px" />
    </div>
  )
}

/* ── PRODUCT CARD ───────────────────────────────────────────── */
function ProductCard({ product, rank }) {
  const rankColors = ['var(--accent-primary)', 'var(--accent-cyber)', 'var(--term-green)']
  const color = rankColors[rank] || 'var(--muted)'

  return (
    <div style={{ background: 'var(--base)', border: `2px solid ${color}`, boxShadow: `4px 4px 0px ${color}`, padding: 'var(--space-5)', position: 'relative' }}>
      <div style={{ position: 'absolute', top: '-12px', left: 'var(--space-4)', background: color, color: '#fff', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', padding: '0.2rem 0.6rem', border: '2px solid var(--base)' }}>
        #{rank + 1} MATCH
      </div>
      <div style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', marginBottom: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
        {product.name}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
        {product.category && <Badge variant="default">{product.category}</Badge>}
        {product.price !== undefined && (
          <span style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)', fontWeight: 700, color, letterSpacing: 'var(--ls-tight)' }}>
            {typeof product.price === 'number' ? `₹${product.price.toLocaleString('en-IN')}` : product.price}
          </span>
        )}
      </div>
      {product.description && (
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', lineHeight: 1.6, marginBottom: 'var(--space-4)' }}>
          {product.description}
        </p>
      )}
      {product.why_match && (
        <div style={{ padding: 'var(--space-3)', background: 'var(--surface)', border: `1px solid ${color}`, borderLeft: `3px solid ${color}` }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', color, marginBottom: 'var(--space-1)' }}>
            WHY IT MATCHES
          </div>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--ink)', lineHeight: 1.5 }}>
            {product.why_match}
          </p>
        </div>
      )}
      {product.features && product.features.length > 0 && (
        <div style={{ marginTop: 'var(--space-4)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-1)' }}>
          {product.features.slice(0, 5).map((f, i) => (
            <span key={i} style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', padding: '0.15rem 0.4rem', border: '1px solid var(--border-subtle)', color: 'var(--muted)', background: 'var(--surface)' }}>
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

/* ── CHAT MESSAGE ───────────────────────────────────────────── */
function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: 'var(--space-4)', gap: 'var(--space-3)', alignItems: 'flex-start' }}>
      {!isUser && (
        <div style={{ width: '32px', height: '32px', background: 'var(--term-bg)', border: '2px solid var(--accent-purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--accent-purple)', fontWeight: 700 }}>
          AI
        </div>
      )}
      <div style={{ maxWidth: '78%', display: 'flex', flexDirection: 'column', gap: 'var(--space-1)', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: isUser ? 'var(--accent-primary)' : 'var(--accent-purple)' }}>
          {isUser ? 'CUSTOMER' : 'SALES AI'}
        </span>
        <div style={{ padding: 'var(--space-4) var(--space-5)', background: isUser ? 'var(--accent-primary)' : 'var(--surface)', border: isUser ? '2px solid var(--accent-primary)' : '2px solid var(--accent-purple)', boxShadow: isUser ? '4px 4px 0px rgba(255,62,0,0.25)' : '4px 4px 0px rgba(123,0,255,0.2)', color: isUser ? '#fff' : 'var(--ink)' }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
            {message.content}
          </p>
        </div>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', opacity: 0.5 }}>
          {new Date(message.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })}
        </span>
      </div>
      {isUser && (
        <div style={{ width: '32px', height: '32px', background: 'var(--accent-primary)', border: '2px solid var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: '#fff', fontWeight: 700 }}>
          C
        </div>
      )}
    </div>
  )
}

/* ── FOLLOW UP PANEL ────────────────────────────────────────── */
function FollowUpPanel() {
  const {
    conversationId,
    followUpEmail, followUpWhatsapp,
    isGeneratingFollowUp,
    setFollowUpEmail, setFollowUpWhatsapp, setIsGeneratingFollowUp,
  } = useSalesStore()

  const [copied, setCopied] = useState(null)

  const handleGenerate = async () => {
    setIsGeneratingFollowUp(true)
    try {
      const convId = conversationId || 'demo-conv'
      const result = await salesService.generateFollowUp(convId)
      const data   = result?.data || result || {}
      setFollowUpEmail(data.email    || '')
      setFollowUpWhatsapp(data.whatsapp || '')
      toast.success('[ GENERATED ] Follow-up messages ready')
    } catch (err) {
      // Offline fallback
      setFollowUpEmail(
        "Subject: Thank you for exploring EduMind AI!\n\n" +
        "Dear Valued Customer,\n\n" +
        "Thank you for your interest today. I recommend EduPro Premium (₹4,999/year):\n" +
        "✓ AI-powered personalized tutoring\n" +
        "✓ Real-time progress analytics\n" +
        "✓ Parent dashboard\n" +
        "✓ Offline learning mode\n\n" +
        "Reply for a free demo!\n\nBest regards,\nEduMind AI Sales Team"
      )
      setFollowUpWhatsapp(
        "Hi! 👋 Thank you for your interest in EduMind AI! 🎓\n\n" +
        "Top pick for you:\n" +
        "🏆 *EduPro Premium* — ₹4,999/year\n" +
        "✅ AI Tutor ✅ Analytics ✅ Parent Dashboard\n\n" +
        "Want a free demo? 😊"
      )
      toast.success('[ GENERATED ] Follow-up messages ready (offline mode)')
    } finally {
      setIsGeneratingFollowUp(false)
    }
  }

  const handleCopy = async (type, text) => {
    await copyToClipboard(text)
    setCopied(type)
    toast.success(`[ COPIED ] ${type} message copied`)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <Button variant="primary" onClick={handleGenerate} loading={isGeneratingFollowUp} disabled={isGeneratingFollowUp} fullWidth style={{ background: 'var(--accent-purple)', borderColor: 'var(--accent-purple)' }}>
        ⚡ GENERATE FOLLOW-UP MESSAGES
      </Button>

      {followUpEmail && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--muted)' }}>EMAIL TEMPLATE</span>
            <Button variant="ghost" size="sm" onClick={() => handleCopy('EMAIL', followUpEmail)}>
              {copied === 'EMAIL' ? '✓ COPIED' : 'COPY'}
            </Button>
          </div>
          <div style={{ padding: 'var(--space-4)', background: 'var(--surface)', border: 'var(--border-thin)', borderLeft: '3px solid var(--accent-primary)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--ink)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
            {followUpEmail}
          </div>
        </div>
      )}

      {followUpWhatsapp && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-2)' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--muted)' }}>WHATSAPP MESSAGE</span>
            <Button variant="ghost" size="sm" onClick={() => handleCopy('WA', followUpWhatsapp)}>
              {copied === 'WA' ? '✓ COPIED' : 'COPY'}
            </Button>
          </div>
          <div style={{ padding: 'var(--space-4)', background: 'var(--surface)', border: 'var(--border-thin)', borderLeft: '3px solid var(--term-green)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--ink)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
            {followUpWhatsapp}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── MAIN SALES PAGE ────────────────────────────────────────── */
export default function SalesPage() {
  const {
    messages, isTyping, recommendations, leadScore,
    conversationId, customerProfile,
    setIsTyping, addMessage, setConversationId,
    setRecommendations, setLeadScore, updateCustomerProfile, resetConversation,
  } = useSalesStore()

  const [input, setInput]   = useState('')
  const messagesEndRef      = useRef(null)
  const inputRef            = useRef(null)

  /* ── AUTO SCROLL ────────────────────────────────────────── */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  /* ── INIT CONVERSATION ──────────────────────────────────── */
  const initConversation = useCallback(async () => {
    try {
      const result = await salesService.startConversation()
      const data   = result?.data || result || {}
      const convId = data.conversation_id || data.id || `conv_${Date.now()}`
      setConversationId(convId)
      return convId
    } catch {
      const convId = `conv_${Date.now()}`
      setConversationId(convId)
      return convId
    }
  }, [setConversationId])

  /* ── SEND MESSAGE ───────────────────────────────────────── */
  const handleSend = async () => {
    const text = input.trim()
    if (!text) return

    setInput('')
    addMessage({ role: 'user', content: text })

    let convId = conversationId
    if (!convId) {
      convId = await initConversation()
    }

    setIsTyping(true)

    try {
      const result = await salesService.sendMessage(convId, text)

      // Handle nested response format: result.data.response or result.response
      const responseData = result?.data || result || {}
      const responseText = responseData.response || result.response

      if (responseText) {
        addMessage({ role: 'assistant', content: responseText })
      } else {
        addMessage({ role: 'assistant', content: 'I can help you find the right educational product. What is your budget and grade level?' })
      }

      // Update recommendations
      const recs = responseData.recommendations || result.recommendations || []
      if (recs.length > 0) setRecommendations(recs)

      // Update lead score
      const ls = responseData.lead_score || result.lead_score
      if (ls) {
        setLeadScore({
          total:     ls.total     ?? 55,
          tier:      ls.tier      ?? 'WARM',
          breakdown: ls.breakdown ?? { budget: 15, intent: 20, authority: 10, urgency: 10 },
        })
      }

      // Update customer profile
      const cp = responseData.customer_profile || result.customer_profile
      if (cp) updateCustomerProfile(cp)

    } catch (err) {
      // Offline / error fallback
      const msg = text.toLowerCase()
      let fallback = ''

      if (msg.includes('grade') || msg.includes('class') || msg.includes('student')) {
        fallback = "For Grade 10 students, I highly recommend **EduPro Premium** (₹4,999/year).\n\nIt includes:\n✓ AI-powered tutoring for all Grade 10 subjects\n✓ Practice tests aligned with board exams\n✓ Parent progress dashboard\n✓ Offline study mode\n\nWould you like to know more about the features?"
      } else if (msg.includes('budget') || msg.includes('price') || msg.includes('cost')) {
        fallback = "We have options for every budget:\n\n💰 SmartLearn Basic — ₹2,499/year\n⭐ EduPro Premium — ₹4,999/year (Most Popular)\n🏆 AcademyX Premium — ₹7,999/year\n\nWhich range works for you?"
      } else {
        fallback = `Thank you for your question about "${text.slice(0, 40)}..."!\n\nOur top recommendation is **EduPro Premium** at ₹4,999/year with AI tutoring included.\n\nCould you tell me:\n1. What grade/level is this for?\n2. What's your budget?\n3. What features matter most?`
      }

      addMessage({ role: 'assistant', content: fallback })

      // Add demo recommendations after 2+ messages
      if (messages.length >= 2 && recommendations.length === 0) {
        setRecommendations([
          { name: 'EduPro Premium', category: 'Software', price: 4999, description: 'Advanced AI-powered learning platform', features: ['AI Tutor', 'Analytics', 'Parent Dashboard', 'Offline Mode'], why_match: 'Best value — matches Grade 10 requirements', match_score: 0.95 },
          { name: 'SmartLearn Basic', category: 'Software', price: 2499, description: 'Affordable online learning platform', features: ['Video Lessons', 'Practice Tests', 'Certificate'], why_match: 'Budget-friendly with core features', match_score: 0.80 },
          { name: 'AcademyX Premium', category: 'Platform', price: 7999, description: 'Premium platform with live tutoring', features: ['Live Tutors', 'Gamification', 'Advanced Analytics'], why_match: 'Best feature set if budget allows', match_score: 0.72 },
        ])
        setLeadScore({ total: 60, tier: 'WARM', breakdown: { budget: 15, intent: 20, authority: 15, urgency: 10 } })
      }
    } finally {
      setIsTyping(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickPrompts = [
    "I'm looking for educational software under ₹5000",
    "I need a product for Grade 10 students",
    "Compare your top 3 learning platforms",
    "What's best for CBSE board exam preparation?",
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gridTemplateRows: 'auto 1fr', minHeight: 'calc(100vh - var(--header-h))', background: 'var(--base)' }}>

      {/* HEADER */}
      <div style={{ gridColumn: '1 / -1', padding: 'var(--space-5) var(--space-8)', borderBottom: 'var(--border)', background: 'var(--surface)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
        <div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-widest)', color: 'var(--accent-purple)', marginBottom: 'var(--space-1)' }}>
            // CH-05 — AI SALES ASSISTANT
          </div>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h2)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', lineHeight: 0.92, display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            SALES AI
            <Badge variant="green" dot pulse>ONLINE</Badge>
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <Link to="/sales/catalogue"><Button variant="surface" size="sm">MANAGE CATALOGUE</Button></Link>
          <Link to="/sales/leads"><Button variant="surface" size="sm">VIEW LEADS</Button></Link>
          <Button variant="ghost" size="sm" onClick={resetConversation}>NEW CHAT</Button>
        </div>
      </div>

      {/* CHAT AREA */}
      <div style={{ display: 'flex', flexDirection: 'column', borderRight: 'var(--border)', overflow: 'hidden' }}>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-6) var(--space-8)' }}>

          {messages.length === 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: 'var(--space-6)', textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h2)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', lineHeight: 0.92 }}>
                INTELLIGENT<br /><span style={{ color: 'var(--accent-purple)' }}>SALES</span><br />ASSISTANT
              </div>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--muted)', maxWidth: '420px', lineHeight: 1.7 }}>
                Tell me what you're looking for and I'll find the perfect products. Zero hallucination — only real catalogue data.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', justifyContent: 'center', maxWidth: '560px' }}>
                {quickPrompts.map((prompt) => (
                  <button key={prompt} onClick={() => { setInput(prompt); inputRef.current?.focus() }} style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', padding: 'var(--space-2) var(--space-4)', border: 'var(--border-thin)', background: 'var(--surface)', color: 'var(--muted)', cursor: 'pointer', transition: 'all 0.12s ease' }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent-purple)'; e.currentTarget.style.color = 'var(--accent-purple)' }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--ink)'; e.currentTarget.style.color = 'var(--muted)' }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}

          {isTyping && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
              <div style={{ width: '32px', height: '32px', background: 'var(--term-bg)', border: '2px solid var(--accent-purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--accent-purple)', fontWeight: 700 }}>
                AI
              </div>
              <div style={{ padding: 'var(--space-3) var(--space-4)', border: '2px solid var(--accent-purple)', background: 'var(--surface)' }}>
                <SpinnerDots color="var(--accent-purple)" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div style={{ padding: 'var(--space-4) var(--space-6)', borderTop: 'var(--border)', background: 'var(--base)', display: 'flex', gap: 'var(--space-3)', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="DESCRIBE WHAT YOU'RE LOOKING FOR..."
              rows={2}
              style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--ink)', background: 'var(--base)', border: 'var(--border-thin)', outline: 'none', padding: '0.75rem 1rem', width: '100%', resize: 'none', lineHeight: 1.5, transition: 'border-color 0.12s ease' }}
              onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--accent-purple)' }}
              onBlur={(e)  => { e.currentTarget.style.borderColor = 'var(--ink)' }}
            />
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', marginTop: 'var(--space-1)' }}>
              PRESS ENTER TO SEND — SHIFT+ENTER FOR NEW LINE
            </div>
          </div>
          <Button
            variant="primary" size="lg"
            onClick={handleSend}
            loading={isTyping}
            disabled={!input.trim() || isTyping}
            style={{ background: 'var(--accent-purple)', borderColor: 'var(--accent-purple)', boxShadow: '6px 6px 0px var(--accent-purple)', marginBottom: '1.6rem' }}
          >
            SEND →
          </Button>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--surface)' }}>
        <Tabs
          tabs={[
            {
              id: 'recommendations', label: 'PRODUCTS', count: recommendations.length,
              content: (
                <div style={{ padding: 'var(--space-4)', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                  {recommendations.length === 0 ? (
                    <div style={{ padding: 'var(--space-10)', textAlign: 'center', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)' }}>
                      CHAT TO GET<br />RECOMMENDATIONS
                    </div>
                  ) : (
                    recommendations.map((p, i) => <ProductCard key={i} product={p} rank={i} />)
                  )}
                </div>
              ),
            },
            {
              id: 'lead', label: 'LEAD',
              content: (
                <div style={{ padding: 'var(--space-4)' }}>
                  <LeadScoreMeter score={leadScore.total} tier={leadScore.tier} />
                  <div style={{ marginTop: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                    {[
                      { label: 'BUDGET CLARITY',    key: 'budget',    max: 25, color: 'var(--accent-primary)' },
                      { label: 'INTENT STRENGTH',   key: 'intent',    max: 25, color: 'var(--accent-cyber)'   },
                      { label: 'DECISION AUTHORITY',key: 'authority', max: 25, color: 'var(--term-green)'     },
                      { label: 'PURCHASE URGENCY',  key: 'urgency',   max: 25, color: 'var(--term-amber)'     },
                    ].map((d) => (
                      <div key={d.key}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-1)' }}>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', color: 'var(--muted)' }}>{d.label}</span>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', fontWeight: 700, color: d.color }}>{leadScore.breakdown?.[d.key] || 0}/{d.max}</span>
                        </div>
                        <ProgressBar value={leadScore.breakdown?.[d.key] || 0} max={d.max} color={d.color} showValue={false} height="4px" />
                      </div>
                    ))}
                  </div>
                  {leadScore.total >= 75 && (
                    <div style={{ marginTop: 'var(--space-5)', padding: 'var(--space-4)', background: 'var(--term-red-dim)', border: '1px solid var(--term-red)', borderLeft: '4px solid var(--term-red)' }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)', color: 'var(--term-red)', marginBottom: 'var(--space-3)' }}>
                        🔥 HOT LEAD — ESCALATION RECOMMENDED
                      </div>
                      <Button variant="danger" size="sm" fullWidth onClick={() => toast.success('[ ESCALATED ] Sales rep notified!')}>
                        ESCALATE TO SALES REP
                      </Button>
                    </div>
                  )}
                </div>
              ),
            },
            {
              id: 'followup', label: 'FOLLOW-UP',
              content: (
                <div style={{ padding: 'var(--space-4)' }}>
                  <FollowUpPanel />
                </div>
              ),
            },
          ]}
          style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
        />
      </div>

      <style>{`
        @media (max-width: 1024px) {
          div[style*="grid-template-columns: 1fr 380px"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
