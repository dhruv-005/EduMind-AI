/* ============================================================
   EDUMIND AI — QUESTION GENERATOR PAGE (Challenge 2)
   ============================================================ */

import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useGeneratorStore } from '@store/generatorStore'
import { generatorService } from '@services/generatorService'
import { SUBJECTS, GRADE_LEVELS, DIFFICULTY_LEVELS, QUESTION_TYPES, MAX_DOC_SIZE } from '@utils/constants'
import { formatBytes, downloadBlob } from '@utils/formatters'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'
import toast from 'react-hot-toast'

/* ── PARSE HELPER ───────────────────────────────────────────── */
function parseList(val) {
  if (Array.isArray(val)) return val
  if (typeof val === 'string') {
    try { return JSON.parse(val) } catch { return [] }
  }
  return []
}

/* ── QUESTION CARD ──────────────────────────────────────────── */
function QuestionCard({ question, index, onRemove }) {
  const [showAnswer, setShowAnswer] = useState(false)

  const diffColors = {
    easy: 'var(--term-green)', medium: 'var(--term-amber)',
    hard: 'var(--term-red)', default: 'var(--muted)',
  }

  const questionText = question.question_text || question.question || ''
  const questionType = question.question_type || question.type || 'short'
  const difficulty   = question.difficulty || 'medium'
  const marks        = question.marks || 5
  const topic        = question.topic || ''
  const answer       = question.model_answer || question.answer || ''
  const options      = parseList(question.options || [])
  const correctOpt   = question.correct_option

  return (
    <div style={{
      background: 'var(--base)', border: 'var(--border)', boxShadow: 'var(--shadow-sm)',
      marginBottom: 'var(--space-4)',
    }}>
      {/* Card header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: 'var(--space-3) var(--space-5)', borderBottom: 'var(--border-thin)',
        background: 'var(--surface)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <span style={{
            fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
            color: 'var(--accent-primary)', fontWeight: 700,
          }}>
            Q{String(index + 1).padStart(2, '0')}
          </span>
          <Badge variant="default">{questionType.toUpperCase()}</Badge>
          <span style={{
            fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
            textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
            color: diffColors[difficulty] || diffColors.default,
            border: `1px solid ${diffColors[difficulty] || diffColors.default}`,
            padding: '0.1rem 0.4rem',
          }}>
            {difficulty}
          </span>
          <span style={{
            fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
            textTransform: 'uppercase', color: 'var(--muted)',
          }}>
            [{marks} MARKS]
          </span>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <Button variant="ghost" size="sm" onClick={() => setShowAnswer(!showAnswer)}>
            {showAnswer ? 'HIDE ANS' : 'SHOW ANS'}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onRemove(index)}>✕</Button>
        </div>
      </div>

      {/* Question body */}
      <div style={{ padding: 'var(--space-5)' }}>
        <p style={{
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
          color: 'var(--ink)', lineHeight: 1.7,
          marginBottom: options.length > 0 ? 'var(--space-4)' : 0,
          whiteSpace: 'pre-wrap',
        }}>
          {questionText}
        </p>

        {/* MCQ Options */}
        {options.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginLeft: 'var(--space-4)' }}>
            {options.map((opt, i) => (
              <div key={i} style={{
                display: 'flex', gap: 'var(--space-3)',
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
                color: showAnswer && (correctOpt === i || correctOpt === String.fromCharCode(65 + i) || correctOpt === opt)
                  ? 'var(--term-green)' : 'var(--muted)',
              }}>
                <span style={{ fontWeight: 700, flexShrink: 0 }}>
                  {String.fromCharCode(65 + i)}.
                </span>
                <span>{opt}</span>
                {showAnswer && (correctOpt === i || correctOpt === String.fromCharCode(65 + i)) && (
                  <span style={{ color: 'var(--term-green)', marginLeft: 'auto' }}>✓ CORRECT</span>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Answer */}
        {showAnswer && answer && (
          <div style={{
            marginTop: 'var(--space-4)', padding: 'var(--space-4)',
            background: 'var(--term-green-dim)', border: '1px solid var(--term-green)',
            borderLeft: '4px solid var(--term-green)',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
              textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
              color: 'var(--term-green)', marginBottom: 'var(--space-2)',
            }}>
              MODEL ANSWER
            </div>
            <p style={{
              fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
              color: 'var(--ink)', lineHeight: 1.6, whiteSpace: 'pre-wrap',
            }}>
              {answer.length > 500 ? answer.slice(0, 500) + '...' : answer}
            </p>
          </div>
        )}

        {topic && (
          <div style={{ marginTop: 'var(--space-3)' }}>
            <Badge variant="default">{topic}</Badge>
          </div>
        )}
      </div>
    </div>
  )
}

/* ── EXPORT PDF ─────────────────────────────────────────────── */
async function exportToPDF(questions, config) {
  try {
    // Try backend PDF export first
    const blob = await generatorService.exportPDF(questions, config)
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `edumind_paper_${Date.now()}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    return true
  } catch {
    return false
  }
}

function generateHTMLPDF(questions, config) {
  const content = questions.map((q, i) => {
    const text    = q.question_text || q.question || ''
    const type    = q.question_type || q.type || 'short'
    const marks   = q.marks || 5
    const options = parseList(q.options || [])
    const answer  = q.model_answer || q.answer || ''
    const topic   = q.topic || ''

    let optionsHTML = ''
    if (options.length > 0) {
      optionsHTML = options.map((o, j) =>
        `<div style="margin:4px 0 4px 20px">${String.fromCharCode(65+j)}. ${o}</div>`
      ).join('')
    }

    return `
      <div style="margin-bottom:24px;padding:16px;border:1px solid #e5e7eb;page-break-inside:avoid">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px">
          <strong>Q${i+1}. [${type.toUpperCase()}]${topic ? ' — ' + topic : ''}</strong>
          <span>[${marks} marks]</span>
        </div>
        <p style="margin:8px 0;white-space:pre-wrap">${text}</p>
        ${optionsHTML}
        <div style="margin-top:16px;padding:8px;background:#f0fdf4;border-left:3px solid #22c55e">
          <strong>Answer:</strong><br/>
          <span style="white-space:pre-wrap">${answer.slice(0, 300)}${answer.length > 300 ? '...' : ''}</span>
        </div>
      </div>
    `
  }).join('')

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>EduMind AI — Question Paper</title>
      <style>
        body { font-family: 'Courier New', monospace; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; border-bottom: 3px solid #000; padding-bottom: 10px; }
        .meta { display: flex; justify-content: space-between; margin: 10px 0 20px; font-size: 12px; }
      </style>
    </head>
    <body>
      <h1>EDUMIND AI — QUESTION PAPER</h1>
      <div class="meta">
        <span>Subject: ${config.subject?.toUpperCase()}</span>
        <span>Level: ${config.level?.toUpperCase()}</span>
        <span>Difficulty: ${config.difficulty?.toUpperCase()}</span>
        <span>Total Questions: ${questions.length}</span>
        <span>Generated: ${new Date().toLocaleDateString()}</span>
      </div>
      ${content}
    </body>
    </html>
  `

  const blob = new Blob([html], { type: 'text/html' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `edumind_paper_${Date.now()}.html`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/* ── CONFIG FORM ────────────────────────────────────────────── */
function ConfigForm({ config, onChange }) {
  const selectStyle = {
    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)',
    textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
    color: 'var(--ink)', background: 'var(--base)',
    border: 'var(--border-thin)', outline: 'none',
    padding: '0.65rem 2rem 0.65rem 0.85rem', width: '100%',
    cursor: 'pointer', appearance: 'none',
  }
  const labelStyle = {
    fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
    textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
    color: 'var(--muted)', display: 'block', marginBottom: 'var(--space-2)',
  }
  const wrap = (child) => (
    <div style={{ position: 'relative' }}>
      {child}
      <span style={{
        position: 'absolute', right: '0.8rem', top: '50%',
        transform: 'translateY(-50%)', pointerEvents: 'none',
        fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)',
      }}>▼</span>
    </div>
  )

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--space-5)' }}>
      <div>
        <label style={labelStyle}>SUBJECT</label>
        {wrap(<select value={config.subject} onChange={e => onChange({subject: e.target.value})} style={selectStyle}>
          {SUBJECTS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>)}
      </div>
      <div>
        <label style={labelStyle}>GRADE / LEVEL</label>
        {wrap(<select value={config.level} onChange={e => onChange({level: e.target.value})} style={selectStyle}>
          {GRADE_LEVELS.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
        </select>)}
      </div>
      <div>
        <label style={labelStyle}>TOPIC (OPTIONAL)</label>
        <input
          type="text" placeholder="e.g. Algebra, Photosynthesis..."
          value={config.topic}
          onChange={e => onChange({topic: e.target.value})}
          style={{ ...selectStyle, padding: '0.65rem 0.85rem' }}
        />
      </div>
      <div>
        <label style={labelStyle}>NUMBER OF QUESTIONS: {config.numQuestions}</label>
        <input
          type="range" min={1} max={20} value={config.numQuestions}
          onChange={e => onChange({numQuestions: Number(e.target.value)})}
          style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--accent-primary)' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', marginTop: 'var(--space-1)' }}>
          <span>1</span><span>20</span>
        </div>
      </div>
      <div>
        <label style={labelStyle}>DIFFICULTY</label>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          {DIFFICULTY_LEVELS.map(d => {
            const colors = { easy: 'var(--term-green)', medium: 'var(--term-amber)', hard: 'var(--term-red)', mixed: 'var(--accent-cyber)' }
            const isActive = config.difficulty === d.value
            return (
              <button key={d.value} onClick={() => onChange({difficulty: d.value})} style={{
                flex: 1, fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
                padding: 'var(--space-2)',
                border: isActive ? `2px solid ${colors[d.value]}` : 'var(--border-thin)',
                background: isActive ? `color-mix(in srgb, ${colors[d.value]} 12%, transparent)` : 'var(--surface)',
                color: isActive ? colors[d.value] : 'var(--muted)',
                cursor: 'pointer', transition: 'all 0.12s ease',
              }}>{d.label}</button>
            )
          })}
        </div>
      </div>
      <div>
        <label style={labelStyle}>QUESTION TYPE</label>
        {wrap(<select value={config.questionType} onChange={e => onChange({questionType: e.target.value})} style={selectStyle}>
          {QUESTION_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>)}
      </div>
    </div>
  )
}

/* ── MAIN PAGE ──────────────────────────────────────────────── */
export default function GeneratorPage() {
  const {
    uploadedFiles, isUploading, uploadProgress, patternAnalysis, isAnalyzing,
    config, generatedQuestions, isGenerating, isExporting, error,
    setUploadedFiles, setIsUploading, setUploadProgress, setPatternAnalysis,
    setIsAnalyzing, setIsGenerating, setIsExporting, setGeneratedQuestions,
    removeQuestion, updateConfig, setError, reset,
  } = useGeneratorStore()

  const [step, setStep] = useState(1)

  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length > 0) { toast.error('[ TYPE ERROR ] Only PDF, DOCX, JPG, PNG accepted'); return }
    setUploadedFiles([...uploadedFiles, ...accepted])
  }, [uploadedFiles, setUploadedFiles])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] },
    maxSize: MAX_DOC_SIZE, multiple: true,
  })

  const handleAnalyze = async () => {
    if (uploadedFiles.length === 0) { toast.error('[ ERROR ] Upload at least one paper'); return }
    setIsUploading(true)
    try {
      toast.loading('[ UPLOADING ] Processing papers...', { id: 'gen-upload' })
      const uploadResult = await generatorService.uploadPapers(uploadedFiles, pct => setUploadProgress(pct))
      setIsUploading(false)
      setIsAnalyzing(true)
      toast.loading('[ ANALYZING ] Extracting patterns...', { id: 'gen-upload' })
      const analysis = await generatorService.analyzePapers(uploadResult.upload_id || uploadResult.data?.upload_id)
      setPatternAnalysis(analysis.data || analysis)
      setStep(2)
      toast.success('[ COMPLETE ] Pattern analysis done', { id: 'gen-upload' })
    } catch (err) {
      toast.error(`[ ERROR ] ${err.message}`, { id: 'gen-upload' })
      setStep(2)
    } finally {
      setIsUploading(false); setIsAnalyzing(false)
    }
  }

  const handleGenerate = async () => {
    setIsGenerating(true); setError(null)
    try {
      toast.loading(`[ GENERATING ] Creating ${config.numQuestions} questions...`, { id: 'gen-toast', duration: 120000 })

      const payload = {
        subject:       config.subject,
        level:         config.level,
        topic:         config.topic,
        num_questions: config.numQuestions,
        difficulty:    config.difficulty,
        question_type: config.questionType,
      }

      const response = await generatorService.generateQuestions(payload)
      const data     = response?.data || response || {}

      // Extract questions from various response formats
      let questions = data.questions || data.items || data.generated_questions || []

      // If questions is empty but response has data, log it
      if (questions.length === 0) {
        console.log('Generator response:', JSON.stringify(response, null, 2))
        toast.error('[ WARN ] No questions in response — check console', { id: 'gen-toast' })
      } else {
        setGeneratedQuestions(questions)
        setStep(3)
        toast.success(`[ COMPLETE ] ${questions.length} questions generated!`, { id: 'gen-toast' })
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Generation failed'
      setError(msg)
      toast.error(`[ ERROR ] ${msg}`, { id: 'gen-toast' })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleExport = async () => {
    if (generatedQuestions.length === 0) return
    setIsExporting(true)
    toast.loading('[ EXPORTING ] Generating document...', { id: 'export' })
    try {
      const success = await exportToPDF(generatedQuestions, config)
      if (!success) {
        // Fallback to HTML export
        generateHTMLPDF(generatedQuestions, config)
        toast.success('[ EXPORTED ] Downloaded as HTML (open in browser to print as PDF)', { id: 'export' })
      } else {
        toast.success('[ EXPORTED ] PDF downloaded!', { id: 'export' })
      }
    } catch (err) {
      generateHTMLPDF(generatedQuestions, config)
      toast.success('[ EXPORTED ] Downloaded as HTML document', { id: 'export' })
    } finally {
      setIsExporting(false)
    }
  }

  const loadDemoQuestions = () => {
    const demo = [
      {
        question_text: 'Which of the following is the primary product of photosynthesis?\nA) Oxygen\nB) Glucose\nC) Carbon dioxide\nD) Water',
        question_type: 'mcq', difficulty: 'easy', marks: 2,
        topic: 'Photosynthesis',
        options: ['Oxygen', 'Glucose', 'Carbon dioxide', 'Water'],
        correct_option: 1,
        model_answer: 'B) Glucose. During photosynthesis, plants convert CO₂ and water into glucose using sunlight energy. Oxygen is released as a byproduct.',
      },
      {
        question_text: 'Explain the process of photosynthesis and write the balanced chemical equation.',
        question_type: 'short', difficulty: 'medium', marks: 5,
        topic: 'Photosynthesis',
        model_answer: '6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂\n\nPhotosynthesis occurs in chloroplasts. Light reactions occur in thylakoids producing ATP and NADPH. Calvin cycle in stroma uses these to fix CO₂ into glucose.',
      },
      {
        question_text: 'Solve for x: 2x² + 5x - 3 = 0. Show all working.',
        question_type: 'numerical', difficulty: 'medium', marks: 4,
        topic: 'Quadratic Equations',
        model_answer: 'Using quadratic formula: x = (-5 ± √(25 + 24)) / 4 = (-5 ± 7) / 4\nx = 0.5 or x = -3',
      },
    ]
    setGeneratedQuestions(demo)
    setStep(3)
    toast.success('[ DEMO ] Sample questions loaded')
  }

  return (
    <div style={{ padding: 'var(--space-8)' }}>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-8)', paddingBottom: 'var(--space-6)', borderBottom: 'var(--border)' }}>
        <div style={{
          fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
          textTransform: 'uppercase', letterSpacing: 'var(--ls-widest)',
          color: 'var(--accent-cyber)', marginBottom: 'var(--space-3)',
        }}>
          // CH-02 — NEURAL QUESTION FORGE
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <h1 style={{
            fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h1)',
            fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)', lineHeight: 0.92,
          }}>
            QUESTION<br/><span style={{ color: 'var(--accent-cyber)' }}>GENERATOR</span>
          </h1>
          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
            <Button variant="ghost" size="sm" onClick={loadDemoQuestions}>LOAD DEMO</Button>
            <Button variant="ghost" size="sm" onClick={() => { reset(); setStep(1) }}>RESET</Button>
          </div>
        </div>
      </div>

      {/* Step indicator */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-2)', marginBottom: 'var(--space-8)' }}>
        {[
          { num: '01', label: 'UPLOAD PAPERS' },
          { num: '02', label: 'CONFIGURE'     },
          { num: '03', label: 'RESULTS'       },
        ].map((s, i) => {
          const stepNum = i + 1
          const isActive = step === stepNum
          const isDone   = step > stepNum
          return (
            <div key={s.num} style={{
              padding: 'var(--space-4)',
              border: isActive ? '3px solid var(--accent-cyber)' : isDone ? '3px solid var(--term-green)' : 'var(--border)',
              background: isActive ? 'color-mix(in srgb, var(--accent-cyber) 8%, var(--base))' : 'var(--surface)',
              boxShadow: isActive ? '4px 4px 0px var(--accent-cyber)' : isDone ? '4px 4px 0px var(--term-green)' : 'var(--shadow-sm)',
            }}>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
                textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)',
                color: isActive ? 'var(--accent-cyber)' : isDone ? 'var(--term-green)' : 'var(--muted)',
                marginBottom: 'var(--space-1)',
              }}>
                {isDone ? '✓ DONE' : `STEP ${s.num}`}
              </div>
              <div style={{
                fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)',
                fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)',
                color: isActive ? 'var(--accent-cyber)' : isDone ? 'var(--term-green)' : 'var(--muted)',
              }}>
                {s.label}
              </div>
            </div>
          )
        })}
      </div>

      {/* STEP 1 — UPLOAD */}
      {step === 1 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 'var(--space-6)', alignItems: 'start' }}>
          <div style={{ background: 'var(--base)', border: 'var(--border)', boxShadow: 'var(--shadow)' }}>
            <div style={{ padding: 'var(--space-5) var(--space-6)', borderBottom: 'var(--border)', background: 'var(--surface)' }}>
              <span style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)' }}>
                UPLOAD PAST PAPERS
              </span>
            </div>
            <div style={{ padding: 'var(--space-6)' }}>
              <div {...getRootProps()} style={{
                border: `2px dashed ${isDragActive ? 'var(--accent-cyber)' : 'rgba(10,10,12,0.25)'}`,
                background: isDragActive ? 'color-mix(in srgb, var(--accent-cyber) 5%, var(--surface))' : 'var(--surface)',
                padding: 'var(--space-12)', display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', gap: 'var(--space-4)',
                cursor: 'pointer', textAlign: 'center', transition: 'all 0.15s ease',
              }}>
                <input {...getInputProps()} />
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: '3rem', color: isDragActive ? 'var(--accent-cyber)' : 'var(--muted)', lineHeight: 1 }}>↑</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: isDragActive ? 'var(--accent-cyber)' : 'var(--ink)', marginBottom: 'var(--space-2)' }}>
                  {isDragActive ? 'DROP FILES HERE' : 'DRAG & DROP PAST PAPERS'}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)' }}>
                  PDF, DOCX, JPG, PNG — MAX 20MB
                </div>
                <Button variant="surface" size="sm">OR BROWSE FILES</Button>
              </div>

              {uploadedFiles.length > 0 && (
                <div style={{ marginTop: 'var(--space-4)', border: 'var(--border)', background: 'var(--base)' }}>
                  {uploadedFiles.map((file, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: 'var(--space-3) var(--space-5)',
                      borderBottom: i < uploadedFiles.length - 1 ? 'var(--border-thin)' : 'none',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--accent-primary)', border: '1px solid var(--accent-primary)', padding: '0.1rem 0.4rem' }}>
                          {file.name.split('.').pop().toUpperCase()}
                        </span>
                        <div>
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--ink)' }}>{file.name}</div>
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--muted)', textTransform: 'uppercase' }}>{formatBytes(file.size)}</div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => setUploadedFiles(uploadedFiles.filter((_, j) => j !== i))}>✕</Button>
                    </div>
                  ))}
                </div>
              )}

              {(isUploading || isAnalyzing) && (
                <div style={{ marginTop: 'var(--space-6)' }}>
                  <ProgressBar value={isAnalyzing ? 100 : uploadProgress} max={100} label={isAnalyzing ? 'ANALYZING PATTERNS' : 'UPLOADING FILES'} color="var(--accent-cyber)" />
                </div>
              )}

              <div style={{ marginTop: 'var(--space-6)', display: 'flex', gap: 'var(--space-4)' }}>
                <Button variant="cyber" size="lg" onClick={handleAnalyze} loading={isUploading || isAnalyzing} disabled={uploadedFiles.length === 0 || isUploading || isAnalyzing}>
                  {isAnalyzing ? 'ANALYZING...' : isUploading ? 'UPLOADING...' : '▶ ANALYZE PAPERS'}
                </Button>
                <Button variant="ghost" size="lg" onClick={() => setStep(2)}>SKIP (NO PAPERS)</Button>
              </div>
            </div>
          </div>

          <div style={{ background: 'var(--term-bg)', border: '1px solid var(--term-border)', padding: 'var(--space-5)' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)', color: 'var(--term-green)', marginBottom: 'var(--space-4)' }}>
              SUPPORTED FORMATS
            </div>
            {[['PDF', 'Text + scanned OCR'], ['DOCX', 'Word documents'], ['JPG', 'JPEG images'], ['PNG', 'PNG scanned papers']].map(([ext, desc]) => (
              <div key={ext} style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-3)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--accent-cyber)', border: '1px solid var(--accent-cyber)', padding: '0.1rem 0.4rem', flexShrink: 0 }}>{ext}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)' }}>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* STEP 2 — CONFIGURE */}
      {step === 2 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <div style={{ background: 'var(--base)', border: 'var(--border)', boxShadow: 'var(--shadow)' }}>
            <div style={{ padding: 'var(--space-5) var(--space-6)', borderBottom: 'var(--border)', background: 'var(--surface)' }}>
              <span style={{ fontFamily: 'var(--font-heading)', fontSize: 'var(--fs-h4)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 'var(--ls-tight)' }}>
                GENERATION CONFIGURATION
              </span>
            </div>
            <div style={{ padding: 'var(--space-6)' }}>
              <ConfigForm config={config} onChange={updateConfig} />
              <div style={{ marginTop: 'var(--space-6)', paddingTop: 'var(--space-5)', borderTop: 'var(--border-thin)', display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                <Button variant="cyber" size="lg" onClick={handleGenerate} loading={isGenerating} disabled={isGenerating}>
                  {isGenerating ? 'GENERATING... (please wait)' : `▶ GENERATE ${config.numQuestions} QUESTIONS`}
                </Button>
                <Button variant="ghost" size="lg" onClick={() => setStep(1)}>← BACK</Button>
              </div>
              {isGenerating && (
                <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-3)', background: 'var(--surface)', border: '1px solid var(--accent-cyber)', borderLeft: '4px solid var(--accent-cyber)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)', color: 'var(--accent-cyber)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)' }}>
                  ● LLM IS GENERATING QUESTIONS... MAY TAKE 10-30 SECONDS
                </div>
              )}
              {error && (
                <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-4)', background: 'var(--term-red-dim)', border: '1px solid var(--term-red)', borderLeft: '4px solid var(--term-red)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--term-red)' }}>
                  ✕ {error}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* STEP 3 — RESULTS */}
      {step === 3 && (
        <div>
          {/* Results header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-6)', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
              <Badge variant="green" dot pulse>{generatedQuestions.length} QUESTIONS GENERATED</Badge>
              <Badge variant="default">{config.subject.toUpperCase()}</Badge>
              <Badge variant="default">{config.difficulty.toUpperCase()}</Badge>
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
              <Button
                variant="primary" size="sm"
                onClick={handleExport}
                loading={isExporting}
                disabled={isExporting || generatedQuestions.length === 0}
              >
                ↓ DOWNLOAD PAPER (HTML/PDF)
              </Button>
              <Button variant="surface" size="sm" onClick={() => setStep(2)}>← RECONFIGURE</Button>
              <Button variant="ghost" size="sm" onClick={() => { reset(); setStep(1) }}>NEW PAPER</Button>
            </div>
          </div>

          {/* Export note */}
          <div style={{
            marginBottom: 'var(--space-4)', padding: 'var(--space-3)',
            background: 'var(--term-green-dim)', border: '1px solid var(--term-green)',
            fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)',
            color: 'var(--term-green)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wide)',
          }}>
            💡 TIP: Click "DOWNLOAD PAPER" to get HTML file. Open in browser → Ctrl+P → Save as PDF for formatted paper.
          </div>

          {/* Questions list */}
          {generatedQuestions.length > 0 ? (
            generatedQuestions.map((q, i) => (
              <QuestionCard key={i} question={q} index={i} onRemove={removeQuestion} />
            ))
          ) : (
            <div style={{
              padding: 'var(--space-16)', textAlign: 'center',
              border: 'var(--border-dashed)', background: 'var(--surface)',
            }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-data)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: 'var(--ls-wider)' }}>
                NO QUESTIONS TO DISPLAY
              </div>
              <Button variant="cyber" style={{ marginTop: 'var(--space-4)' }} onClick={() => setStep(2)}>
                ← GO BACK AND GENERATE
              </Button>
            </div>
          )}
        </div>
      )}

      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns: 1fr 280px"] { grid-template-columns: 1fr !important; }
          div[style*="repeat(2, 1fr)"] { grid-template-columns: 1fr !important; }
          div[style*="repeat(3, 1fr)"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
