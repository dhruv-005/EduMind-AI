/* ============================================================
   EDUMIND AI — EVALUATOR STORE (Challenge 1)
   ============================================================ */

import { create } from 'zustand'

export const useEvaluatorStore = create((set, get) => ({
  // Form state
  question: '',
  referenceAnswer: '',
  studentAnswer: '',
  subject: 'general',
  maxScore: 10,

  // Result state
  result: null,
  isLoading: false,
  error: null,

  // History
  history: [],

  // Setters
  setQuestion: (question) => set({ question }),
  setReferenceAnswer: (referenceAnswer) => set({ referenceAnswer }),
  setStudentAnswer: (studentAnswer) => set({ studentAnswer }),
  setSubject: (subject) => set({ subject }),
  setMaxScore: (maxScore) => set({ maxScore }),

  // Set result
  setResult: (result) => set({ result }),

  // Set loading
  setLoading: (isLoading) => set({ isLoading }),

  // Set error
  setError: (error) => set({ error }),

  // Clear error
  clearError: () => set({ error: null }),

  // Reset form
  resetForm: () =>
    set({
      question: '',
      referenceAnswer: '',
      studentAnswer: '',
      subject: 'general',
      maxScore: 10,
      result: null,
      error: null,
    }),

  // Add to history
  addToHistory: (evaluation) =>
    set((state) => ({
      history: [evaluation, ...state.history].slice(0, 50),
    })),

  // Clear history
  clearHistory: () => set({ history: [] }),

  // Get form data
  getFormData: () => {
    const state = get()
    return {
      question: state.question,
      reference_answer: state.referenceAnswer,
      student_answer: state.studentAnswer,
      subject: state.subject,
      max_score: state.maxScore,
    }
  },
}))
