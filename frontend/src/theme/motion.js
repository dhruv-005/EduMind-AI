/**
 * EduMind AI — Motion Tokens
 * Warm, encouraging motion for student surfaces
 * Snappy but not cold
 */

export const EASE        = [0.22, 1, 0.36, 1]
export const EASE_SPRING = [0.34, 1.56, 0.64, 1]  /* slight spring */
export const EASE_SNAPPY = [0.16, 1, 0.30, 1]

export const DUR = {
  xs:  0.15,
  sm:  0.25,
  md:  0.35,
  lg:  0.50,
}

/* Page transitions */
export const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: DUR.md, ease: EASE },
  },
  exit: {
    opacity: 0,
    y: -6,
    transition: { duration: DUR.xs },
  },
}

export const fadeVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: DUR.sm } },
  exit:    { opacity: 0, transition: { duration: DUR.xs } },
}

/* Card/list stagger */
export const listVariants = {
  animate: {
    transition: { staggerChildren: 0.07, delayChildren: 0.05 },
  },
}

export const cardVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: DUR.md, ease: EASE },
  },
}

/* Modal */
export const modalVariants = {
  initial: { opacity: 0, scale: 0.95, y: 10 },
  animate: {
    opacity: 1, scale: 1, y: 0,
    transition: { duration: DUR.sm, ease: EASE_SNAPPY },
  },
  exit: {
    opacity: 0, scale: 0.95,
    transition: { duration: DUR.xs },
  },
}

export const backdropVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: DUR.sm } },
  exit:    { opacity: 0, transition: { duration: DUR.sm } },
}

/* Toast */
export const toastVariants = {
  initial: { opacity: 0, x: 80 },
  animate: {
    opacity: 1,
    x: 0,
    transition: { type: 'spring', stiffness: 300, damping: 28 },
  },
  exit: {
    opacity: 0,
    x: 80,
    transition: { duration: DUR.xs },
  },
}

/* Input shake on error */
export const inputShakeVariants = {
  shake: {
    x: [0, -5, 5, -5, 5, 0],
    transition: { duration: DUR.sm },
  },
}

/* Governance badge pulse */
export const govBadgeVariants = {
  initial: { scale: 1 },
  animate: {
    scale: [1, 1.05, 1],
    transition: { duration: 0.4, ease: EASE_SPRING },
  },
}

export const pressVariants = { tap: { scale: 0.97 } }

export const sidebarVariants = {
  open:   { width: 240, transition: { duration: DUR.sm, ease: EASE_SNAPPY } },
  closed: { width: 72,  transition: { duration: DUR.sm, ease: EASE_SNAPPY } },
}

/**
 * Returns fade-only variants when reduced-motion is preferred
 */
export function resolveVariants(isReduced, fullVariants) {
  return isReduced ? fadeVariants : fullVariants
}
