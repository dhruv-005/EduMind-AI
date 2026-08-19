/* ============================================================
   EDUMIND AI — SPELLING CHECKER PAGE (Challenge 3)
   OCR-powered spell detection with PDF annotation
   ============================================================ */

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useSpellingStore } from '@store/spellingStore'
import { spellingService } from '@services/spellingService'
import { ACCEPTED_DOC_TYPES, MAX_DOC_SIZE } from '@utils/constants'
import { formatBytes } from '@utils/formatters'
import { downloadBlob } from '@utils/helpers'
import Button from '@components/ui/Button'
import Badge from '@components/ui/Badge'
import ProgressBar from '@components/ui/ProgressBar'
import Spinner from '@components/ui/Spinner'
import toast from 'react-hot-toast'

/* ── PROCESSING STEPS ───────────────────────────────────────── */
const PROCESSING_STEPS = [
  { id: 'upload',    label: 'Uploading document'      },
  { id: 'ocr',       label: 'Running OCR extraction'  },
  { id: 'detect',    label: 'Detecting spelling errors'},
  { id: 'filter',    label: 'Smart filtering'          },
  { id: 'annotate',  label: 'Annotating document'     },
  { id: 'complete',  label: 'Complete'                 },
]

/* ── ERROR ROW ──────────────────────────────────────────────── */
function ErrorRow({ error, index }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(error.correction)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{
      display:        'grid',
      gridTemplateColumns: '40px 1fr 1fr 80px 100px 80px',
      alignItems:     'center',
      gap:            'var(--space-4)',
      padding:        'var(--space-4) var(--space-5)',
      borderBottom:   'var(--border-thin)',
      transition:     'background-color 0.12s ease',
    }}
      onMouseEnter={(e) =>
        (e.currentTarget.style.background = 'var(--surface)')
      }
      onMouseLeave={(e) =>
        (e.currentTarget.style.background = 'transparent')
      }
    >
      {/* Index */}
      <span style={{
        fontFamily:    'var(--font-mono)',
        fontSize:      'var(--fs-nano)',
        color:         'var(--muted)',
        textAlign:     'center',
      }}>
        {String(index + 1).padStart(2, '0')}
      </span>

      {/* Wrong word */}
      <div style={{
        display:    'flex',
        alignItems: 'center',
        gap:        'var(--space-2)',
      }}>
        <span style={{
          fontFamily:     'var(--font-mono)',
          fontSize:       'var(--fs-data)',
          color:          'var(--term-red)',
          textDecoration: 'line-through',
          fontWeight:     700,
        }}>
          {error.word}
        </span>
      </div>

      {/* Correction */}
      <div style={{
        display:    'flex',
        alignItems: 'center',
        gap:        'var(--space-2)',
      }}>
        <span style={{ color: 'var(--term-green)', fontFamily: 'var(--font-mono)', fontSize: 'var(--fs-nano)' }}>
          →
        </span>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize:   'var(--fs-data)',
          color:      'var(--term-green)',
          fontWeight: 700,
        }}>
          {error.correction}
        </span>
      </div>

      {/* Page */}
      <Badge variant="default">
        PG {error.page || 1}
      </Badge>

      {/* Confidence */}
      <div>
        <div style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          color:         (error.confidence || 1) >= 0.8
            ? 'var(--term-green)'
            : 'var(--term-amber)',
          marginBottom:  '2px',
          textAlign:     'right',
        }}>
          {Math.round((error.confidence || 1) * 100)}%
        </div>
        <ProgressBar
          value={(error.confidence || 1) * 100}
          max={100}
          color={(error.confidence || 1) >= 0.8
            ? 'var(--term-green)'
            : 'var(--term-amber)'}
          showValue={false}
          height="3px"
        />
      </div>

      {/* Copy */}
      <Button
        variant="ghost"
        size="sm"
        onClick={handleCopy}
      >
        {copied ? '✓ COPIED' : 'COPY'}
      </Button>
    </div>
  )
}

/* ── MAIN SPELLING PAGE ─────────────────────────────────────── */
export default function SpellingPage() {
  const {
    uploadedFile,
    fileType,
    isUploading,
    isProcessing,
    processingStep,
    report,
    annotatedFileUrl,
    error,
    setUploadedFile,
    setIsUploading,
    setIsProcessing,
    setProcessingStep,
    setReport,
    setAnnotatedFileUrl,
    setError,
    reset,
  } = useSpellingStore()

  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')

  /* ── DROPZONE ───────────────────────────────────────────── */
  const onDrop = useCallback(
    (accepted, rejected) => {
      if (rejected.length > 0) {
        toast.error('[ TYPE ERROR ] Only PDF, JPG, PNG accepted')
        return
      }
      if (accepted.length > 0) {
        const file = accepted[0]
        const ext  = file.name.split('.').pop().toLowerCase()
        setUploadedFile(file, ext)
        setError(null)
      }
    },
    [setUploadedFile, setError]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg':      ['.jpg', '.jpeg'],
      'image/png':       ['.png'],
    },
    maxSize:  MAX_DOC_SIZE,
    multiple: false,
  })

  /* ── PROCESS DOCUMENT ───────────────────────────────────── */
  const handleProcess = async () => {
    if (!uploadedFile) {
      toast.error('[ ERROR ] Please upload a document first')
      return
    }

    setIsProcessing(true)
    setCurrentStepIndex(0)
    setError(null)

    try {
      // Simulate step progression
      const stepInterval = setInterval(() => {
        setCurrentStepIndex((prev) => {
          const next = prev + 1
          if (next >= PROCESSING_STEPS.length - 1) {
            clearInterval(stepInterval)
          }
          return next
        })
      }, 800)

      toast.loading('[ PROCESSING ] Analyzing document...', {
        id: 'spell-toast',
      })

      const result = await spellingService.detectErrors(
        uploadedFile,
        (pct) => setUploadProgress(pct)
      )

      clearInterval(stepInterval)
      setCurrentStepIndex(PROCESSING_STEPS.length - 1)

      setReport(result)
      if (result.annotated_url) {
        setAnnotatedFileUrl(result.annotated_url)
      }

      toast.success(
        `[ COMPLETE ] ${result.errors?.length || 0} errors detected`,
        { id: 'spell-toast' }
      )
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Processing failed'
      setError(msg)
      toast.error(`[ ERROR ] ${msg}`, { id: 'spell-toast' })
    } finally {
      setIsProcessing(false)
    }
  }

  /* ── LOAD DEMO ──────────────────────────────────────────── */
  const loadDemo = () => {
    const demoReport = {
      total_words:  342,
      error_count:  7,
      error_rate:   '2.0%',
      errors: [
        { word: 'recieve',    correction: 'receive',    page: 1, confidence: 0.98, position: { x: 120, y: 340 } },
        { word: 'occured',    correction: 'occurred',   page: 1, confidence: 0.95, position: { x: 200, y: 420 } },
        { word: 'seperately', correction: 'separately', page: 2, confidence: 0.92, position: { x: 80,  y: 150 } },
        { word: 'accomodate', correction: 'accommodate',page: 2, confidence: 0.97, position: { x: 310, y: 290 } },
        { word: 'definately', correction: 'definitely', page: 3, confidence: 0.99, position: { x: 150, y: 180 } },
        { word: 'goverment',  correction: 'government', page: 3, confidence: 0.94, position: { x: 220, y: 390 } },
        { word: 'beleive',    correction: 'believe',    page: 4, confidence: 0.96, position: { x: 90,  y: 240 } },
      ],
    }
    setReport(demoReport)
    toast.success('[ DEMO ] Sample report loaded')
  }

  /* ── DOWNLOAD ANNOTATED ─────────────────────────────────── */
  const handleDownload = async () => {
    if (annotatedFileUrl) {
      window.open(annotatedFileUrl, '_blank')
    } else if (report?.report_id) {
      try {
        const blob = await spellingService.downloadAnnotated(report.report_id)
        downloadBlob(blob, `annotated_${Date.now()}.pdf`)
      } catch {
        toast.error('[ ERROR ] Download failed')
      }
    }
  }

  /* ── FILTER ERRORS ──────────────────────────────────────── */
  const filteredErrors = report?.errors?.filter((e) =>
    searchQuery
      ? e.word.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.correction.toLowerCase().includes(searchQuery.toLowerCase())
      : true
  ) || []

  /* ── RENDER ─────────────────────────────────────────────── */
  return (
    <div style={{ padding: 'var(--space-8)' }}>

      {/* ── PAGE HEADER ───────────────────────────────── */}
      <div style={{
        marginBottom:  'var(--space-8)',
        paddingBottom: 'var(--space-6)',
        borderBottom:  'var(--border)',
      }}>
        <div style={{
          fontFamily:    'var(--font-mono)',
          fontSize:      'var(--fs-nano)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-widest)',
          color:         'var(--term-amber)',
          marginBottom:  'var(--space-3)',
        }}>
          // CH-03 — OCR SPELL DETECTION
        </div>
        <div style={{
          display:        'flex',
          alignItems:     'flex-start',
          justifyContent: 'space-between',
          flexWrap:       'wrap',
          gap:            'var(--space-4)',
        }}>
          <h1 style={{
            fontFamily:    'var(--font-heading)',
            fontSize:      'var(--fs-h1)',
            fontWeight:    700,
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-tight)',
            lineHeight:    0.92,
          }}>
            SPELL<br />
            <span style={{ color: 'var(--term-amber)' }}>CHECKER</span>
          </h1>

          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
            <Button variant="ghost" size="sm" onClick={loadDemo}>
              LOAD DEMO
            </Button>
            <Button variant="ghost" size="sm" onClick={reset}>
              RESET
            </Button>
          </div>
        </div>
      </div>

      <div style={{
        display:             'grid',
        gridTemplateColumns: report ? '1fr' : '1fr 320px',
        gap:                 'var(--space-6)',
        alignItems:          'start',
      }}>

        {/* ── UPLOAD PANEL ──────────────────────────── */}
        {!report && (
          <>
            <div style={{
              background:  'var(--base)',
              border:      'var(--border)',
              boxShadow:   'var(--shadow)',
            }}>
              {/* Header */}
              <div style={{
                padding:      'var(--space-5) var(--space-6)',
                borderBottom: 'var(--border)',
                background:   'var(--surface)',
              }}>
                <span style={{
                  fontFamily:    'var(--font-heading)',
                  fontSize:      'var(--fs-h4)',
                  fontWeight:    700,
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-tight)',
                }}>
                  UPLOAD DOCUMENT
                </span>
              </div>

              <div style={{ padding: 'var(--space-6)' }}>

                {/* Drop zone */}
                <div
                  {...getRootProps()}
                  style={{
                    border:         `2px dashed ${isDragActive ? 'var(--term-amber)' : 'rgba(10,10,12,0.25)'}`,
                    background:     isDragActive
                      ? 'color-mix(in srgb, var(--term-amber) 5%, var(--surface))'
                      : 'var(--surface)',
                    padding:        'var(--space-16)',
                    display:        'flex',
                    flexDirection:  'column',
                    alignItems:     'center',
                    justifyContent: 'center',
                    gap:            'var(--space-4)',
                    cursor:         'pointer',
                    textAlign:      'center',
                    transition:     'all 0.15s ease',
                  }}
                >
                  <input {...getInputProps()} />

                  <div style={{
                    fontFamily: 'var(--font-heading)',
                    fontSize:   '3rem',
                    color:      isDragActive
                      ? 'var(--term-amber)'
                      : 'var(--muted)',
                    lineHeight: 1,
                  }}>
                    ⊕
                  </div>

                  <div>
                    <div style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-data)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wider)',
                      color:         isDragActive
                        ? 'var(--term-amber)'
                        : 'var(--ink)',
                      marginBottom:  'var(--space-2)',
                    }}>
                      {isDragActive
                        ? 'DROP DOCUMENT HERE'
                        : 'DRAG & DROP YOUR DOCUMENT'}
                    </div>
                    <div style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      color:         'var(--muted)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wide)',
                    }}>
                      PDF, JPG, PNG — MAX 20MB — ONE FILE
                    </div>
                  </div>

                  <Button variant="surface" size="sm">
                    OR BROWSE
                  </Button>
                </div>

                {/* Selected file */}
                {uploadedFile && (
                  <div style={{
                    marginTop:      'var(--space-4)',
                    padding:        'var(--space-4) var(--space-5)',
                    background:     'var(--surface)',
                    border:         'var(--border-thin)',
                    borderLeft:     '3px solid var(--term-amber)',
                    display:        'flex',
                    alignItems:     'center',
                    justifyContent: 'space-between',
                  }}>
                    <div style={{
                      display:    'flex',
                      alignItems: 'center',
                      gap:        'var(--space-3)',
                    }}>
                      <span style={{
                        fontFamily:    'var(--font-mono)',
                        fontSize:      'var(--fs-nano)',
                        color:         'var(--term-amber)',
                        textTransform: 'uppercase',
                        border:        '1px solid var(--term-amber)',
                        padding:       '0.1rem 0.4rem',
                      }}>
                        {fileType?.toUpperCase()}
                      </span>
                      <div>
                        <div style={{
                          fontFamily: 'var(--font-mono)',
                          fontSize:   'var(--fs-data)',
                          color:      'var(--ink)',
                        }}>
                          {uploadedFile.name}
                        </div>
                        <div style={{
                          fontFamily:    'var(--font-mono)',
                          fontSize:      'var(--fs-nano)',
                          color:         'var(--muted)',
                          textTransform: 'uppercase',
                        }}>
                          {formatBytes(uploadedFile.size)}
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setUploadedFile(null, null)}
                    >
                      ✕ REMOVE
                    </Button>
                  </div>
                )}

                {/* Processing steps */}
                {isProcessing && (
                  <div style={{ marginTop: 'var(--space-6)' }}>
                    <div style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wider)',
                      color:         'var(--muted)',
                      marginBottom:  'var(--space-4)',
                    }}>
                      PROCESSING PIPELINE
                    </div>

                    {PROCESSING_STEPS.map((s, i) => {
                      const isDone    = i < currentStepIndex
                      const isRunning = i === currentStepIndex
                      return (
                        <div
                          key={s.id}
                          style={{
                            display:      'flex',
                            alignItems:   'center',
                            gap:          'var(--space-3)',
                            marginBottom: 'var(--space-3)',
                          }}
                        >
                          <div style={{
                            width:        '20px',
                            height:       '20px',
                            border:       `2px solid ${isDone ? 'var(--term-green)' : isRunning ? 'var(--term-amber)' : 'var(--border-subtle)'}`,
                            display:      'flex',
                            alignItems:   'center',
                            justifyContent:'center',
                            flexShrink:   0,
                            background:   isDone ? 'var(--term-green-dim)' : 'transparent',
                          }}>
                            {isDone ? (
                              <span style={{ fontSize: '10px', color: 'var(--term-green)' }}>✓</span>
                            ) : isRunning ? (
                              <div style={{
                                width:        '8px',
                                height:       '8px',
                                background:   'var(--term-amber)',
                                borderRadius: '50%',
                                animation:    'pulseDot 1s ease-in-out infinite',
                              }} />
                            ) : null}
                          </div>
                          <span style={{
                            fontFamily:    'var(--font-mono)',
                            fontSize:      'var(--fs-nano)',
                            textTransform: 'uppercase',
                            letterSpacing: 'var(--ls-wide)',
                            color:         isDone
                              ? 'var(--term-green)'
                              : isRunning
                                ? 'var(--term-amber)'
                                : 'var(--muted)',
                          }}>
                            {s.label}
                            {isRunning && (
                              <span style={{ animation: 'blink 1s step-end infinite' }}>_</span>
                            )}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                )}

                {error && (
                  <div style={{
                    marginTop:  'var(--space-4)',
                    padding:    'var(--space-4)',
                    background: 'var(--term-red-dim)',
                    border:     '1px solid var(--term-red)',
                    borderLeft: '4px solid var(--term-red)',
                    fontFamily: 'var(--font-mono)',
                    fontSize:   'var(--fs-data)',
                    color:      'var(--term-red)',
                  }}>
                    ✕ {error}
                  </div>
                )}

                {/* Action buttons */}
                <div style={{
                  marginTop: 'var(--space-6)',
                  display:   'flex',
                  gap:       'var(--space-4)',
                  flexWrap:  'wrap',
                }}>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={handleProcess}
                    loading={isProcessing}
                    disabled={!uploadedFile || isProcessing}
                    style={{ borderColor: 'var(--term-amber)', background: 'var(--term-amber)' }}
                  >
                    {isProcessing ? 'PROCESSING...' : '▶ DETECT ERRORS'}
                  </Button>
                </div>
              </div>
            </div>

            {/* Info sidebar */}
            <div style={{
              background:  'var(--term-bg)',
              border:      '1px solid var(--term-border)',
              padding:     'var(--space-5)',
            }}>
              <div style={{
                fontFamily:    'var(--font-mono)',
                fontSize:      'var(--fs-nano)',
                textTransform: 'uppercase',
                letterSpacing: 'var(--ls-wider)',
                color:         'var(--term-green)',
                marginBottom:  'var(--space-4)',
              }}>
                DETECTION PIPELINE
              </div>

              {[
                { layer: 'L1', label: 'PySpellChecker',  detail: 'Fast initial scan'          },
                { layer: 'L2', label: 'LanguageTool',    detail: 'Context-aware grammar'      },
                { layer: 'L3', label: 'LLM Verify',      detail: 'Groq LLaMA confirmation'    },
              ].map((l) => (
                <div key={l.layer} style={{
                  padding:      'var(--space-3)',
                  border:       '1px solid var(--term-border)',
                  marginBottom: 'var(--space-2)',
                }}>
                  <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
                    <span style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      color:         'var(--accent-cyber)',
                      fontWeight:    700,
                      border:        '1px solid var(--accent-cyber)',
                      padding:       '0.1rem 0.3rem',
                    }}>
                      {l.layer}
                    </span>
                    <div>
                      <div style={{
                        fontFamily:    'var(--font-mono)',
                        fontSize:      'var(--fs-nano)',
                        color:         'rgba(255,255,255,0.7)',
                        textTransform: 'uppercase',
                        letterSpacing: 'var(--ls-wide)',
                      }}>
                        {l.label}
                      </div>
                      <div style={{
                        fontFamily:    'var(--font-mono)',
                        fontSize:      '0.6rem',
                        color:         'rgba(255,255,255,0.3)',
                        textTransform: 'uppercase',
                      }}>
                        {l.detail}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              <div style={{
                marginTop: 'var(--space-4)',
                padding:   'var(--space-3)',
                border:    '1px solid rgba(0,230,91,0.2)',
                background:'rgba(0,230,91,0.05)',
              }}>
                <div style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--term-green)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                  marginBottom:  'var(--space-2)',
                }}>
                  SMART FILTER
                </div>
                {[
                  'Skips person names (NER)',
                  'Skips abbreviations',
                  'Skips technical terms',
                  'Skips ALL CAPS words',
                ].map((f) => (
                  <div key={f} style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      '0.6rem',
                    color:         'rgba(255,255,255,0.4)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wide)',
                    marginBottom:  'var(--space-1)',
                    display:       'flex',
                    alignItems:    'center',
                    gap:           'var(--space-2)',
                  }}>
                    <span style={{ color: 'var(--term-green)' }}>✓</span>
                    {f}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ── REPORT PANEL ──────────────────────────── */}
        {report && (
          <div>
            {/* Report header */}
            <div style={{
              display:        'flex',
              alignItems:     'center',
              justifyContent: 'space-between',
              marginBottom:   'var(--space-6)',
              flexWrap:       'wrap',
              gap:            'var(--space-4)',
            }}>
              <div style={{
                display:    'flex',
                alignItems: 'center',
                gap:        'var(--space-4)',
              }}>
                <Badge variant="green" dot>
                  ANALYSIS COMPLETE
                </Badge>
                <Badge variant="red">
                  {report.error_count || report.errors?.length || 0} ERRORS
                </Badge>
                <span style={{
                  fontFamily:    'var(--font-mono)',
                  fontSize:      'var(--fs-nano)',
                  color:         'var(--muted)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-wide)',
                }}>
                  ERROR RATE: {report.error_rate || '0%'}
                </span>
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleDownload}
                  style={{ background: 'var(--term-amber)', borderColor: 'var(--term-amber)' }}
                >
                  ↓ DOWNLOAD ANNOTATED
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={reset}
                >
                  ← NEW DOCUMENT
                </Button>
              </div>
            </div>

            {/* Summary stats */}
            <div style={{
              display:             'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap:                 'var(--space-4)',
              marginBottom:        'var(--space-6)',
            }}>
              {[
                { label: 'TOTAL WORDS',   value: report.total_words || 0,                             color: 'var(--accent-cyber)'   },
                { label: 'ERRORS FOUND',  value: report.errors?.length || 0,                          color: 'var(--term-red)'       },
                { label: 'ERROR RATE',    value: report.error_rate || '0%',                           color: 'var(--term-amber)'     },
                { label: 'PAGES SCANNED', value: [...new Set(report.errors?.map((e) => e.page) || [])].length || 1, color: 'var(--term-green)' },
              ].map((s) => (
                <div key={s.label} style={{
                  background:  'var(--base)',
                  border:      'var(--border)',
                  boxShadow:   'var(--shadow-sm)',
                  padding:     'var(--space-5)',
                }}>
                  <div style={{
                    fontFamily:    'var(--font-heading)',
                    fontSize:      'var(--fs-h2)',
                    fontWeight:    700,
                    letterSpacing: 'var(--ls-tight)',
                    color:         s.color,
                    lineHeight:    1,
                    marginBottom:  'var(--space-1)',
                  }}>
                    {s.value}
                  </div>
                  <div style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wider)',
                    color:         'var(--muted)',
                  }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>

            {/* Error list */}
            <div style={{
              background:  'var(--base)',
              border:      'var(--border)',
              boxShadow:   'var(--shadow)',
            }}>
              {/* Table header */}
              <div style={{
                display:        'flex',
                alignItems:     'center',
                justifyContent: 'space-between',
                padding:        'var(--space-5) var(--space-6)',
                borderBottom:   'var(--border)',
                background:     'var(--surface)',
                flexWrap:       'wrap',
                gap:            'var(--space-4)',
              }}>
                <span style={{
                  fontFamily:    'var(--font-heading)',
                  fontSize:      'var(--fs-h4)',
                  fontWeight:    700,
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--ls-tight)',
                }}>
                  ERROR LOG
                </span>

                {/* Search */}
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    placeholder="SEARCH ERRORS..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      fontFamily:    'var(--font-mono)',
                      fontSize:      'var(--fs-nano)',
                      textTransform: 'uppercase',
                      letterSpacing: 'var(--ls-wide)',
                      color:         'var(--ink)',
                      background:    'var(--base)',
                      border:        'var(--border-thin)',
                      outline:       'none',
                      padding:       '0.45rem 0.9rem',
                      width:         '220px',
                    }}
                  />
                </div>
              </div>

              {/* Column headers */}
              <div style={{
                display:             'grid',
                gridTemplateColumns: '40px 1fr 1fr 80px 100px 80px',
                gap:                 'var(--space-4)',
                padding:             'var(--space-3) var(--space-5)',
                borderBottom:        'var(--border)',
                background:          'var(--surface)',
              }}>
                {['#', 'WRONG WORD', 'CORRECTION', 'PAGE', 'CONFIDENCE', 'ACTION'].map((h) => (
                  <span key={h} style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      'var(--fs-nano)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--ls-wider)',
                    color:         'var(--muted)',
                  }}>
                    {h}
                  </span>
                ))}
              </div>

              {/* Error rows */}
              {filteredErrors.length > 0 ? (
                filteredErrors.map((err, i) => (
                  <ErrorRow key={i} error={err} index={i} />
                ))
              ) : (
                <div style={{
                  padding:    'var(--space-12)',
                  textAlign:  'center',
                  fontFamily: 'var(--font-mono)',
                  fontSize:   'var(--fs-data)',
                  color:      'var(--muted)',
                  textTransform:'uppercase',
                  letterSpacing:'var(--ls-wider)',
                }}>
                  {searchQuery ? 'NO MATCHING ERRORS' : 'NO ERRORS DETECTED'}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Responsive */}
      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns: 1fr 320px"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          div[style*="grid-template-columns: 40px 1fr 1fr 80px 100px 80px"] {
            grid-template-columns: 40px 1fr 1fr !important;
          }
        }
      `}</style>
    </div>
  )
}
