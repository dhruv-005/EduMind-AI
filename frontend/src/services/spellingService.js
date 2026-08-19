/* ============================================================
   EDUMIND AI — SPELLING SERVICE (Challenge 3)
   ============================================================ */

import api from './api'

export const spellingService = {
  // Upload and detect spelling errors
  detectErrors: async (file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      '/api/v1/spelling/detect',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
        onUploadProgress: (e) => {
          if (onProgress) {
            onProgress(Math.round((e.loaded * 100) / e.total))
          }
        },
      }
    )
    return response.data
  },

  // Download annotated document
  downloadAnnotated: async (reportId) => {
    const response = await api.get(
      `/api/v1/spelling/annotated/${reportId}`,
      { responseType: 'blob' }
    )
    return response.data
  },

  // Get report by ID
  getReport: async (reportId) => {
    const response = await api.get(`/api/v1/spelling/report/${reportId}`)
    return response.data
  },
}

export default spellingService
