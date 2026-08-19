/* ============================================================
   EDUMIND AI — TYPOGRAPHY TOKENS
   ============================================================ */

export const typography = {
  fonts: {
    heading: "'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif",
    mono: "'JetBrains Mono', 'Courier New', monospace",
  },

  weights: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  sizes: {
    hero: 'clamp(3rem, 8vw, 8.5rem)',
    display: 'clamp(2rem, 5vw, 5rem)',
    h1: 'clamp(1.8rem, 3.5vw, 3.5rem)',
    h2: 'clamp(1.4rem, 2.5vw, 2.4rem)',
    h3: 'clamp(1.1rem, 1.5vw, 1.4rem)',
    h4: 'clamp(0.95rem, 1.2vw, 1.1rem)',
    body: 'clamp(0.85rem, 1vw, 1rem)',
    data: 'clamp(0.75rem, 0.9vw, 0.9rem)',
    micro: '0.65rem',
    nano: '0.58rem',
  },

  letterSpacing: {
    tight: '-0.03em',
    normal: '0em',
    wide: '0.08em',
    wider: '0.12em',
    widest: '0.2em',
  },

  lineHeights: {
    heading: '0.92',
    body: '1.6',
    relaxed: '1.7',
    tight: '1.2',
  },
}

export default typography
