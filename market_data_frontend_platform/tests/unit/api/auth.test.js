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

  it('calls POST /api/v1/auth/login', async () => {
    await login({ username: 'admin', password: 'secret' })

    expect(clientModule.apiClient.request).toHaveBeenCalledWith(
      '/api/v1/auth/login',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('sends credentials as JSON body', async () => {
    const credentials = { username: 'admin', password: 'secret' }
    await login(credentials)

    const [, options] = clientModule.apiClient.request.mock.calls[0]
    expect(options.body).toBe(JSON.stringify(credentials))
  })

  it('returns the token response from the API', async () => {
    const result = await login({ username: 'admin', password: 'secret' })

    expect(result).toEqual({ access_token: 'jwt-token-123' })
  })
})
