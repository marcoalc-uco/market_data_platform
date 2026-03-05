import { useQuery } from '@tanstack/react-query'
import { getLatestPrice } from '../api/prices.js'

/**
 * Fetches the latest price snapshot for an instrument.
 *
 * @param {number|string} instrumentId - The instrument ID.
 * @returns {import('@tanstack/react-query').UseQueryResult}
 */
export function useLatestPrice(instrumentId) {
  return useQuery({
    queryKey: ['latestPrice', instrumentId],
    queryFn: () => getLatestPrice(instrumentId),
    enabled: Boolean(instrumentId),
  })
}
