/* ============================================================
   EDUMIND AI — COLOR TOKENS (JS Mirror of CSS Variables)
   ============================================================ */

export const colors = {
  // Base
  base: 'var(--base)',
  surface: 'var(--surface)',
  surfaceElevated: 'var(--surface-elevated)',
  ink: 'var(--ink)',
  muted: 'var(--muted)',

  // Accents
  accentPrimary: 'var(--accent-primary)',
  accentCyber: 'var(--accent-cyber)',
  accentPurple: 'var(--accent-purple)',

  // Status
  termGreen: 'var(--term-green)',
  termAmber: 'var(--term-amber)',
  termRed: 'var(--term-red)',
  termBg: 'var(--term-bg)',

  // Raw values — Light
  light: {
    base: '#FFFFFF',
    surface: '#F4F4EF',
    surfaceElevated: '#EAEAE4',
    ink: '#0A0A0C',
    muted: '#737373',
    accentPrimary: '#FF3E00',
    accentCyber: '#00F0FF',
    termGreen: '#00E65B',
    termAmber: '#FFB000',
    termRed: '#FF2D55',
    termBg: '#0A0B0E',
  },

  // Raw values — Dark
  dark: {
    base: '#0A0B0E',
    surface: '#12141A',
    surfaceElevated: '#1A1D26',
    ink: '#F0F2F5',
    muted: '#8E95A2',
    accentPrimary: '#FF5500',
    accentCyber: '#00F0FF',
    termGreen: '#00E65B',
    termAmber: '#FFB000',
    termRed: '#FF2D55',
    termBg: '#050507',
  },
}

// Score color helper
export function getScoreColor(score) {
  if (score >= 8) return colors.termGreen
  if (score >= 5) return colors.termAmber
  return colors.termRed
}

// Grade label helper
export function getGradeLabel(score) {
  if (score >= 9) return 'A+'
  if (score >= 8) return 'A'
  if (score >= 7) return 'B+'
  if (score >= 6) return 'B'
  if (score >= 5) return 'C'
  if (score >= 4) return 'D'
  return 'F'
}

// Lead score color helper
export function getLeadColor(score) {
  if (score >= 75) return colors.termRed      // Hot
  if (score >= 50) return colors.termAmber    // Warm
  if (score >= 25) return colors.accentCyber  // Cool
  return colors.muted                          // Cold
}

export default colors
