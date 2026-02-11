/**
 * API Client for Friday.AI backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('friday_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('friday_token')
      localStorage.removeItem('friday_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  signup: (data) => apiClient.post('/auth/signup', data),
  login: (data) => apiClient.post('/auth/login', data),
  me: () => apiClient.get('/auth/me'),
}

// Projects API
export const projectsAPI = {
  list: (skip = 0, limit = 50) => apiClient.get(`/projects?skip=${skip}&limit=${limit}`),
  get: (id) => apiClient.get(`/projects/${id}`),
  create: (data) => apiClient.post('/projects', data),
  update: (id, data) => apiClient.put(`/projects/${id}`, data),
  delete: (id) => apiClient.delete(`/projects/${id}`),
  stats: () => apiClient.get('/projects/stats'),
}

// Lifecycle API
export const lifecycleAPI = {
  getSteps: (projectId) => apiClient.get(`/projects/${projectId}/lifecycle`),
  getStep: (projectId, stepNumber) => apiClient.get(`/projects/${projectId}/lifecycle/${stepNumber}`),
  updateStep: (projectId, stepNumber, data) =>
    apiClient.put(`/projects/${projectId}/lifecycle/${stepNumber}`, data),
}

// Research Papers API (Step 1)
export const papersAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/papers`),
  get: (projectId, paperId) => apiClient.get(`/projects/${projectId}/papers/${paperId}`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/papers`, data),
  update: (projectId, paperId, data) =>
    apiClient.put(`/projects/${projectId}/papers/${paperId}`, data),
  delete: (projectId, paperId) => apiClient.delete(`/projects/${projectId}/papers/${paperId}`),
}

// Experiments API (Steps 2, 3, 4, 7)
export const experimentsAPI = {
  list: (projectId, type = null) =>
    apiClient.get(`/projects/${projectId}/experiments${type ? `?experiment_type=${type}` : ''}`),
  get: (projectId, expId) => apiClient.get(`/projects/${projectId}/experiments/${expId}`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/experiments`, data),
  update: (projectId, expId, data) =>
    apiClient.put(`/projects/${projectId}/experiments/${expId}`, data),
  delete: (projectId, expId) => apiClient.delete(`/projects/${projectId}/experiments/${expId}`),
}

// Benchmarks API (Step 5)
export const benchmarksAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/benchmarks`),
  get: (projectId, benchId) => apiClient.get(`/projects/${projectId}/benchmarks/${benchId}`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/benchmarks`, data),
  update: (projectId, benchId, data) =>
    apiClient.put(`/projects/${projectId}/benchmarks/${benchId}`, data),
  delete: (projectId, benchId) => apiClient.delete(`/projects/${projectId}/benchmarks/${benchId}`),
}

// Result Tables API (Step 6)
export const tablesAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/tables`),
  get: (projectId, tableId) => apiClient.get(`/projects/${projectId}/tables/${tableId}`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/tables`, data),
  autoGenerate: (projectId) => apiClient.post(`/projects/${projectId}/tables/auto-generate`),
  update: (projectId, tableId, data) =>
    apiClient.put(`/projects/${projectId}/tables/${tableId}`, data),
  delete: (projectId, tableId) => apiClient.delete(`/projects/${projectId}/tables/${tableId}`),
}

// LaTeX Reports API (Step 9)
export const reportsAPI = {
  list: (projectId) => apiClient.get(`/projects/${projectId}/reports`),
  get: (projectId, reportId) => apiClient.get(`/projects/${projectId}/reports/${reportId}`),
  create: (projectId, data) => apiClient.post(`/projects/${projectId}/reports`, data),
  generate: (projectId, templateType = 'ieee') =>
    apiClient.post(`/projects/${projectId}/reports/generate?template_type=${templateType}`),
  update: (projectId, reportId, data) =>
    apiClient.put(`/projects/${projectId}/reports/${reportId}`, data),
  delete: (projectId, reportId) => apiClient.delete(`/projects/${projectId}/reports/${reportId}`),
}

// Lifecycle Info
export const lifecycleInfoAPI = {
  get: () => apiClient.get('/lifecycle-info'),
}

export default apiClient
