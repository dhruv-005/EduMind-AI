import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useThemeStore } from '@store/themeStore'

// Pages
import Landing from '@pages/Landing'
import Dashboard from '@pages/Dashboard'
import Login from '@pages/Login'

// Evaluator Pages
import EvaluatorPage from '@pages/evaluator/EvaluatorPage'
import EvaluationHistoryPage from '@pages/evaluator/EvaluationHistoryPage'

// Generator Pages
import GeneratorPage from '@pages/generator/GeneratorPage'
import PaperUploadPage from '@pages/generator/PaperUploadPage'

// Spelling Pages
import SpellingPage from '@pages/spelling/SpellingPage'
import SpellingReportPage from '@pages/spelling/SpellingReportPage'

// Voice Tutor Pages
import VoiceTutorPage from '@pages/voice_tutor/VoiceTutorPage'

// Sales Pages
import SalesPage from '@pages/sales/SalesPage'
import CataloguePage from '@pages/sales/CataloguePage'
import LeadsPage from '@pages/sales/LeadsPage'

// Admin Pages
import AdminDashboard from '@pages/admin/AdminDashboard'
import GovernanceDashboard from '@pages/admin/GovernanceDashboard'
import AuditLogs from '@pages/admin/AuditLogs'

// Layout
import PageWrapper from '@components/layout/PageWrapper'

export default function App() {
  const { theme } = useThemeStore()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <Router>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'var(--term-bg)',
            color: '#fff',
            border: '2px solid var(--accent-primary)',
            borderRadius: '0px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            letterSpacing: '0.05em',
          },
        }}
      />
      <Routes>
        {/* Public */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />

        {/* App Shell */}
        <Route element={<PageWrapper />}>
          <Route path="/dashboard" element={<Dashboard />} />

          {/* Challenge 1 — Evaluator */}
          <Route path="/evaluator" element={<EvaluatorPage />} />
          <Route path="/evaluator/history" element={<EvaluationHistoryPage />} />

          {/* Challenge 2 — Generator */}
          <Route path="/generator" element={<GeneratorPage />} />
          <Route path="/generator/upload" element={<PaperUploadPage />} />

          {/* Challenge 3 — Spelling */}
          <Route path="/spelling" element={<SpellingPage />} />
          <Route path="/spelling/report" element={<SpellingReportPage />} />

          {/* Challenge 4 — Voice Tutor */}
          <Route path="/voice-tutor" element={<VoiceTutorPage />} />

          {/* Challenge 5 — Sales */}
          <Route path="/sales" element={<SalesPage />} />
          <Route path="/sales/catalogue" element={<CataloguePage />} />
          <Route path="/sales/leads" element={<LeadsPage />} />

          {/* Admin */}
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/governance" element={<GovernanceDashboard />} />
          <Route path="/admin/audit" element={<AuditLogs />} />
        </Route>
      </Routes>
    </Router>
  )
}
