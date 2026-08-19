import React, { useState } from 'react'
import { FiSend, FiRefreshCw, FiArrowRight, FiZap } from 'react-icons/fi'
import Input, { Textarea, Select } from '@components/ui/Input'
import { SUBJECTS, GRADE_LEVELS } from '@utils/constants'
import { validateEvaluationForm } from '@utils/validators'
import { showError } from '@components/ui/Toast'

const DEFAULT = { question:'', reference_answer:'', student_answer:'', subject:'general', grade_level:'', max_score:'10', strict_mode:false }

export default function EvaluationForm({ onSubmit, isLoading }) {
  const [form, setForm]     = useState(DEFAULT)
  const [errors, setErrors] = useState({})

  const set = f => e => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm(p => ({ ...p, [f]: val }))
    setErrors(p => ({ ...p, [f]: null }))
  }

  const handleSubmit = async e => {
    e.preventDefault()
    const { valid, errors: errs } = validateEvaluationForm(form)
    if (!valid) { setErrors(errs); showError('Please fix the form errors'); return }
    await onSubmit({ ...form, max_score: parseFloat(form.max_score) || 10 })
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Select label="Subject" value={form.subject} onChange={set('subject')}
          options={SUBJECTS.map(s => ({ value: s.id, label: `${s.icon} ${s.name}` }))} required />
        <Select label="Grade Level" value={form.grade_level} onChange={set('grade_level')}
          options={GRADE_LEVELS.map(g => ({ value: g, label: g }))} placeholder="Optional" />
      </div>

      <Textarea label="Question" placeholder="Enter the exam question…"
        value={form.question} onChange={set('question')} error={errors.question} rows={3} required />
      <Textarea label="Reference Answer" placeholder="Enter the correct model answer…"
        value={form.reference_answer} onChange={set('reference_answer')} error={errors.reference_answer} rows={4} required />
      <Textarea label="Student Answer" placeholder="Enter the student's answer to evaluate…"
        value={form.student_answer} onChange={set('student_answer')} error={errors.student_answer} rows={4} required />

      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 18, flexWrap: 'wrap' }}>
        <div style={{ width: 120 }}>
          <Input label="Max Score" type="number" min="1" max="100" value={form.max_score} onChange={set('max_score')} />
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', paddingBottom: 8 }}>
          <div style={{ position: 'relative', width: 20, height: 20 }}>
            <input type="checkbox" checked={form.strict_mode} onChange={set('strict_mode')}
              style={{ width: 18, height: 18, cursor: 'pointer', accentColor: '#6366f1' }} />
          </div>
          <span style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', fontSize: 13, fontWeight: 600, color: 'var(--ink-soft)' }}>
            Strict Mode
          </span>
        </label>
      </div>

      <div style={{ height: 1, background: 'linear-gradient(90deg, transparent, var(--border), transparent)' }} />

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <button type="submit" disabled={isLoading} className="btn-primary"
          style={{ flex: 1, minWidth: 180, justifyContent: 'center', gap: 10, opacity: isLoading ? 0.8 : 1 }}>
          {isLoading ? (
            <>
              <div style={{ width: 16, height: 16, border: '2.5px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
              Evaluating…
            </>
          ) : (
            <>
              <FiZap size={16} strokeWidth={2} />
              Evaluate Answer
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 26, height: 26, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', flexShrink: 0 }}>
                <FiArrowRight size={13} strokeWidth={2.5} />
              </div>
            </>
          )}
        </button>
        <button type="button" onClick={() => { setForm(DEFAULT); setErrors({}) }} className="btn-secondary" style={{ gap: 8 }}>
          <FiRefreshCw size={14} strokeWidth={1.5} /> Reset
        </button>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </form>
  )
}
