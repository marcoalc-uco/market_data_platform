/**
 * Tests for ChatBox component.
 *
 * Covers:
 *   - Collapsed/expanded state toggle
 *   - Empty state message
 *   - Message sending and display
 *   - Keyboard shortcuts (Enter to send, Shift+Enter for newline)
 *   - Input disabled during streaming
 *   - Document upload UI
 *   - Error display
 *   - Accessibility attributes
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import ChatBox from './ChatBox.jsx'

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock the chat API module
vi.mock('../../api/chat.js', () => ({
  streamChat: vi.fn(),
  uploadDocument: vi.fn(),
  listDocuments: vi.fn().mockResolvedValue({ documents: [] }),
}))

import { streamChat, uploadDocument, listDocuments } from '../../api/chat.js'

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

beforeEach(() => {
  vi.clearAllMocks()
  listDocuments.mockResolvedValue({ documents: [] })
})

afterEach(() => {
  vi.restoreAllMocks()
})

const defaultProps = {
  instrumentId: 1,
  instrumentName: 'Apple Inc.',
}

// ---------------------------------------------------------------------------
// Collapsed / Expanded State
// ---------------------------------------------------------------------------

describe('ChatBox toggle', () => {
  it('should render collapsed by default', () => {
    render(<ChatBox {...defaultProps} />)

    // Header visible
    expect(screen.getByText(/Ask about Apple Inc./)).toBeInTheDocument()
    // Input area NOT visible
    expect(screen.queryByPlaceholderText(/Ask about Apple Inc/)).not.toBeInTheDocument()
  })

  it('should expand when header is clicked', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    // Input area now visible
    expect(screen.getByPlaceholderText(/Ask about Apple Inc/)).toBeInTheDocument()
  })

  it('should collapse when header is clicked again', async () => {
    render(<ChatBox {...defaultProps} />)

    const header = screen.getByText(/Ask about Apple Inc./)
    await act(async () => {
      fireEvent.click(header)
    })
    expect(screen.getByPlaceholderText(/Ask about Apple Inc/)).toBeInTheDocument()

    await act(async () => {
      fireEvent.click(header)
    })
    expect(screen.queryByPlaceholderText(/Ask about Apple Inc/)).not.toBeInTheDocument()
  })

  it('should have correct aria-expanded attribute', async () => {
    render(<ChatBox {...defaultProps} />)

    const toggle = screen.getByRole('button', { name: /Toggle chat/i })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')

    await act(async () => {
      fireEvent.click(toggle)
    })
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
  })

  it('should toggle on Enter key press', async () => {
    render(<ChatBox {...defaultProps} />)

    const toggle = screen.getByRole('button', { name: /Toggle chat/i })

    await act(async () => {
      fireEvent.keyDown(toggle, { key: 'Enter' })
    })

    expect(screen.getByPlaceholderText(/Ask about Apple Inc/)).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Empty State
// ---------------------------------------------------------------------------

describe('ChatBox empty state', () => {
  it('should show empty state message when no messages', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(screen.getByText(/Ask anything about/)).toBeInTheDocument()
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Message Input
// ---------------------------------------------------------------------------

describe('ChatBox input', () => {
  it('should have send button disabled when input is empty', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(screen.getByRole('button', { name: /Send/ })).toBeDisabled()
  })

  it('should enable send button when input has text', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Hello' } })
    })

    expect(screen.getByRole('button', { name: /Send/ })).not.toBeDisabled()
  })

  it('should have maxLength of 2000', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    expect(input).toHaveAttribute('maxlength', '2000')
  })
})

// ---------------------------------------------------------------------------
// Sending Messages
// ---------------------------------------------------------------------------

describe('ChatBox send message', () => {
  it('should call streamChat when send button is clicked', async () => {
    streamChat.mockImplementation(async (id, msg, history, onToken) => {
      onToken('response')
      return 'response'
    })

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    await act(async () => {
      fireEvent.change(input, { target: { value: 'What is the trend?' } })
    })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Send/ }))
    })

    expect(streamChat).toHaveBeenCalledWith(
      1,
      'What is the trend?',
      expect.any(Array),
      expect.any(Function),
      expect.any(Object) // AbortSignal
    )
  })

  it('should display user message after sending', async () => {
    streamChat.mockImplementation(async () => 'ok')

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    await act(async () => {
      fireEvent.change(input, { target: { value: 'My question' } })
    })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Send/ }))
    })

    expect(screen.getByText('My question')).toBeInTheDocument()
  })

  it('should clear input after sending', async () => {
    streamChat.mockImplementation(async () => 'ok')

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    await act(async () => {
      fireEvent.change(input, { target: { value: 'question' } })
    })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Send/ }))
    })

    expect(input.value).toBe('')
  })

  it('should display assistant response from streaming', async () => {
    streamChat.mockImplementation(async (id, msg, history, onToken) => {
      onToken('The trend is bullish.')
      return 'The trend is bullish.'
    })

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText(/Ask about Apple Inc/), {
        target: { value: 'trend?' },
      })
    })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Send/ }))
    })

    await waitFor(() => {
      expect(screen.getByText('The trend is bullish.')).toBeInTheDocument()
    })
  })

  it('should not send empty or whitespace-only messages', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText(/Ask about Apple Inc/), {
        target: { value: '   ' },
      })
    })

    // Button should be disabled for whitespace
    expect(screen.getByRole('button', { name: /Send/ })).toBeDisabled()
    expect(streamChat).not.toHaveBeenCalled()
  })
})

// ---------------------------------------------------------------------------
// Keyboard Shortcuts
// ---------------------------------------------------------------------------

describe('ChatBox keyboard', () => {
  it('should send on Enter key', async () => {
    streamChat.mockImplementation(async () => 'ok')

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    await act(async () => {
      fireEvent.change(input, { target: { value: 'question' } })
    })

    await act(async () => {
      fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })
    })

    expect(streamChat).toHaveBeenCalled()
  })

  it('should NOT send on Shift+Enter', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const input = screen.getByPlaceholderText(/Ask about Apple Inc/)
    await act(async () => {
      fireEvent.change(input, { target: { value: 'question' } })
    })

    await act(async () => {
      fireEvent.keyDown(input, { key: 'Enter', shiftKey: true })
    })

    expect(streamChat).not.toHaveBeenCalled()
  })
})

// ---------------------------------------------------------------------------
// Error Handling
// ---------------------------------------------------------------------------

describe('ChatBox error handling', () => {
  it('should display error message when streamChat fails', async () => {
    streamChat.mockRejectedValue(new Error('Ollama is down'))

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText(/Ask about Apple Inc/), {
        target: { value: 'question' },
      })
    })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Send/ }))
    })

    await waitFor(() => {
      expect(screen.getByText('Ollama is down')).toBeInTheDocument()
    })
  })
})

// ---------------------------------------------------------------------------
// Document Upload UI
// ---------------------------------------------------------------------------

describe('ChatBox documents', () => {
  it('should show Upload button when expanded', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(screen.getByRole('button', { name: /Upload/ })).toBeInTheDocument()
  })

  it('should show RAG Documents section', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(screen.getByText('RAG Documents')).toBeInTheDocument()
  })

  it('should display document chips when documents exist', async () => {
    listDocuments.mockResolvedValue({
      documents: [
        { filename: 'report.pdf', chunk_count: 12 },
        { filename: 'notes.txt', chunk_count: 3 },
      ],
    })

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    await waitFor(() => {
      expect(screen.getByText(/report\.pdf/)).toBeInTheDocument()
      expect(screen.getByText(/notes\.txt/)).toBeInTheDocument()
    })
  })

  it('should show upload status after successful upload', async () => {
    uploadDocument.mockResolvedValue({
      filename: 'data.txt',
      chunks_stored: 5,
      instrument_id: 1,
    })

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    // Simulate file selection
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['content'], 'data.txt', { type: 'text/plain' })

    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } })
    })

    await waitFor(() => {
      expect(screen.getByText(/data\.txt/)).toBeInTheDocument()
      expect(screen.getByText(/5 chunks indexed/)).toBeInTheDocument()
    })
  })

  it('should show error on upload failure', async () => {
    uploadDocument.mockRejectedValue(new Error('File too large'))

    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['x'], 'big.txt')

    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } })
    })

    await waitFor(() => {
      expect(screen.getByText(/File too large/)).toBeInTheDocument()
    })
  })

  it('should accept .pdf, .md, and .txt files', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    const fileInput = document.querySelector('input[type="file"]')
    expect(fileInput.accept).toBe('.pdf,.md,.txt')
  })

  it('should load documents when chat is opened', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(listDocuments).toHaveBeenCalledWith(1)
  })
})

// ---------------------------------------------------------------------------
// Accessibility
// ---------------------------------------------------------------------------

describe('ChatBox accessibility', () => {
  it('should have role="log" on messages area', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(screen.getByRole('log')).toBeInTheDocument()
  })

  it('should have aria-live="polite" on messages area', async () => {
    render(<ChatBox {...defaultProps} />)

    await act(async () => {
      fireEvent.click(screen.getByText(/Ask about Apple Inc./))
    })

    expect(screen.getByRole('log')).toHaveAttribute('aria-live', 'polite')
  })

  it('header should be focusable with tabIndex', () => {
    render(<ChatBox {...defaultProps} />)

    const toggle = screen.getByRole('button', { name: /Toggle chat/i })
    expect(toggle).toHaveAttribute('tabindex', '0')
  })
})
