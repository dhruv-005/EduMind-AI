/* ============================================================
   EDUMIND AI — PAGE WRAPPER COMPONENT
   Main app shell layout — Nav + Main + Terminal Sidebar
   ============================================================ */

import React, { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import TerminalSidebar from './TerminalSidebar'
import Breadcrumb from './Breadcrumb'
import Footer from './Footer'

// Pages that should hide the terminal sidebar
const NO_TERMINAL_PAGES = [
  '/voice-tutor',
]

// Pages that should hide footer
const NO_FOOTER_PAGES = [
  '/voice-tutor',
  '/sales',
]

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    y: 8,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: {
      duration: 0.15,
    },
  },
}

export default function PageWrapper() {
  const location = useLocation()

  const showTerminal = !NO_TERMINAL_PAGES.some((p) =>
    location.pathname.startsWith(p)
  )
  const showFooter = !NO_FOOTER_PAGES.some((p) =>
    location.pathname.startsWith(p)
  )

  // Scroll to top on route change
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  return (
    <div style={{
      display: 'grid',
      gridTemplateRows: 'var(--header-h) 1fr',
      minHeight: '100vh',
    }}>

      {/* ── FIXED NAVBAR ──────────────────────────────── */}
      <Navbar />

      {/* ── CONTENT AREA (below navbar) ───────────────── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: showTerminal
          ? 'var(--nav-sidebar-w) 1fr var(--sidebar-w)'
          : 'var(--nav-sidebar-w) 1fr',
        marginTop: 'var(--header-h)',
        minHeight: 'calc(100vh - var(--header-h))',
      }}>

        {/* ── LEFT NAV SIDEBAR ──────────────────────── */}
        <Sidebar />

        {/* ── MAIN CONTENT ──────────────────────────── */}
        <main style={{
          minWidth: 0,
          display: 'flex',
          flexDirection: 'column',
          borderRight: showTerminal ? 'var(--border)' : 'none',
          borderLeft: 'var(--border)',
        }}>

          {/* Breadcrumb */}
          <Breadcrumb />

          {/* Coordinate grid background */}
          <div style={{ position: 'relative', flex: 1 }}>
            <div className="coord-grid" />

            {/* Page content with transition */}
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                variants={pageVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                style={{
                  position: 'relative',
                  zIndex: 1,
                  minHeight: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <Outlet />

                {/* Footer inside main */}
                {showFooter && <Footer />}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        {/* ── RIGHT TERMINAL SIDEBAR ────────────────── */}
        {showTerminal && <TerminalSidebar />}
      </div>

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 1280px) {
          div[style*="var(--nav-sidebar-w) 1fr var(--sidebar-w)"] {
            grid-template-columns: var(--nav-sidebar-w) 1fr !important;
          }
          div[style*="var(--nav-sidebar-w) 1fr var(--sidebar-w)"] > aside:last-child {
            display: none !important;
          }
        }

        @media (max-width: 768px) {
          div[style*="var(--nav-sidebar-w) 1fr"] {
            grid-template-columns: 1fr !important;
          }
          div[style*="var(--nav-sidebar-w) 1fr"] > aside:first-child {
            display: none !important;
          }
          main {
            border-left: none !important;
          }
        }
      `}</style>
    </div>
  )
}
