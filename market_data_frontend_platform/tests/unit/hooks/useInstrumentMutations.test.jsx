import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useInstrumentMutations } from '../../../src/hooks/useInstrumentMutations.js'
import * as instrumentsApi from '../../../src/api/instruments.js'

vi.mock('../../../src/api/instruments.js')

const INSTRUMENT = { id: 1, symbol: 'AAPL', name: 'Apple', asset_type: 'STOCK', is_active: true }

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { mutations: { retry: false } },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useInstrumentMutations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('create calls createInstrument with the provided data', async () => {
    instrumentsApi.createInstrument.mockResolvedValue(INSTRUMENT)

    const { result } = renderHook(() => useInstrumentMutations(), {
      wrapper: createWrapper(),
    })

    act(() => {
      result.current.create.mutate({ symbol: 'AAPL', name: 'Apple', asset_type: 'STOCK', is_active: true })
    })

    await waitFor(() => expect(result.current.create.isSuccess).toBe(true))
    expect(instrumentsApi.createInstrument.mock.calls[0][0]).toMatchObject({
      symbol: 'AAPL',
    })
  })

  it('update calls updateInstrument with id and data', async () => {
    instrumentsApi.updateInstrument.mockResolvedValue({ ...INSTRUMENT, name: 'Apple Inc.' })

    const { result } = renderHook(() => useInstrumentMutations(), {
      wrapper: createWrapper(),
    })

    act(() => {
      result.current.update.mutate({ id: 1, data: { ...INSTRUMENT, name: 'Apple Inc.' } })
    })

    await waitFor(() => expect(result.current.update.isSuccess).toBe(true))
    expect(instrumentsApi.updateInstrument).toHaveBeenCalledWith(1, expect.objectContaining({ name: 'Apple Inc.' }))
  })

  it('remove calls deleteInstrument with the id', async () => {
    instrumentsApi.deleteInstrument.mockResolvedValue(null)

    const { result } = renderHook(() => useInstrumentMutations(), {
      wrapper: createWrapper(),
    })

    act(() => {
      result.current.remove.mutate(1)
    })

    await waitFor(() => expect(result.current.remove.isSuccess).toBe(true))
    expect(instrumentsApi.deleteInstrument.mock.calls[0][0]).toBe(1)
  })
})
