import PropTypes from 'prop-types'
import styles from './InstrumentFilters.module.css'

// Must match InstrumentType enum values defined in the backend (lowercase)
const ASSET_TYPES = ['stock', 'index', 'crypto']

/**
 * Filter bar for the instruments list.
 * Emits the full updated filters object via onChange on every change.
 */
export default function InstrumentFilters({ filters, onChange }) {
  return (
    <div className={styles.bar}>
      <label htmlFor="asset-type-filter" className={styles.label}>
        Asset Type
      </label>
      <select
        id="asset-type-filter"
        className={styles.select}
        value={filters.asset_type ?? ''}
        onChange={(e) => onChange({ ...filters, asset_type: e.target.value || undefined })}
      >
        <option value="">All</option>
        {ASSET_TYPES.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>

      <label className={styles.checkLabel}>
        <input
          type="checkbox"
          checked={filters.is_active ?? false}
          onChange={(e) => onChange({ ...filters, is_active: e.target.checked || undefined })}
        />
        Active only
      </label>
    </div>
  )
}

InstrumentFilters.propTypes = {
  /** Current filter state: { asset_type?, is_active? } */
  filters: PropTypes.shape({
    asset_type: PropTypes.string,
    is_active: PropTypes.bool,
  }).isRequired,
  /** Called with the new filters object on every change */
  onChange: PropTypes.func.isRequired,
}
