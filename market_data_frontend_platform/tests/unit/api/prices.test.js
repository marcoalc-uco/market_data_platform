import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getPrices, getLatestPrice } from '../../../src/api/prices.js'
import * as clientModule from '../../../src/api/client.js'

const mockPrice = {
  id: 1,
  instrument_id: 1,
  open: 100,
  high: 110,
  low: 95,
  close: 105,
  volume: 5000000,
}

describe('prices API', () => {
  beforeEach(() => {
    vi.spyOn(clientModule.apiClient, 'request').mockResolvedValue(mockPrice)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getPrices', () => {
    it('calls GET /api/v1/prices/:instrumentId', async () => {
      await getPrices(1, {})
      const [url] = clientModule.apiClient.request.mock.calls[0]
      expect(url).toContain('/api/v1/prices/1')
    })

    it('appends query params (start_date, end_date, skip, limit)', async () => {
      await getPrices(1, { start_date: '2024-01-01', end_date: '2024-12-31', limit: '100' })
      const [url] = clientModule.apiClient.request.mock.calls[0]
      expect(url).toContain('start_date=2024-01-01')
      expect(url).toContain('end_date=2024-12-31')
      expect(url).toContain('limit=100')
    })
  })

  describe('getLatestPrice', () => {
    it('calls GET /api/v1/prices/:instrumentId/latest', async () => {
      await getLatestPrice(1)
      expect(clientModule.apiClient.request).toHaveBeenCalledWith('/api/v1/prices/1/latest')
    })

    it('returns the latest price object', async () => {
      const result = await getLatestPrice(1)
      expect(result).toEqual(mockPrice)
    })
  })
})
