/**
 * API Client — Axios instance with auth interceptor.
 * Implementation: TICKET-015
 */

// TODO: [TICKET-015] Implement API client
// - Create Axios instance with baseURL from env
// - Request interceptor: attach Bearer token from localStorage
// - Response interceptor: redirect to /login on 401
// - Export helper functions: get, post, put, delete

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export default { API_BASE_URL }
