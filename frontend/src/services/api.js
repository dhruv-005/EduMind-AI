/* ============================================================
   EDUMIND AI — BASE API CLIENT
   ============================================================ */

import axios from 'axios'
import toast from 'react-hot-toast'
import { API_BASE } from '@utils/constants'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — attach token
api.interceptors.request.use(
  (config) => {
    const stored = localStorage.getItem('edumind-auth')
    if (stored) {
      try {
        const { state } = JSON.parse(stored)
        if (state?.token) {
          config.headers.Authorization = `Bearer ${state.token}`
        }
      } catch {
        // ignore
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status  = error.response?.status
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An error occurred'

    if (status === 401) {
      localStorage.removeItem('edumind-auth')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (status === 429) {
      toast.error('[ RATE LIMIT ] Too many requests. Please wait.')
      return Promise.reject(error)
    }

    if (status >= 500) {
      toast.error(`[ SERVER ERROR ] ${message}`)
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

export default api
