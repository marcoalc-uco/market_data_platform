import PropTypes from 'prop-types'
import styles from './LatestPriceSummary.module.css'

/**
 * Summary card displaying the latest OHLCV price snapshot.
 *
 * @param {Object}      props
 * @param {Object|null} props.price     - Latest price { open, high, low, close, volume }.
 *                                        OHLC values may be strings (Decimal from API).
 * @param {boolean}     props.isLoading - True while the query is in-flight.
 * @param {Object|null} props.error     - Error object if the query failed.
 */
export default function LatestPriceSummary({ price, isLoading, error }) {
  if (isLoading) return <p className={styles.state}>Loading latest price…</p>
  if (error) return <p className={styles.state}>No latest price available.</p>
  if (!price) return null

  const fmt = (v) => parseFloat(v).toFixed(2)

  return (
    <dl className={styles.card}>
      <div className={styles.item}>
        <dt>Open</dt>
        <dd>{fmt(price.open)}</dd>
      </div>
      <div className={styles.item}>
        <dt>High</dt>
        <dd className={styles.high}>{fmt(price.high)}</dd>
      </div>
      <div className={styles.item}>
        <dt>Low</dt>
        <dd className={styles.low}>{fmt(price.low)}</dd>
      </div>
      <div className={styles.item}>
        <dt>Close</dt>
        <dd>{fmt(price.close)}</dd>
      </div>
      <div className={styles.item}>
        <dt>Volume</dt>
        <dd>{Number(price.volume).toLocaleString('en-US')}</dd>
      </div>
    </dl>
  )
}

LatestPriceSummary.propTypes = {
  price: PropTypes.shape({
    open: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    high: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    low: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    close: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    volume: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
  }),
  isLoading: PropTypes.bool,
  error: PropTypes.object,
}
