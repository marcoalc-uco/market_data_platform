/**
 * Chat API functions — Ollama LLM streaming + RAG document management.
 *
 * Uses SSE (Server-Sent Events) for real-time token streaming from the
 * backend chat endpoint powered by a local Ollama model.
 */

const getBaseUrl = () => import.meta.env.VITE_API_URL ?? ''

/**
 * Stream a chat response for a given instrument.
 *
 * @param {number}   instrumentId  - Instrument to discuss.
 * @param {string}   message       - User message (1–2000 chars).
 * @param {Array}    history       - Previous messages [{role, content}, …].
 * @param {function} onToken       - Called with each text token as it arrives.
 * @param {AbortSignal} [signal]   - Optional abort signal.
 * @returns {Promise<string>} The complete assembled response.
 */
export async function streamChat(instrumentId, message, history, onToken, signal) {
  const token = localStorage.getItem('token')

  const response = await fetch(`${getBaseUrl()}/api/v1/chat/${instrumentId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, history }),
    signal,
  })

  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Session expired')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? response.statusText)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let fullResponse = ''
  let buffer = ''

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    // Keep the last (possibly incomplete) line in the buffer
    buffer = lines.pop() || ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed.startsWith('data: ')) continue

      const payload = trimmed.slice(6)
      if (payload === '[DONE]') break

      try {
        const tokenText = JSON.parse(payload)
        if (typeof tokenText === 'string' && !tokenText.startsWith('Error:')) {
          fullResponse += tokenText
          onToken(tokenText)
        } else if (typeof tokenText === 'string') {
          throw new Error(tokenText)
        }
      } catch {
        // Skip malformed SSE lines
      }
    }
  }

  return fullResponse
}

/**
 * Upload a document for RAG context.
 *
 * @param {number} instrumentId - Target instrument.
 * @param {File}   file         - File to upload (.pdf, .md, .txt).
 * @returns {Promise<{filename: string, chunks_stored: number, instrument_id: number}>}
 */
export async function uploadDocument(instrumentId, file) {
  const token = localStorage.getItem('token')
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${getBaseUrl()}/api/v1/chat/${instrumentId}/documents`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  })

  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Session expired')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? response.statusText)
  }

  return response.json()
}

/**
 * List all uploaded documents for an instrument.
 *
 * @param {number} instrumentId
 * @returns {Promise<{instrument_id: number, documents: Array<{filename: string, chunk_count: number}>}>}
 */
export async function listDocuments(instrumentId) {
  const token = localStorage.getItem('token')

  const response = await fetch(`${getBaseUrl()}/api/v1/chat/${instrumentId}/documents`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Session expired')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? response.statusText)
  }

  return response.json()
}
