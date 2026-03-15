import PropTypes from 'prop-types'
import styles from './DateRangePicker.module.css'

/**
 * Date range picker with start and end date inputs.
 *
 * @param {Object}   props
 * @param {string}   props.startDate - Selected start date (YYYY-MM-DD).
 * @param {string}   props.endDate   - Selected end date (YYYY-MM-DD).
 * @param {Function} props.onChange  - Called with { startDate, endDate } on any change.
 */
export default function DateRangePicker({ startDate, endDate, onChange }) {
  const handleStart = (e) => onChange({ startDate: e.target.value, endDate })
  const handleEnd = (e) => onChange({ startDate, endDate: e.target.value })

  return (
    <div className={styles.container}>
      <label className={styles.field}>
        <span className={styles.label}>From</span>
        <input
          type="date"
          className={styles.input}
          value={startDate}
          onChange={handleStart}
          aria-label="Start date"
        />
      </label>
      <label className={styles.field}>
        <span className={styles.label}>To</span>
        <input
          type="date"
          className={styles.input}
          value={endDate}
          onChange={handleEnd}
          aria-label="End date"
        />
      </label>
    </div>
  )
}

DateRangePicker.propTypes = {
  startDate: PropTypes.string.isRequired,
  endDate: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
}
