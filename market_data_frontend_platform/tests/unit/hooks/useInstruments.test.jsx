import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useInstruments } from '../../../src/hooks/useInstruments.js'
import * as instrumentsApi from '../../../src/api/instruments.js'

vi.mock('../../../src/api/instruments.js')

const INSTRUMENTS = [
  { id: 1, symbol: 'AAPL', name: 'Apple', asset_type: 'STOCK', is_active: true },
  { id: 2, symbol: 'BTC', name: 'Bitcoin', asset_type: 'CRYPTO', is_active: false },
]

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useInstruments', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns data from the API', async () => {
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)

    const { result } = renderHook(() => useInstruments(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual(INSTRUMENTS)
  })

  it('calls getInstruments with the provided params', async () => {
    instrumentsApi.getInstruments.mockResolvedValue([])
    const params = { asset_type: 'STOCK', skip: 0, limit: 20 }

    renderHook(() => useInstruments(params), { wrapper: createWrapper() })

    await waitFor(() =>
      expect(instrumentsApi.getInstruments).toHaveBeenCalledWith(params)
    )
  })

  it('exposes isLoading while the query is pending', () => {
    instrumentsApi.getInstruments.mockImplementation(
      () => new Promise(() => {}) // never resolves
    )

    const { result } = renderHook(() => useInstruments(), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(true)
  })

  it('exposes error when the API rejects', async () => {
    instrumentsApi.getInstruments.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useInstruments(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(result.current.error.message).toBe('Network error')
  })
})
