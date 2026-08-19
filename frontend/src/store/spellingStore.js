/* ============================================================
   EDUMIND AI — SPELLING STORE (Challenge 3)
   ============================================================ */

import { create } from 'zustand'

export const useSpellingStore = create((set, get) => ({
  // Upload
  uploadedFile: null,
  fileType: null,
  isUploading: false,

  // Processing
  isProcessing: false,
  processingStep: '',

  // Results
  report: null,
  annotatedFileUrl: null,

  // Filter
  showOnlyErrors: true,
  selectedPage: 1,

  // Error
  error: null,

  // Setters
  setUploadedFile: (file, type) =>
    set({ uploadedFile: file, fileType: type }),
  setIsUploading: (uploading) => set({ isUploading: uploading }),
  setIsProcessing: (processing) => set({ isProcessing: processing }),
  setProcessingStep: (step) => set({ processingStep: step }),
  setReport: (report) => set({ report }),
  setAnnotatedFileUrl: (url) => set({ annotatedFileUrl: url }),
  setShowOnlyErrors: (show) => set({ showOnlyErrors: show }),
  setSelectedPage: (page) => set({ selectedPage: page }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Get filtered errors
  getErrors: () => {
    const { report } = get()
    if (!report) return []
    return report.errors || []
  },

  // Reset
  reset: () =>
    set({
      uploadedFile: null,
      fileType: null,
      isUploading: false,
      isProcessing: false,
      processingStep: '',
      report: null,
      annotatedFileUrl: null,
      showOnlyErrors: true,
      selectedPage: 1,
      error: null,
    }),
}))
