import { useQuery } from '@tanstack/react-query'
import { getInstrument } from '../api/instruments.js'

/**
 * Fetches data for a specific instrument.
 * @param {string|number} id - The ID of the instrument to fetch
 */
export function useInstrument(id) {
  return useQuery({
    queryKey: ['instrument', id],
    queryFn: () => getInstrument(id),
    enabled: !!id,
  })
}
