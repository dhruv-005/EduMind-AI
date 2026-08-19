/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Space Grotesk', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        base: 'var(--base)',
        surface: 'var(--surface)',
        'surface-elevated': 'var(--surface-elevated)',
        ink: 'var(--ink)',
        muted: 'var(--muted)',
        'accent-primary': 'var(--accent-primary)',
        'accent-cyber': 'var(--accent-cyber)',
        'term-green': 'var(--term-green)',
        'term-amber': 'var(--term-amber)',
        'term-bg': 'var(--term-bg)',
      },
      boxShadow: {
        'hard': '6px 6px 0px var(--ink)',
        'hard-hover': '10px 10px 0px var(--ink)',
        'hard-accent': '6px 6px 0px var(--accent-primary)',
        'hard-cyber': '6px 6px 0px var(--accent-cyber)',
      },
      borderWidth: {
        '3': '3px',
      },
      animation: {
        'radar-sweep': 'radarSweep 6s linear infinite',
        'pulse-dot': 'pulseDot 2s ease-in-out infinite',
        'marquee': 'marquee 30s linear infinite',
        'blink': 'blink 1s step-end infinite',
        'scan-line': 'scanLine 3s ease-in-out infinite',
        'counter': 'counter 2s ease-out forwards',
      },
      keyframes: {
        radarSweep: {
          'from': { transform: 'rotate(0deg)' },
          'to': { transform: 'rotate(360deg)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: 1, transform: 'scale(1)' },
          '50%': { opacity: 0.4, transform: 'scale(0.8)' },
        },
        marquee: {
          'from': { transform: 'translateX(0)' },
          'to': { transform: 'translateX(-50%)' },
        },
        blink: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0 },
        },
        scanLine: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
      },
      gridTemplateColumns: {
        '12': 'repeat(12, 1fr)',
        'bento': '8fr 4fr',
        'bento-equal': '1fr 1fr',
      },
    },
  },
  plugins: [],
}
