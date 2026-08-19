/* ============================================================
   EDUMIND AI — EVALUATOR SERVICE (Challenge 1)
   ============================================================ */

import api from './api'

export const evaluatorService = {

  evaluate: async (data) => {
    const response = await api.post(
      '/api/v1/evaluator/evaluate',
      data,
      { timeout: 120000 }
    )
    return response.data
  },

  batchEvaluate: async (data) => {
    const response = await api.post(
      '/api/v1/evaluator/batch',
      data,
      { timeout: 180000 }
    )
    return response.data
  },

  getHistory: async (params = {}) => {
    const response = await api.get(
      '/api/v1/evaluator/history',
      { params, timeout: 30000 }
    )
    return response.data
  },

  getEvaluation: async (id) => {
    const response = await api.get(
      `/api/v1/evaluator/${id}`,
      { timeout: 30000 }
    )
    return response.data
  },

  getSubjects: async () => {
    const response = await api.get(
      '/api/v1/evaluator/subjects',
      { timeout: 10000 }
    )
    return response.data
  },
}

export default evaluatorService
