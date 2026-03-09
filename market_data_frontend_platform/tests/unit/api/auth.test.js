import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { login } from '../../../src/api/auth.js'
import * as clientModule from '../../../src/api/client.js'

describe('auth API', () => {
  beforeEach(() => {
    vi.spyOn(clientModule.apiClient, 'request').mockResolvedValue({
      access_token: 'jwt-token-123',
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls POST /api/v1/auth/token', async () => {
    await login({ username: 'admin', password: 'secret' })

    expect(clientModule.apiClient.request).toHaveBeenCalledWith(
      '/api/v1/auth/token',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('sends credentials as form-urlencoded body', async () => {
    await login({ username: 'admin', password: 'secret' })

    const [, options] = clientModule.apiClient.request.mock.calls[0]
    expect(options.headers['Content-Type']).toBe('application/x-www-form-urlencoded')
    expect(options.body).toBe('username=admin&password=secret')
  })

  it('returns the token response from the API', async () => {
    const result = await login({ username: 'admin', password: 'secret' })

    expect(result).toEqual({ access_token: 'jwt-token-123' })
  })
})
