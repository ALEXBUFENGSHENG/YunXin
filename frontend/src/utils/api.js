const ADMIN_TOKEN_KEY = 'ai-assistant-admin-token'

export const getApiBaseUrl = () => {
  const envBase = import.meta.env?.VITE_API_BASE?.trim()
  if (envBase) return envBase.replace(/\/$/, '')

  // In development (with proxy), we can use relative path
  // If the host has a port (dev server), use relative path to let Vite proxy handle it
  if (/:(\d+)$/.test(window.location.host)) {
    return ''
  }

  // Production or other cases
  return ''
}

export const getAdminToken = () => localStorage.getItem(ADMIN_TOKEN_KEY)

export const setAdminToken = (token) => {
  if (!token) return
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
}

export const clearAdminToken = () => {
  localStorage.removeItem(ADMIN_TOKEN_KEY)
}

export const getAuthHeaders = () => {
  const token = getAdminToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}
