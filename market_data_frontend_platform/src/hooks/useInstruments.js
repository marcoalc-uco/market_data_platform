import { useQuery } from '@tanstack/react-query'
import { getInstruments } from '../api/instruments.js'

/**
 * Fetches the instruments list with optional filters and pagination.
 * @param {Object} params - Query params: asset_type, is_active, skip, limit
 */
export function useInstruments(params = {}) {
  return useQuery({
    queryKey: ['instruments', params],
    queryFn: () => getInstruments(params),
  })
}
