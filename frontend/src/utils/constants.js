/* ============================================================
   EDUMIND AI — GLOBAL CONSTANTS
   ============================================================ */

// API
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_BASE  = import.meta.env.VITE_WS_BASE_URL  || 'ws://localhost:8000'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '2.0.0'

// Subjects
export const SUBJECTS = [
  { value: 'mathematics', label: 'Mathematics' },
  { value: 'science',     label: 'Science'      },
  { value: 'english',     label: 'English'      },
  { value: 'general',     label: 'General'      },
  { value: 'history',     label: 'History'      },
  { value: 'geography',   label: 'Geography'    },
  { value: 'physics',     label: 'Physics'      },
  { value: 'chemistry',   label: 'Chemistry'    },
  { value: 'biology',     label: 'Biology'      },
  { value: 'computer_science', label: 'CS'      },
]

// Grade Levels
export const GRADE_LEVELS = [
  { value: 'grade-1',         label: 'Grade 1'        },
  { value: 'grade-2',         label: 'Grade 2'        },
  { value: 'grade-3',         label: 'Grade 3'        },
  { value: 'grade-4',         label: 'Grade 4'        },
  { value: 'grade-5',         label: 'Grade 5'        },
  { value: 'grade-6',         label: 'Grade 6'        },
  { value: 'grade-7',         label: 'Grade 7'        },
  { value: 'grade-8',         label: 'Grade 8'        },
  { value: 'grade-9',         label: 'Grade 9'        },
  { value: 'grade-10',        label: 'Grade 10'       },
  { value: 'grade-11',        label: 'Grade 11'       },
  { value: 'grade-12',        label: 'Grade 12'       },
  { value: 'undergraduate',   label: 'Undergraduate'  },
  { value: 'postgraduate',    label: 'Postgraduate'   },
]

// Difficulty Levels
export const DIFFICULTY_LEVELS = [
  { value: 'easy',   label: 'Easy'   },
  { value: 'medium', label: 'Medium' },
  { value: 'hard',   label: 'Hard'   },
  { value: 'mixed',  label: 'Mixed'  },
]

// Question Types
export const QUESTION_TYPES = [
  { value: 'mcq',       label: 'MCQ'           },
  { value: 'short',     label: 'Short Answer'  },
  { value: 'long',      label: 'Long Answer'   },
  { value: 'numerical', label: 'Numerical'     },
  { value: 'mixed',     label: 'Mixed'         },
]

// Score Grades
export const GRADE_THRESHOLDS = [
  { min: 9,  max: 10, grade: 'A+', label: 'Outstanding'  },
  { min: 8,  max: 9,  grade: 'A',  label: 'Excellent'    },
  { min: 7,  max: 8,  grade: 'B+', label: 'Very Good'    },
  { min: 6,  max: 7,  grade: 'B',  label: 'Good'         },
  { min: 5,  max: 6,  grade: 'C',  label: 'Average'      },
  { min: 4,  max: 5,  grade: 'D',  label: 'Below Avg'    },
  { min: 0,  max: 4,  grade: 'F',  label: 'Fail'         },
]

// File types
export const ACCEPTED_DOC_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg':      ['.jpg', '.jpeg'],
  'image/png':       ['.png'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
}

export const ACCEPTED_CATALOGUE_TYPES = {
  'text/csv':         ['.csv'],
  'application/json': ['.json'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
}

// Max file sizes
export const MAX_DOC_SIZE    = 20 * 1024 * 1024  // 20MB
export const MAX_AUDIO_SIZE  = 10 * 1024 * 1024  // 10MB

// Nav items for sidebar
export const NAV_ITEMS = [
  {
    section: 'PLATFORM',
    items: [
      { path: '/dashboard', label: 'Dashboard',  num: '00' },
    ],
  },
  {
    section: 'AI ENGINES',
    items: [
      { path: '/evaluator',   label: 'Evaluator',    num: '01' },
      { path: '/generator',   label: 'Generator',    num: '02' },
      { path: '/spelling',    label: 'Spell Check',  num: '03' },
      { path: '/voice-tutor', label: 'Voice Tutor',  num: '04' },
      { path: '/sales',       label: 'Sales AI',     num: '05' },
    ],
  },
  {
    section: 'ADMIN',
    items: [
      { path: '/admin',            label: 'Overview',    num: 'A1' },
      { path: '/admin/governance', label: 'Governance',  num: 'A2' },
      { path: '/admin/audit',      label: 'Audit Logs',  num: 'A3' },
    ],
  },
]

// Header nav items
export const HEADER_NAV = [
  { path: '/evaluator',   label: '01. ENGINE'     },
  { path: '/generator',   label: '02. CURRICULUM' },
  { path: '/voice-tutor', label: '03. NEURAL'     },
  { path: '/sales',       label: '04. SALES'      },
]

// Terminal log messages
export const LOG_MESSAGES = [
  { tag: 'SYS',  msg: 'INFERENCE_NODE: Token stream verified'             },
  { tag: 'OK',   msg: 'ADAPTIVE_ENGINE: Difficulty calibration complete'  },
  { tag: 'SYS',  msg: 'NEURAL_SYNTH: Embedding context vector loaded'     },
  { tag: 'OK',   msg: 'VECTOR_DB: Semantic query resolved in 1.4ms'       },
  { tag: 'SYS',  msg: 'AGENT_MONITOR: Student node active'                },
  { tag: 'OK',   msg: 'GOVERNANCE: Content filter pass — clean output'    },
  { tag: 'SYS',  msg: 'LLM_ROUTER: Groq LLaMA 3.3-70B responding'        },
  { tag: 'WARN', msg: 'RATE_LIMITER: Throttling burst requests'           },
  { tag: 'OK',   msg: 'AUDIT_LOG: Evaluation #8831 stored'               },
  { tag: 'SYS',  msg: 'VAD_PROC: Speech segment detected — 340ms'        },
  { tag: 'OK',   msg: 'STT_ENGINE: Transcription confidence 0.97'        },
  { tag: 'SYS',  msg: 'TTS_ENGINE: Edge TTS stream ready'                },
  { tag: 'OK',   msg: 'RAG_PIPE: Retrieved top-3 catalogue matches'      },
  { tag: 'SYS',  msg: 'LEAD_SCORER: Profile updated — WARM tier'        },
  { tag: 'OK',   msg: 'BIAS_CHECK: No discriminatory patterns found'     },
]

// Telemetry ribbon data
export const TELEMETRY_STATS = [
  { label: 'ACTIVE MODELS',    value: '04',    delta: '+0 errors' },
  { label: 'INFERENCE SPEED',  value: '1.4ms', delta: 'avg latency' },
  { label: 'STUDENT NODES',    value: '1.2K',  delta: '+8% today'  },
  { label: 'RETENTION RATE',   value: '94.2%', delta: '+2.1% week' },
]
