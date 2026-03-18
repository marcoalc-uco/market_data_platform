/**
 * Tests for Chat API functions.
 *
 * Covers:
 *   - streamChat: SSE parsing, token callback, auth, error handling
 *   - uploadDocument: FormData construction, auth, error handling
 *   - listDocuments: fetch call, auth, error handling
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { streamChat, uploadDocument, listDocuments } from './chat.js'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a ReadableStream that yields SSE lines */
function makeSSEStream(lines) {
  const encoder = new TextEncoder()
  const text = lines.map((l) => `data: ${l}\n\n`).join('')
  return new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(text))
      controller.close()
    },
  })
}

function mockFetchOk(body, headers = {}) {
  return vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    headers: new Headers({ 'content-type': 'text/event-stream', ...headers }),
    body: typeof body === 'string' ? makeSSEStream(body.split('||')) : body,
    json: async () => (typeof body === 'object' ? body : JSON.parse(body)),
  })
}

function mockFetchError(status, detail) {
  return vi.fn().mockResolvedValue({
    ok: false,
    status,
    statusText: 'Error',
    json: async () => ({ detail }),
  })
}

// ---------------------------------------------------------------------------
// Setup / Teardown
// ---------------------------------------------------------------------------

const originalFetch = globalThis.fetch
const originalLocation = window.location

beforeEach(() => {
  localStorage.clear()
  localStorage.setItem('token', 'test-jwt-token')
})

afterEach(() => {
  globalThis.fetch = originalFetch
  vi.restoreAllMocks()
})

// ---------------------------------------------------------------------------
// streamChat
// ---------------------------------------------------------------------------

describe('streamChat', () => {
  it('should call the correct endpoint with POST', async () => {
    globalThis.fetch = mockFetchOk(makeSSEStream(['"Hello"', '[DONE]']))

    const onToken = vi.fn()
    await streamChat(42, 'test message', [], onToken)

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/chat/42'),
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('should send message and history in the body', async () => {
    globalThis.fetch = mockFetchOk(makeSSEStream(['"ok"', '[DONE]']))

    const history = [{ role: 'user', content: 'prev' }]
    await streamChat(1, 'hello', history, vi.fn())

    const body = JSON.parse(globalThis.fetch.mock.calls[0][1].body)
    expect(body.message).toBe('hello')
    expect(body.history).toEqual(history)
  })

  it('should include Authorization header when token exists', async () => {
    globalThis.fetch = mockFetchOk(makeSSEStream(['[DONE]']))

    await streamChat(1, 'test', [], vi.fn())

    const headers = globalThis.fetch.mock.calls[0][1].headers
    expect(headers.Authorization).toBe('Bearer test-jwt-token')
  })

  it('should call onToken for each SSE token', async () => {
    globalThis.fetch = mockFetchOk(makeSSEStream(['"Hello"', '" world"', '"!"', '[DONE]']))

    const onToken = vi.fn()
    await streamChat(1, 'test', [], onToken)

    expect(onToken).toHaveBeenCalledTimes(3)
    expect(onToken).toHaveBeenNthCalledWith(1, 'Hello')
    expect(onToken).toHaveBeenNthCalledWith(2, ' world')
    expect(onToken).toHaveBeenNthCalledWith(3, '!')
  })

  it('should return the full assembled response', async () => {
    globalThis.fetch = mockFetchOk(makeSSEStream(['"Hello"', '" world"', '[DONE]']))

    const result = await streamChat(1, 'test', [], vi.fn())
    expect(result).toBe('Hello world')
  })

  it('should throw on non-OK response', async () => {
    globalThis.fetch = mockFetchError(500, 'Server error')

    await expect(streamChat(1, 'test', [], vi.fn())).rejects.toThrow('Server error')
  })

  it('should redirect to login on 401', async () => {
    // Mock window.location
    delete window.location
    window.location = { href: '' }

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({}),
    })

    await expect(streamChat(1, 'test', [], vi.fn())).rejects.toThrow('Session expired')
    expect(localStorage.getItem('token')).toBeNull()
    expect(window.location.href).toBe('/login')

    window.location = originalLocation
  })

  it('should not include auth header when no token', async () => {
    localStorage.removeItem('token')
    globalThis.fetch = mockFetchOk(makeSSEStream(['[DONE]']))

    await streamChat(1, 'test', [], vi.fn())

    const headers = globalThis.fetch.mock.calls[0][1].headers
    expect(headers.Authorization).toBeUndefined()
  })

  it('should pass abort signal to fetch', async () => {
    globalThis.fetch = mockFetchOk(makeSSEStream(['[DONE]']))

    const controller = new AbortController()
    await streamChat(1, 'test', [], vi.fn(), controller.signal)

    expect(globalThis.fetch.mock.calls[0][1].signal).toBe(controller.signal)
  })
})

// ---------------------------------------------------------------------------
// uploadDocument
// ---------------------------------------------------------------------------

describe('uploadDocument', () => {
  it('should POST FormData to the documents endpoint', async () => {
    const mockResult = { filename: 'test.txt', chunks_stored: 3, instrument_id: 1 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockResult,
    })

    const file = new File(['content'], 'test.txt', { type: 'text/plain' })
    const result = await uploadDocument(1, file)

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/chat/1/documents'),
      expect.objectContaining({ method: 'POST' })
    )
    expect(result).toEqual(mockResult)
  })

  it('should send file in FormData body', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ filename: 'f.txt', chunks_stored: 1, instrument_id: 1 }),
    })

    const file = new File(['data'], 'f.txt')
    await uploadDocument(1, file)

    const body = globalThis.fetch.mock.calls[0][1].body
    expect(body).toBeInstanceOf(FormData)
    expect(body.get('file')).toBeInstanceOf(File)
  })

  it('should NOT include Content-Type header (browser sets boundary)', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ filename: 'f.txt', chunks_stored: 1, instrument_id: 1 }),
    })

    await uploadDocument(1, new File(['x'], 'f.txt'))

    const headers = globalThis.fetch.mock.calls[0][1].headers
    expect(headers['Content-Type']).toBeUndefined()
  })

  it('should include Authorization header', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ filename: 'f.txt', chunks_stored: 1, instrument_id: 1 }),
    })

    await uploadDocument(1, new File(['x'], 'f.txt'))

    const headers = globalThis.fetch.mock.calls[0][1].headers
    expect(headers.Authorization).toBe('Bearer test-jwt-token')
  })

  it('should throw on error response', async () => {
    globalThis.fetch = mockFetchError(422, 'Unsupported file type')

    await expect(uploadDocument(1, new File(['x'], 'f.png'))).rejects.toThrow(
      'Unsupported file type'
    )
  })

  it('should redirect to login on 401', async () => {
    delete window.location
    window.location = { href: '' }

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({}),
    })

    await expect(uploadDocument(1, new File(['x'], 'f.txt'))).rejects.toThrow('Session expired')
    expect(window.location.href).toBe('/login')

    window.location = originalLocation
  })
})

// ---------------------------------------------------------------------------
// listDocuments
// ---------------------------------------------------------------------------

describe('listDocuments', () => {
  it('should GET the documents endpoint', async () => {
    const mockResult = { instrument_id: 1, documents: [] }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockResult,
    })

    const result = await listDocuments(1)

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/chat/1/documents'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-jwt-token',
        }),
      })
    )
    expect(result).toEqual(mockResult)
  })

  it('should return documents with chunk counts', async () => {
    const mockResult = {
      instrument_id: 42,
      documents: [
        { filename: 'report.pdf', chunk_count: 12 },
        { filename: 'notes.txt', chunk_count: 3 },
      ],
    }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockResult,
    })

    const result = await listDocuments(42)
    expect(result.documents).toHaveLength(2)
    expect(result.documents[0].filename).toBe('report.pdf')
  })

  it('should throw on error response', async () => {
    globalThis.fetch = mockFetchError(500, 'Internal error')

    await expect(listDocuments(1)).rejects.toThrow('Internal error')
  })

  it('should redirect to login on 401', async () => {
    delete window.location
    window.location = { href: '' }

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({}),
    })

    await expect(listDocuments(1)).rejects.toThrow('Session expired')
    expect(window.location.href).toBe('/login')

    window.location = originalLocation
  })
})
