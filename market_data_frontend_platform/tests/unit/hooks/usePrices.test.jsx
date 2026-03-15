import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { usePrices } from '../../../src/hooks/usePrices.js'
import * as pricesApi from '../../../src/api/prices.js'

const PRICES = [
  {
    id: 1,
    instrument_id: 42,
    timestamp: '2024-01-15T00:00:00',
    open: '100.00',
    high: '110.00',
    low: '95.00',
    close: '105.00',
    volume: 5000000,
  },
  {
    id: 2,
    instrument_id: 42,
    timestamp: '2024-01-16T00:00:00',
    open: '105.00',
    high: '115.00',
    low: '102.00',
    close: '112.00',
    volume: 4000000,
  },
]

function wrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  // eslint-disable-next-line react/display-name
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('usePrices', () => {
  beforeEach(() => {
    vi.spyOn(pricesApi, 'getPrices').mockResolvedValue(PRICES)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns price data from the API', async () => {
    const { result } = renderHook(() => usePrices(42, {}), { wrapper: wrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual(PRICES)
  })

  it('calls getPrices with the provided instrumentId and params', async () => {
    const params = { start_date: '2024-01-01', end_date: '2024-12-31' }
    renderHook(() => usePrices(42, params), { wrapper: wrapper() })
    await waitFor(() => expect(pricesApi.getPrices).toHaveBeenCalledWith(42, params))
  })

  it('exposes isLoading while the query is pending', () => {
    vi.spyOn(pricesApi, 'getPrices').mockReturnValue(new Promise(() => {}))
    const { result } = renderHook(() => usePrices(42, {}), { wrapper: wrapper() })
    expect(result.current.isLoading).toBe(true)
  })

  it('does not fetch when instrumentId is falsy', async () => {
    renderHook(() => usePrices(null, {}), { wrapper: wrapper() })
    await new Promise((r) => setTimeout(r, 50))
    expect(pricesApi.getPrices).not.toHaveBeenCalled()
  })
})
