import { apiClient } from './client.js'

export const login = (credentials) =>
  apiClient.request('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
