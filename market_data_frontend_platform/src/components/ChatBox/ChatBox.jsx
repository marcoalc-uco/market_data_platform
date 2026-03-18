import PropTypes from 'prop-types'
import { useState, useRef, useEffect, useCallback } from 'react'
import { streamChat, uploadDocument, listDocuments } from '../../api/chat.js'
import styles from './ChatBox.module.css'

/**
 * ChatBox — conversational assistant for a financial instrument.
 *
 * Streams responses from a local Ollama model via SSE and supports
 * RAG by letting users upload PDF / Markdown / text documents.
 *
 * @param {{ instrumentId: number, instrumentName: string }} props
 */
export default function ChatBox({ instrumentId, instrumentName }) {
  // ── State ────────────────────────────────────────────────
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState(null)
  const [isOpen, setIsOpen] = useState(false)

  // Documents (RAG)
  const [documents, setDocuments] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const abortRef = useRef(null)
  const fileInputRef = useRef(null)

  // ── Auto-scroll ──────────────────────────────────────────
  const scrollToBottom = useCallback(() => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // ── Load documents on open ───────────────────────────────
  useEffect(() => {
    if (!isOpen) return
    listDocuments(instrumentId)
      .then((res) => setDocuments(res.documents ?? []))
      .catch(() => {}) // silent — non-critical
  }, [isOpen, instrumentId])

  // ── Cleanup abort controller on unmount ──────────────────
  useEffect(() => {
    return () => abortRef.current?.abort()
  }, [])

  // ── Build history for the API ────────────────────────────
  const buildHistory = () =>
    messages
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map(({ role, content }) => ({ role, content }))

  // ── Send message ─────────────────────────────────────────
  const handleSend = async () => {
    const trimmed = input.trim()
    if (!trimmed || isStreaming) return

    const userMsg = { role: 'user', content: trimmed }
    const assistantMsg = { role: 'assistant', content: '', streaming: true }

    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setInput('')
    setError(null)
    setIsStreaming(true)

    abortRef.current = new AbortController()

    try {
      await streamChat(
        instrumentId,
        trimmed,
        buildHistory(),
        (token) => {
          setMessages((prev) => {
            const updated = [...prev]
            const last = updated[updated.length - 1]
            updated[updated.length - 1] = { ...last, content: last.content + token }
            return updated
          })
        },
        abortRef.current.signal
      )

      // Mark streaming complete
      setMessages((prev) => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        updated[updated.length - 1] = { ...last, streaming: false }
        return updated
      })
    } catch (err) {
      if (err.name === 'AbortError') return
      setError(err.message)
      // Remove the empty assistant placeholder on error
      setMessages((prev) => {
        const updated = [...prev]
        if (updated[updated.length - 1]?.content === '') {
          updated.pop()
        } else {
          const last = updated[updated.length - 1]
          updated[updated.length - 1] = { ...last, streaming: false }
        }
        return updated
      })
    } finally {
      setIsStreaming(false)
      abortRef.current = null
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // ── Document upload ──────────────────────────────────────
  const handleUploadClick = () => fileInputRef.current?.click()

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    e.target.value = '' // reset so same file can be re-uploaded

    setIsUploading(true)
    setUploadStatus(null)

    try {
      const result = await uploadDocument(instrumentId, file)
      setUploadStatus(`✓ ${result.filename} — ${result.chunks_stored} chunks indexed`)
      // Refresh doc list
      const res = await listDocuments(instrumentId)
      setDocuments(res.documents ?? [])
    } catch (err) {
      setUploadStatus(`✗ ${err.message}`)
    } finally {
      setIsUploading(false)
    }
  }

  // ── Render ───────────────────────────────────────────────
  return (
    <div className={styles.chatBox}>
      {/* Collapsible header */}
      <div
        className={styles.chatHeader}
        onClick={() => setIsOpen((o) => !o)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setIsOpen((o) => !o)}
        aria-expanded={isOpen}
        aria-label="Toggle chat"
      >
        <span className={styles.chatHeaderLeft}>
          <span className={styles.chatHeaderIcon}>💬</span>
          Ask about {instrumentName}
        </span>
        <span className={`${styles.toggleIcon} ${isOpen ? styles.toggleIconOpen : ''}`}>▼</span>
      </div>

      {isOpen && (
        <>
          {/* Messages */}
          <div className={styles.messages} role="log" aria-live="polite">
            {messages.length === 0 && (
              <div className={styles.emptyState}>
                <span className={styles.emptyIcon}>🤖</span>
                <span>
                  Ask anything about <strong>{instrumentName}</strong>. The AI has access to recent
                  price data
                  {documents.length > 0 && ' and your uploaded documents'}.
                </span>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`${styles.message} ${
                  msg.role === 'user' ? styles.userMessage : styles.assistantMessage
                } ${msg.streaming ? styles.streamingCursor : ''}`}
              >
                {msg.content}
              </div>
            ))}

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div ref={messagesEndRef} />
          </div>

          {/* Documents (RAG) */}
          <div className={styles.docsSection}>
            <div className={styles.docsHeader}>
              <span className={styles.docsTitle}>RAG Documents</span>
              <button
                className={styles.uploadBtn}
                onClick={handleUploadClick}
                disabled={isUploading}
              >
                {isUploading ? 'Uploading…' : '+ Upload'}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.md,.txt"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
            </div>

            {documents.length > 0 && (
              <div className={styles.docsList}>
                {documents.map((doc) => (
                  <span key={doc.filename} className={styles.docChip}>
                    📄 {doc.filename}
                    <span className={styles.docChipCount}>{doc.chunk_count}</span>
                  </span>
                ))}
              </div>
            )}

            {uploadStatus && (
              <div
                className={uploadStatus.startsWith('✓') ? styles.uploadStatus : styles.uploadError}
              >
                {uploadStatus}
              </div>
            )}
          </div>

          {/* Input */}
          <div className={styles.inputArea}>
            <textarea
              ref={inputRef}
              className={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask about ${instrumentName}…`}
              disabled={isStreaming}
              rows={1}
              maxLength={2000}
            />
            <button
              className={styles.sendBtn}
              onClick={handleSend}
              disabled={isStreaming || !input.trim()}
            >
              {isStreaming ? '…' : 'Send'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}

ChatBox.propTypes = {
  instrumentId: PropTypes.number.isRequired,
  instrumentName: PropTypes.string.isRequired,
}
