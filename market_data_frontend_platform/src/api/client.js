const getBaseUrl = () => import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? response.statusText)
  }

  return response.json()
}

export const apiClient = { request }
