import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useLatestPrice } from '../../../src/hooks/useLatestPrice.js'
import * as pricesApi from '../../../src/api/prices.js'

const LATEST_PRICE = {
  id: 10,
  instrument_id: 42,
  timestamp: '2024-03-01T00:00:00',
  open: '185.50',
  high: '186.20',
  low: '185.00',
  close: '185.80',
  volume: 3000000,
}

function wrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  // eslint-disable-next-line react/display-name
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useLatestPrice', () => {
  beforeEach(() => {
    vi.spyOn(pricesApi, 'getLatestPrice').mockResolvedValue(LATEST_PRICE)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns the latest price from the API', async () => {
    const { result } = renderHook(() => useLatestPrice(42), { wrapper: wrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual(LATEST_PRICE)
  })

  it('calls getLatestPrice with the instrumentId', async () => {
    renderHook(() => useLatestPrice(42), { wrapper: wrapper() })
    await waitFor(() => expect(pricesApi.getLatestPrice).toHaveBeenCalledWith(42))
  })

  it('does not fetch when instrumentId is falsy', async () => {
    renderHook(() => useLatestPrice(null), { wrapper: wrapper() })
    await new Promise((r) => setTimeout(r, 50))
    expect(pricesApi.getLatestPrice).not.toHaveBeenCalled()
  })

  it('exposes error when the API rejects', async () => {
    vi.spyOn(pricesApi, 'getLatestPrice').mockRejectedValue(new Error('Not found'))
    const { result } = renderHook(() => useLatestPrice(99), { wrapper: wrapper() })
    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(result.current.error.message).toBe('Not found')
  })
})
