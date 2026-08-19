/* ============================================================
   EDUMIND AI — GENERATOR SERVICE (Challenge 2)
   ============================================================ */

import api from './api'

export const generatorService = {

  uploadPapers: async (files, onProgress) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))

    const response = await api.post(
      '/api/v1/generator/upload',
      formData,
      {
        headers:  { 'Content-Type': 'multipart/form-data' },
        timeout:  60000,
        onUploadProgress: (e) => {
          if (onProgress) {
            onProgress(Math.round((e.loaded * 100) / e.total))
          }
        },
      }
    )
    return response.data
  },

  analyzePapers: async (uploadId) => {
    const response = await api.post(
      `/api/v1/generator/analyze/${uploadId}`,
      {},
      { timeout: 60000 }
    )
    return response.data
  },

  generateQuestions: async (config) => {
    const response = await api.post(
      '/api/v1/generator/generate',
      config,
      { timeout: 120000 }
    )
    return response.data
  },

  exportPDF: async (questions, config) => {
    const response = await api.post(
      '/api/v1/generator/export',
      { questions, config },
      { responseType: 'blob', timeout: 60000 }
    )
    return response.data
  },

  getHistory: async () => {
    const response = await api.get(
      '/api/v1/generator/history',
      { timeout: 30000 }
    )
    return response.data
  },
}

export default generatorService
