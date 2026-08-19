/* ============================================================
   EDUMIND AI — VOICE TUTOR SERVICE (Challenge 4)
   ============================================================ */

import api from './api'
import { WS_BASE } from '@utils/constants'

export const voiceTutorService = {
  // Create a new session
  createSession: async (config) => {
    const response = await api.post(
      '/api/v1/voice-tutor/session',
      config
    )
    return response.data
  },

  // End session
  endSession: async (sessionId) => {
    const response = await api.delete(
      `/api/v1/voice-tutor/session/${sessionId}`
    )
    return response.data
  },

  // Get session history
  getHistory: async (params = {}) => {
    const response = await api.get(
      '/api/v1/voice-tutor/history',
      { params }
    )
    return response.data
  },

  // Get session summary
  getSessionSummary: async (sessionId) => {
    const response = await api.get(
      `/api/v1/voice-tutor/session/${sessionId}/summary`
    )
    return response.data
  },

  // Create WebSocket connection
  createWebSocket: (sessionId, token) => {
    const wsUrl = `${WS_BASE}/api/v1/voice-tutor/ws/${sessionId}?token=${token}`
    return new WebSocket(wsUrl)
  },

  // Get supported subjects
  getSubjects: async () => {
    const response = await api.get('/api/v1/voice-tutor/subjects')
    return response.data
  },
}

export default voiceTutorService
