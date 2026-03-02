import { apiClient } from './client.js'

export const getPrices = (instrumentId, params) =>
  apiClient.request(`/api/v1/prices/${instrumentId}?` + new URLSearchParams(params))

export const getLatestPrice = (instrumentId) =>
  apiClient.request(`/api/v1/prices/${instrumentId}/latest`)
