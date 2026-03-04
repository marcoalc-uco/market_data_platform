import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useAuth } from '../../../src/hooks/useAuth.js'
import * as authApi from '../../../src/api/auth.js'

vi.mock('../../../src/api/auth.js')

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('isAuthenticated is false when no token in localStorage', () => {
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('isAuthenticated is true when token exists in localStorage', () => {
    localStorage.setItem('token', 'existing-token')
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('isLoading is false initially', () => {
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })
    expect(result.current.isLoading).toBe(false)
  })

  it('error is null initially', () => {
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })
    expect(result.current.error).toBeNull()
  })

  it('login calls the auth API with credentials', async () => {
    authApi.login.mockResolvedValue({ access_token: 'new-token' })
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })

    act(() => {
      result.current.login({ username: 'admin', password: 'secret' })
    })

    await waitFor(() => {
      expect(authApi.login.mock.calls[0][0]).toEqual({ username: 'admin', password: 'secret' })
    })
  })

  it('stores token in localStorage after successful login', async () => {
    authApi.login.mockResolvedValue({ access_token: 'new-token' })
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })

    act(() => {
      result.current.login({ username: 'admin', password: 'secret' })
    })

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('new-token')
    })
  })

  it('logout removes token from localStorage', () => {
    localStorage.setItem('token', 'some-token')
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })

    act(() => {
      result.current.logout()
    })

    expect(localStorage.getItem('token')).toBeNull()
  })

  it('sets error when login fails', async () => {
    authApi.login.mockRejectedValue(new Error('Invalid credentials'))
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() })

    act(() => {
      result.current.login({ username: 'admin', password: 'wrong' })
    })

    await waitFor(() => {
      expect(result.current.error).toBeInstanceOf(Error)
      expect(result.current.error.message).toBe('Invalid credentials')
    })
  })
})
