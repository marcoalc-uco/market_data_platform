import { apiClient } from './client.js'

export const getInstruments = (params) =>
  apiClient.request('/api/v1/instruments?' + new URLSearchParams(params))

export const getInstrument = (id) => apiClient.request(`/api/v1/instruments/${id}`)

export const createInstrument = (data) =>
  apiClient.request('/api/v1/instruments', {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const updateInstrument = (id, data) =>
  apiClient.request(`/api/v1/instruments/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })

export const deleteInstrument = (id) =>
  apiClient.request(`/api/v1/instruments/${id}`, { method: 'DELETE' })
