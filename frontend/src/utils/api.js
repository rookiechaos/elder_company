import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// GET response cache (no dedup - pendingRequests was ineffective)
const requestCache = new Map()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes
const MAX_RETRIES = 2
const RETRY_DELAY_MS = 1000

function getCacheKey(config) {
  return `${config.method}:${config.url}:${JSON.stringify(config.params || {})}:${JSON.stringify(config.data || {})}`
}

function isRetryable(config) {
  return (config.method === 'get' || config.retry === true) && (config.__retryCount ?? 0) < MAX_RETRIES
}

// Request interceptor - attach auth token, optional GET cache hit
api.interceptors.request.use(
  (config) => {
    const token = typeof localStorage !== 'undefined' && localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    const cacheKey = getCacheKey(config)

    // Check cache for GET requests only
    if (config.method === 'get' && requestCache.has(cacheKey)) {
      const cached = requestCache.get(cacheKey)
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        return Promise.reject({ __cached: true, data: cached.data })
      }
      requestCache.delete(cacheKey)
    }

    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - cache GET, parse errors, 401 logout, retry
api.interceptors.response.use(
  (response) => {
    const config = response.config
    if (config.method === 'get') {
      const cacheKey = getCacheKey(config)
      requestCache.set(cacheKey, { data: response.data, timestamp: Date.now() })
      if (requestCache.size > 100) {
        const now = Date.now()
        for (const [key, value] of requestCache.entries()) {
          if (now - value.timestamp > CACHE_TTL) requestCache.delete(key)
        }
      }
    }
    return response
  },
  (error) => {
    if (error.__cached) {
      return Promise.resolve({ data: error.data, __cached: true })
    }

    const config = error.config || {}

    // 401: clear token and notify app to logout (AuthContext listens for 'auth:logout')
    if (error.response?.status === 401) {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_id')
      }
      if (typeof window !== 'undefined' && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('auth:logout', { detail: { reason: 'session_expired' } }))
      }
    }

    // Retry: only for retryable requests (GET or config.retry) on no response or 5xx
    const noResponse = !error.response
    const serverError = error.response?.status >= 500
    if (isRetryable(config) && (noResponse || serverError)) {
      config.__retryCount = (config.__retryCount ?? 0) + 1
      return new Promise((resolve) => {
        setTimeout(() => resolve(api.request(config)), RETRY_DELAY_MS)
      })
    }

    // Normalize error message: backend uses { error: { message } } (error_handler), or detail/message
    let message = 'Request failed'
    if (error.response?.data) {
      const d = error.response.data
      message = d?.error?.message ?? d?.detail ?? d?.message ?? message
    } else if (error.request) {
      message = 'Unable to connect to the server. Please check your network connection.'
    } else if (error.message) {
      message = error.message
    }
    return Promise.reject(new Error(message))
  }
)

export default api
