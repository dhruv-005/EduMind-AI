/* ============================================================
   EDUMIND AI — GENERATOR STORE (Challenge 2)
   ============================================================ */

import { create } from 'zustand'

export const useGeneratorStore = create((set, get) => ({
  // Upload state
  uploadedFiles: [],
  uploadProgress: 0,
  isUploading: false,

  // Pattern analysis
  patternAnalysis: null,
  isAnalyzing: false,

  // Config
  config: {
    subject: 'mathematics',
    level: 'grade-10',
    topic: '',
    numQuestions: 10,
    difficulty: 'mixed',
    questionType: 'mixed',
  },

  // Generated questions
  generatedQuestions: [],
  isGenerating: false,

  // Export
  isExporting: false,

  // Error
  error: null,

  // Setters
  setUploadedFiles: (files) => set({ uploadedFiles: files }),
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  setIsUploading: (uploading) => set({ isUploading: uploading }),
  setPatternAnalysis: (analysis) => set({ patternAnalysis: analysis }),
  setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
  setIsGenerating: (generating) => set({ isGenerating: generating }),
  setIsExporting: (exporting) => set({ isExporting: exporting }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Update config
  updateConfig: (updates) =>
    set((state) => ({
      config: { ...state.config, ...updates },
    })),

  // Set generated questions
  setGeneratedQuestions: (questions) =>
    set({ generatedQuestions: questions }),

  // Remove question
  removeQuestion: (index) =>
    set((state) => ({
      generatedQuestions: state.generatedQuestions.filter(
        (_, i) => i !== index
      ),
    })),

  // Reset all
  reset: () =>
    set({
      uploadedFiles: [],
      uploadProgress: 0,
      isUploading: false,
      patternAnalysis: null,
      isAnalyzing: false,
      generatedQuestions: [],
      isGenerating: false,
      error: null,
    }),
}))
