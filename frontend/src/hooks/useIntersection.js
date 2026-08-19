/* ============================================================
   EDUMIND AI — INTERSECTION OBSERVER HOOK
   For scroll-triggered animations
   ============================================================ */

import { useState, useEffect, useRef } from 'react'

export function useIntersection({
  threshold = 0.1,
  rootMargin = '0px',
  once = true,
} = {}) {
  const ref = useRef(null)
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [hasTriggered, setHasTriggered]     = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true)
          setHasTriggered(true)
          if (once) observer.unobserve(element)
        } else {
          if (!once) setIsIntersecting(false)
        }
      },
      { threshold, rootMargin }
    )

    observer.observe(element)
    return () => observer.unobserve(element)
  }, [threshold, rootMargin, once])

  return { ref, isIntersecting, hasTriggered }
}

export default useIntersection
