import React from 'react'
import toast from 'react-hot-toast'
import { FiCheckCircle, FiAlertCircle, FiInfo, FiAlertTriangle } from 'react-icons/fi'

const BASE = {
  duration: 4000,
  style: {
    background:   'var(--bg-card)',
    color:        'var(--ink)',
    border:       '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    boxShadow:    'var(--shadow-xl)',
    fontFamily:   '"Plus Jakarta Sans", sans-serif',
    fontSize:     '14px', fontWeight: '600',
    padding:      '14px 18px', maxWidth: '400px',
  },
}

function GlowIcon({ icon: Icon, gradient, glow }) {
  return (
    <div style={{
      width: 32, height: 32, borderRadius: 'var(--radius-md)',
      background: gradient, display: 'flex', alignItems: 'center',
      justifyContent: 'center', flexShrink: 0,
      boxShadow: glow,
    }}>
      <Icon size={15} strokeWidth={2.5} color="#ffffff" />
    </div>
  )
}

export const showSuccess = (msg, opts = {}) =>
  toast.success(msg, { ...BASE, ...opts, icon: <GlowIcon icon={FiCheckCircle} gradient="linear-gradient(135deg,#10b981,#06b6d4)" glow="0 4px 12px rgba(16,185,129,0.4)" /> })

export const showError = (msg, opts = {}) =>
  toast.error(msg, { ...BASE, duration: 5000, ...opts, icon: <GlowIcon icon={FiAlertCircle} gradient="linear-gradient(135deg,#f43f5e,#ec4899)" glow="0 4px 12px rgba(244,63,94,0.4)" /> })

export const showInfo = (msg, opts = {}) =>
  toast(msg, { ...BASE, ...opts, icon: <GlowIcon icon={FiInfo} gradient="linear-gradient(135deg,#6366f1,#8b5cf6)" glow="0 4px 12px rgba(99,102,241,0.4)" /> })

export const showWarning = (msg, opts = {}) =>
  toast(msg, { ...BASE, ...opts, icon: <GlowIcon icon={FiAlertTriangle} gradient="linear-gradient(135deg,#f59e0b,#f43f5e)" glow="0 4px 12px rgba(245,158,11,0.4)" /> })

export const showLoading = (msg, opts = {}) => toast.loading(msg, { ...BASE, duration: Infinity, ...opts })
export const dismissToast = (id) => toast.dismiss(id)

export default { success: showSuccess, error: showError, info: showInfo, warning: showWarning, loading: showLoading, dismiss: dismissToast }
