/* ============================================================
   EDUMIND AI — LOCAL STORAGE HOOK
   ============================================================ */

import { useState, useCallback } from 'react'

export function useLocalStorage(key, initialValue) {
  // Get initial value
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch {
      return initialValue
    }
  })

  // Set value
  const setValue = useCallback(
    (value) => {
      try {
        const valueToStore =
          value instanceof Function ? value(storedValue) : value
        setStoredValue(valueToStore)
        localStorage.setItem(key, JSON.stringify(valueToStore))
      } catch (err) {
        console.error('useLocalStorage set error:', err)
      }
    },
    [key, storedValue]
  )

  // Remove value
  const removeValue = useCallback(() => {
    try {
      localStorage.removeItem(key)
      setStoredValue(initialValue)
    } catch (err) {
      console.error('useLocalStorage remove error:', err)
    }
  }, [key, initialValue])

  return [storedValue, setValue, removeValue]
}

export default useLocalStorage
