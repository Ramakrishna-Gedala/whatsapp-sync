import axios from 'axios'
import { toast } from 'sonner'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — log in dev
apiClient.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data)
  }
  return config
})

// Response interceptor — standardized error toasts
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    if (status === 422) {
      toast.error(detail || 'Invalid input — please check your data.')
    } else if (status === 409) {
      toast.warning(detail || 'This message was already processed.')
    } else if (status === 502) {
      toast.error('WhatsApp / AI service unavailable. Try again shortly.')
    } else if (status === 500) {
      toast.error('Server error. Please try again.')
    } else if (status === 404) {
      toast.error(detail || 'Resource not found.')
    } else if (!status) {
      toast.error('Network error — cannot reach the server.')
    }

    return Promise.reject(error)
  }
)

export default apiClient
