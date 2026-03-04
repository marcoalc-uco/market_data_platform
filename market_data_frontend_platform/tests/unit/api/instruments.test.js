import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getInstruments,
  getInstrument,
  createInstrument,
  updateInstrument,
  deleteInstrument,
} from '../../../src/api/instruments.js'
import * as clientModule from '../../../src/api/client.js'

const mockInstrument = {
  id: 1,
  symbol: 'AAPL',
  name: 'Apple Inc.',
  asset_type: 'stock',
  is_active: true,
}

describe('instruments API', () => {
  beforeEach(() => {
    vi.spyOn(clientModule.apiClient, 'request').mockResolvedValue(mockInstrument)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getInstruments', () => {
    it('calls GET /api/v1/instruments', async () => {
      await getInstruments({})
      expect(clientModule.apiClient.request).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/instruments')
      )
    })

    it('appends query params to URL', async () => {
      await getInstruments({ asset_type: 'stock', is_active: 'true' })
      const [url] = clientModule.apiClient.request.mock.calls[0]
      expect(url).toContain('asset_type=stock')
      expect(url).toContain('is_active=true')
    })
  })

  describe('getInstrument', () => {
    it('calls GET /api/v1/instruments/:id', async () => {
      await getInstrument(1)
      expect(clientModule.apiClient.request).toHaveBeenCalledWith('/api/v1/instruments/1')
    })
  })

  describe('createInstrument', () => {
    it('calls POST /api/v1/instruments with body', async () => {
      const data = { symbol: 'TSLA', name: 'Tesla', asset_type: 'stock' }
      await createInstrument(data)
      expect(clientModule.apiClient.request).toHaveBeenCalledWith(
        '/api/v1/instruments',
        expect.objectContaining({ method: 'POST', body: JSON.stringify(data) })
      )
    })
  })

  describe('updateInstrument', () => {
    it('calls PUT /api/v1/instruments/:id with body', async () => {
      const data = { name: 'Apple Inc. Updated' }
      await updateInstrument(1, data)
      expect(clientModule.apiClient.request).toHaveBeenCalledWith(
        '/api/v1/instruments/1',
        expect.objectContaining({ method: 'PUT', body: JSON.stringify(data) })
      )
    })
  })

  describe('deleteInstrument', () => {
    it('calls DELETE /api/v1/instruments/:id', async () => {
      vi.spyOn(clientModule.apiClient, 'request').mockResolvedValue(null)
      await deleteInstrument(1)
      expect(clientModule.apiClient.request).toHaveBeenCalledWith(
        '/api/v1/instruments/1',
        expect.objectContaining({ method: 'DELETE' })
      )
    })
  })
})
