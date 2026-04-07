/**
 * Axios API client — all requests go through here.
 *
 * Features:
 *  - Auto-attaches Bearer token from localStorage
 *  - Intercepts 401 → clears auth & redirects to /login
 *  - Base URL set to /api/v1 (proxied to backend in dev)
 */
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 90_000, // 90s — AI generation can be slow
})

// ── Request interceptor: attach JWT ──────────────────
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor: handle 401 ─────────────────
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      // Avoid redirect loop on login page
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── Auth ──────────────────────────────────────────────
export const authApi = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  me: () => client.get('/auth/me'),
}

// ── Lessons ───────────────────────────────────────────
export const lessonsApi = {
  generate: (data) => client.post('/lessons/generate', data),
  get: (lessonId) => client.get(`/lessons/${lessonId}`),
}

// ── Quizzes ───────────────────────────────────────────
export const quizzesApi = {
  generate: (data) => client.post('/quizzes/generate', data),
  submit: (data) => client.post('/quizzes/submit', data),
}

// ── Performance ───────────────────────────────────────
export const performanceApi = {
  list: () => client.get('/performance'),
  insights: () => client.get('/performance/insights'),
}

// ── Strategy ──────────────────────────────────────────
export const strategyApi = {
  nextTopic: () => client.get('/strategy/next-topic'),
}

export default client
