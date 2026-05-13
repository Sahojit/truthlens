import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Add auth token from storage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tl_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Prediction ────────────────────────────────────────────────
export const predict = (data) => api.post('/api/predict/', data)
export const quickPredict = (data) => api.post('/api/predict/quick', data)

// ── Auth ──────────────────────────────────────────────────────
export const register = (data) => api.post('/api/auth/register', data)
export const login = (data) => api.post('/api/auth/login', data)
export const getProfile = () => api.get('/api/auth/me')

// ── Analytics ─────────────────────────────────────────────────
export const getAnalyticsSummary = () => api.get('/api/analytics/summary')
export const getAnalyticsTrends = (days = 30) => api.get(`/api/analytics/trends?days=${days}`)
export const getEmotionDistribution = () => api.get('/api/analytics/emotion-distribution')
export const getModelAccuracy = () => api.get('/api/analytics/model-accuracy')

// ── Sources ───────────────────────────────────────────────────
export const checkSource = (url) => api.get(`/api/sources/check?url=${encodeURIComponent(url)}`)
export const getCredibilityLeaderboard = () => api.get('/api/sources/leaderboard')
export const getAllSources = () => api.get('/api/sources/all')

// ── Graphs ────────────────────────────────────────────────────
export const buildEntityGraph = (data) => api.post('/api/graphs/entity-graph', data)
export const getSampleGraph = () => api.get('/api/graphs/sample')

// ── Metrics ───────────────────────────────────────────────────
export const getModelEvaluation = () => api.get('/api/metrics/evaluation')
export const getConfusionMatrix = (model) => api.get(`/api/metrics/confusion-matrix/${model}`)

// ── History ───────────────────────────────────────────────────
export const getHistory = (page = 1, limit = 20) =>
  api.get(`/api/history/?page=${page}&limit=${limit}`)
export const getPrediction = (id) => api.get(`/api/history/${id}`)
export const deletePrediction = (id) => api.delete(`/api/history/${id}`)

export default api
