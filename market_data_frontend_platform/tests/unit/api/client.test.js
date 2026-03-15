import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Import after stubbing env
vi.stubEnv('VITE_API_URL', 'http://testserver')

const { apiClient } = await import('../../../src/api/client.js')

describe('apiClient.request', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sends request to VITE_API_URL base + path', async () => {
    fetch.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ id: 1 }) })

    await apiClient.request('/api/v1/instruments')

    expect(fetch).toHaveBeenCalledWith('http://testserver/api/v1/instruments', expect.any(Object))
  })

  it('always sends Content-Type: application/json', async () => {
    fetch.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({}) })

    await apiClient.request('/api/v1/instruments')

    const [, options] = fetch.mock.calls[0]
    expect(options.headers['Content-Type']).toBe('application/json')
  })

  it('attaches Authorization header when token in localStorage', async () => {
    localStorage.setItem('token', 'my-jwt-token')
    fetch.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({}) })

    await apiClient.request('/api/v1/instruments')

    const [, options] = fetch.mock.calls[0]
    expect(options.headers['Authorization']).toBe('Bearer my-jwt-token')
  })

  it('omits Authorization header when no token in localStorage', async () => {
    fetch.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({}) })

    await apiClient.request('/api/v1/instruments')

    const [, options] = fetch.mock.calls[0]
    expect(options.headers).not.toHaveProperty('Authorization')
  })

  it('returns parsed JSON on OK response', async () => {
    const data = [{ id: 1, symbol: 'AAPL' }]
    fetch.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve(data) })

    const result = await apiClient.request('/api/v1/instruments')

    expect(result).toEqual(data)
  })

  it('returns null on 204 No Content', async () => {
    fetch.mockResolvedValue({ ok: true, status: 204, json: () => Promise.resolve(null) })

    const result = await apiClient.request('/api/v1/instruments/1', { method: 'DELETE' })

    expect(result).toBeNull()
  })

  it('clears token and redirects to /login on 401', async () => {
    localStorage.setItem('token', 'expired-token')
    const hrefSpy = vi.fn()
    Object.defineProperty(window, 'location', {
      value: { href: '', set href(v) { hrefSpy(v); this._href = v }, get href() { return this._href } },
      writable: true,
      configurable: true,
    })

    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: () => Promise.resolve({ detail: 'Not authenticated' }),
    })

    await expect(apiClient.request('/api/v1/instruments')).rejects.toThrow('Session expired')

    expect(localStorage.getItem('token')).toBeNull()
    expect(hrefSpy).toHaveBeenCalledWith('/login')
  })

  it('throws Error with backend detail message on non-OK response', async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({ detail: 'Instrument not found' }),
    })

    await expect(apiClient.request('/api/v1/instruments/99')).rejects.toThrow('Instrument not found')
  })

  it('throws Error with statusText when no detail in error body', async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.resolve({}),
    })

    await expect(apiClient.request('/api/v1/instruments')).rejects.toThrow('Internal Server Error')
  })

  it('forwards method and body from options', async () => {
    fetch.mockResolvedValue({ ok: true, status: 201, json: () => Promise.resolve({ id: 2 }) })
    const body = JSON.stringify({ symbol: 'TSLA', name: 'Tesla' })

    await apiClient.request('/api/v1/instruments', { method: 'POST', body })

    const [, options] = fetch.mock.calls[0]
    expect(options.method).toBe('POST')
    expect(options.body).toBe(body)
  })
})
