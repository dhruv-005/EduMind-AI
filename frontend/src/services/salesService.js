/* ============================================================
   EDUMIND AI — SALES SERVICE (Challenge 5)
   ============================================================ */

import api from './api'

export const salesService = {
  // Upload product catalogue
  uploadCatalogue: async (file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      '/api/v1/sales/catalogue/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (onProgress) {
            onProgress(Math.round((e.loaded * 100) / e.total))
          }
        },
      }
    )
    return response.data
  },

  // Get catalogue
  getCatalogue: async () => {
    const response = await api.get('/api/v1/sales/catalogue')
    return response.data
  },

  // Send chat message
  sendMessage: async (conversationId, message) => {
    const response = await api.post('/api/v1/sales/chat', {
      conversation_id: conversationId,
      message,
    })
    return response.data
  },

  // Start new conversation
  startConversation: async () => {
    const response = await api.post('/api/v1/sales/conversation')
    return response.data
  },

  // Get recommendations
  getRecommendations: async (conversationId) => {
    const response = await api.get(
      `/api/v1/sales/recommendations/${conversationId}`
    )
    return response.data
  },

  // Get lead score
  getLeadScore: async (conversationId) => {
    const response = await api.get(
      `/api/v1/sales/lead-score/${conversationId}`
    )
    return response.data
  },

  // Generate follow-up
  generateFollowUp: async (conversationId) => {
    const response = await api.post(
      `/api/v1/sales/follow-up/${conversationId}`
    )
    return response.data
  },

  // Get all leads
  getLeads: async (params = {}) => {
    const response = await api.get('/api/v1/sales/leads', { params })
    return response.data
  },

  // Escalate conversation
  escalate: async (conversationId) => {
    const response = await api.post(
      `/api/v1/sales/escalate/${conversationId}`
    )
    return response.data
  },
}

export default salesService
