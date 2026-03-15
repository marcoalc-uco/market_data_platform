const getBaseUrl = () => import.meta.env.VITE_API_URL ?? ''

function buildHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra }
  const token = localStorage.getItem('token')
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function request(path, options = {}) {
  const { headers: extraHeaders, ...rest } = options
  const response = await fetch(`${getBaseUrl()}${path}`, {
    ...rest,
    headers: buildHeaders(extraHeaders),
  })

  if (response.status === 204) return null

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      // Throw a silent error so the promise chain breaks without showing an alert
      throw new Error('Session expired')
    }
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? response.statusText)
  }

  return response.json()
}

export const apiClient = { request }
