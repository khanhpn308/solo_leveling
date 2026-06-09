const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

export const TOKEN_KEY = 'ielts_access_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setTokens(accessToken) {
  if (accessToken) localStorage.setItem(TOKEN_KEY, accessToken)
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
}

async function attemptRefresh() {
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!res.ok) return false
    const data = await res.json()
    setTokens(data.access_token)
    return true
  } catch {
    return false
  }
}

export async function apiFetch(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (response.status === 401) {
    const refreshed = await attemptRefresh()
    if (refreshed) {
      const retryHeaders = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
        ...(options.headers || {}),
      }
      const retryResponse = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: retryHeaders,
        credentials: 'include',
      })
      if (!retryResponse.ok) {
        const text = await retryResponse.text()
        const error = new Error(text || 'API error')
        error.status = retryResponse.status
        throw error
      }
      return retryResponse.json()
    }
    const text = await response.text()
    const error = new Error(text || 'Unauthorized')
    error.status = 401
    error.sessionExpired = true
    throw error
  }

  if (!response.ok) {
    const text = await response.text()
    const error = new Error(text || 'API error')
    error.status = response.status
    throw error
  }

  return response.json()
}
