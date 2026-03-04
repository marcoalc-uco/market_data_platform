import PropTypes from 'prop-types'
import styles from './Pagination.module.css'

/**
 * Previous / Next pagination control.
 * `hasMore` should be true when the current page has `limit` items
 * (i.e. there may be more pages).
 */
export default function Pagination({ skip, limit, hasMore, onChange }) {
  const page = Math.floor(skip / limit) + 1

  const handlePrev = () => onChange({ skip: Math.max(0, skip - limit), limit })
  const handleNext = () => onChange({ skip: skip + limit, limit })

  return (
    <div className={styles.pagination}>
      <button onClick={handlePrev} disabled={skip === 0} aria-label="Previous page">
        ← Prev
      </button>
      <span className={styles.info}>Page {page}</span>
      <button onClick={handleNext} disabled={!hasMore} aria-label="Next page">
        Next →
      </button>
    </div>
  )
}

Pagination.propTypes = {
  /** Current offset (number of records to skip) */
  skip: PropTypes.number.isRequired,
  /** Number of records per page */
  limit: PropTypes.number.isRequired,
  /** True when there may be more pages (current page is full) */
  hasMore: PropTypes.bool.isRequired,
  /** Called with { skip, limit } when the user changes page */
  onChange: PropTypes.func.isRequired,
}
