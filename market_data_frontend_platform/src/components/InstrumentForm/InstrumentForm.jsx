import { useState } from 'react'
import PropTypes from 'prop-types'
import styles from './InstrumentForm.module.css'

// Must match InstrumentType enum values defined in the backend (lowercase)
const ASSET_TYPES = ['stock', 'index', 'crypto']

const EMPTY = { symbol: '', name: '', asset_type: 'stock', exchange: '', is_active: true }

/**
 * Modal form for creating or editing an instrument.
 * When `instrument` is null/undefined the form is in create mode.
 *
 * In edit mode, `symbol` and `asset_type` are shown as read-only because
 * the backend does not allow changing them after creation.
 * Only `name`, `exchange`, and `is_active` are editable.
 */
export default function InstrumentForm({ instrument, onSubmit, onClose, isLoading, error }) {
  const isEdit = Boolean(instrument)
  const [fields, setFields] = useState(instrument ?? EMPTY)

  const set = (key, value) => setFields((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(fields)
  }

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true">
      <div className={styles.modal}>
        <h2>{isEdit ? 'Edit Instrument' : 'Add Instrument'}</h2>

        {error && (
          <p role="alert" className={styles.error}>
            {error.message}
          </p>
        )}

        <form onSubmit={handleSubmit}>
          {/* Symbol — immutable after creation */}
          <div className={styles.field}>
            <label htmlFor="symbol">Symbol</label>
            <input
              id="symbol"
              value={fields.symbol}
              onChange={(e) => set('symbol', e.target.value)}
              disabled={isEdit}
              required={!isEdit}
            />
          </div>

          {/* Name — always editable */}
          <div className={styles.field}>
            <label htmlFor="name">Name</label>
            <input
              id="name"
              value={fields.name}
              onChange={(e) => set('name', e.target.value)}
              required
            />
          </div>

          {/* Asset Type — immutable after creation */}
          <div className={styles.field}>
            <label htmlFor="asset_type">Asset Type</label>
            <select
              id="asset_type"
              value={fields.asset_type}
              onChange={(e) => set('asset_type', e.target.value)}
              disabled={isEdit}
            >
              {ASSET_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Exchange — always editable */}
          <div className={styles.field}>
            <label htmlFor="exchange">Exchange</label>
            <input
              id="exchange"
              value={fields.exchange}
              onChange={(e) => set('exchange', e.target.value)}
              placeholder="e.g. NASDAQ, NYSE, CRYPTO"
              required
            />
          </div>

          <label className={styles.checkLabel}>
            <input
              type="checkbox"
              checked={fields.is_active}
              onChange={(e) => set('is_active', e.target.checked)}
            />
            Active
          </label>

          <div className={styles.actions}>
            <button type="button" onClick={onClose} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

InstrumentForm.propTypes = {
  /** Instrument to edit. Null/undefined for create mode. */
  instrument: PropTypes.shape({
    id: PropTypes.number,
    symbol: PropTypes.string,
    name: PropTypes.string,
    asset_type: PropTypes.string,
    exchange: PropTypes.string,
    is_active: PropTypes.bool,
  }),
  /** Called with the form data object on submit */
  onSubmit: PropTypes.func.isRequired,
  /** Called when the user cancels or the form should close */
  onClose: PropTypes.func.isRequired,
  /** Disables buttons and shows "Saving…" text while true */
  isLoading: PropTypes.bool,
  /** Error from the mutation — displayed as an alert */
  error: PropTypes.shape({ message: PropTypes.string }),
}
