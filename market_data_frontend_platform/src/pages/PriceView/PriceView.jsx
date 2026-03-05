import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { usePrices } from '../../hooks/usePrices.js'
import { useLatestPrice } from '../../hooks/useLatestPrice.js'
import PriceChart from '../../components/PriceChart/PriceChart.jsx'
import DateRangePicker from '../../components/DateRangePicker/DateRangePicker.jsx'
import LatestPriceSummary from '../../components/LatestPriceSummary/LatestPriceSummary.jsx'
import styles from './PriceView.module.css'

const toDateString = (d) => d.toISOString().slice(0, 10)
const today = () => toDateString(new Date())
const nDaysAgo = (n) => toDateString(new Date(Date.now() - n * 86_400_000))

/**
 * Price view page — OHLCV candlestick chart with date range filter
 * and latest price summary for a specific instrument.
 */
export default function PriceView() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [dateRange, setDateRange] = useState({
    startDate: nDaysAgo(90),
    endDate: today(),
  })

  const queryParams = {
    start_date: dateRange.startDate,
    end_date: dateRange.endDate,
    limit: 500,
  }

  const pricesQuery = usePrices(id, queryParams)
  const latestQuery = useLatestPrice(id)

  // Transform API payload to lightweight-charts candlestick format.
  // API returns Decimal fields as strings, so we parseFloat each OHLC value.
  const chartData = (pricesQuery.data ?? []).map((p) => ({
    time: p.timestamp.slice(0, 10),
    open: parseFloat(p.open),
    high: parseFloat(p.high),
    low: parseFloat(p.low),
    close: parseFloat(p.close),
  }))

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className={styles.back} onClick={() => navigate('/instruments')}>
          ← Back to Instruments
        </button>
        <h1 className={styles.title}>Price History — Instrument #{id}</h1>
      </header>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Latest Price</h2>
        <LatestPriceSummary
          price={latestQuery.data}
          isLoading={latestQuery.isLoading}
          error={latestQuery.error}
        />
      </section>

      <section className={styles.section}>
        <DateRangePicker
          startDate={dateRange.startDate}
          endDate={dateRange.endDate}
          onChange={setDateRange}
        />
      </section>

      {pricesQuery.isLoading && (
        <p className={styles.state} role="status">
          Loading chart data…
        </p>
      )}
      {pricesQuery.error && (
        <p className={styles.state} role="alert">
          Failed to load prices: {pricesQuery.error.message}
        </p>
      )}
      {!pricesQuery.isLoading && !pricesQuery.error && chartData.length === 0 && (
        <p className={styles.state}>No price data available for the selected range.</p>
      )}
      {chartData.length > 0 && (
        <section className={styles.section}>
          <PriceChart symbol={`Instrument #${id}`} data={chartData} />
        </section>
      )}
    </div>
  )
}
