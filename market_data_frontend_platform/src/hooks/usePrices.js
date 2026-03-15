import { useQuery } from '@tanstack/react-query'
import { getPrices } from '../api/prices.js'

/**
 * Fetches OHLCV price series for an instrument.
 *
 * @param {number|string} instrumentId - The instrument ID.
 * @param {Object} params - Query params: { start_date, end_date, limit }.
 * @returns {import('@tanstack/react-query').UseQueryResult}
 */
export function usePrices(instrumentId, params = {}) {
  return useQuery({
    queryKey: ['prices', instrumentId, params],
    queryFn: () => getPrices(instrumentId, params),
    enabled: Boolean(instrumentId),
  })
}
