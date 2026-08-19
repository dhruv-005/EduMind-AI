/* ============================================================
   EDUMIND AI — THEME STORE (Zustand)
   ============================================================ */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'dark', // default dark

      // Toggle between light and dark
      toggleTheme: () => {
        const next = get().theme === 'dark' ? 'light' : 'dark'
        document.documentElement.setAttribute('data-theme', next)
        set({ theme: next })
      },

      // Set specific theme
      setTheme: (theme) => {
        document.documentElement.setAttribute('data-theme', theme)
        set({ theme })
      },

      // Initialize from system preference if no stored value
      initTheme: () => {
        const stored = localStorage.getItem('edumind-theme')
        if (!stored) {
          const prefersDark = window.matchMedia(
            '(prefers-color-scheme: dark)'
          ).matches
          const theme = prefersDark ? 'dark' : 'light'
          document.documentElement.setAttribute('data-theme', theme)
          set({ theme })
        } else {
          document.documentElement.setAttribute(
            'data-theme',
            get().theme
          )
        }
      },
    }),
    {
      name: 'edumind-theme',
      partialize: (state) => ({ theme: state.theme }),
    }
  )
)
