import { apiClient } from './client.js'

export const login = ({ username, password }) =>
  apiClient.request('/api/v1/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password }).toString(),
  })
