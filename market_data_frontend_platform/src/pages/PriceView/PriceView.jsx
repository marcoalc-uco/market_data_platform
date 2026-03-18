import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { usePrices } from '../../hooks/usePrices.js'
import { useLatestPrice } from '../../hooks/useLatestPrice.js'
import { useInstrument } from '../../hooks/useInstrument.js'
import PriceChart from '../../components/PriceChart/PriceChart.jsx'
import DateRangePicker from '../../components/DateRangePicker/DateRangePicker.jsx'
import LatestPriceSummary from '../../components/LatestPriceSummary/LatestPriceSummary.jsx'
import ChatBox from '../../components/ChatBox/ChatBox.jsx'
import styles from './PriceView.module.css'

const toDateString = (d) => d.toISOString().slice(0, 10)
const today = () => toDateString(new Date())
const nDaysAgo = (n) => toDateString(new Date(Date.now() - n * 86_400_000))

/** Chart types available for user selection. */
const CHART_TYPES = [
  { value: 'candlestick', label: '🕯 Candles' },
  { value: 'line', label: '📈 Line' },
  { value: 'area', label: '⛰ Mountain' },
]

/**
 * Default chart type based on asset class.
 * Indices and ETFs have identical OHLC values, so area/line looks better.
 */
function defaultChartType(assetType) {
  return assetType === 'index' || assetType === 'etf' ? 'area' : 'candlestick'
}

/**
 * Price view page — OHLCV chart with date range filter, latest price summary
 * and AI chat assistant for a specific instrument.
 */
export default function PriceView() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [dateRange, setDateRange] = useState({
    startDate: nDaysAgo(90),
    endDate: today(),
  })

  // null = not yet initialised; will be set once instrument metadata loads
  const [chartType, setChartType] = useState(null)

  const queryParams = {
    start_date: dateRange.startDate ? `${dateRange.startDate}T00:00:00.000Z` : undefined,
    end_date: dateRange.endDate ? `${dateRange.endDate}T23:59:59.999Z` : undefined,
    limit: 1000,
  }

  const pricesQuery = usePrices(id, queryParams)
  const latestQuery = useLatestPrice(id)
  const instrumentQuery = useInstrument(id)

  // Set a sensible default chart type once instrument data is available,
  // but only if the user has not already made a manual selection.
  useEffect(() => {
    if (chartType === null && instrumentQuery.data?.asset_type) {
      setChartType(defaultChartType(instrumentQuery.data.asset_type))
    }
  }, [instrumentQuery.data?.asset_type, chartType])

  // Transform API payload to lightweight-charts OHLCV format.
  // API returns Decimal fields as strings, so we parseFloat each OHLC value.
  const chartData = (pricesQuery.data ?? [])
    .map((p) => ({
      // Lightweight charts uses UNIX timestamp (in seconds) for intraday data
      time: Math.floor(new Date(p.timestamp).getTime() / 1000),
      open: parseFloat(p.open),
      high: parseFloat(p.high),
      low: parseFloat(p.low),
      close: parseFloat(p.close),
    }))
    // Lightweight-charts strictly requires data in ascending time order
    .sort((a, b) => a.time - b.time)

  const activeChartType = chartType ?? 'candlestick'

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className={styles.back} onClick={() => navigate('/instruments')}>
          ← Back to Instruments
        </button>
        <h1 className={styles.title}>
          Price History — {instrumentQuery.data?.name || `Instrument #${id}`}
        </h1>
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
          {/* Chart type selector */}
          <div className={styles.chartTypeSelector} role="group" aria-label="Chart type">
            {CHART_TYPES.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setChartType(value)}
                className={`${styles.chartTypeBtn} ${activeChartType === value ? styles.chartTypeBtnActive : ''}`}
                aria-pressed={activeChartType === value}
              >
                {label}
              </button>
            ))}
          </div>

          <PriceChart
            symbol={instrumentQuery.data?.name || `Instrument #${id}`}
            data={chartData}
            chartType={activeChartType}
          />
        </section>
      )}

      {/* AI Chat — Ollama LLM with RAG support */}
      <section className={styles.section}>
        <ChatBox
          instrumentId={Number(id)}
          instrumentName={instrumentQuery.data?.name || `Instrument #${id}`}
        />
      </section>
    </div>
  )
}
