import { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { createChart } from 'lightweight-charts'
import styles from './PriceChart.module.css'

/**
 * Candlestick chart for OHLCV price data powered by lightweight-charts.
 *
 * @param {Object}   props
 * @param {string}   props.symbol - Instrument symbol label (e.g. "AAPL").
 * @param {Array}    props.data   - Array of { time, open, high, low, close }.
 *                                  `time` must be a UNIX timestamp in seconds (number).
 *                                  OHLC values must be numbers.
 */
export default function PriceChart({ symbol, data }) {
  const containerRef = useRef(null)
  const chartRef = useRef(null)
  const seriesRef = useRef(null)

  // Initialise chart once on mount, destroy on unmount
  useEffect(() => {
    if (!containerRef.current) return

    chartRef.current = createChart(containerRef.current, {
      width: containerRef.current.clientWidth || 800,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333333',
      },
      grid: {
        vertLines: { color: '#f0f3fa' },
        horzLines: { color: '#f0f3fa' },
      },
      timeScale: {
        borderColor: '#d1d4dc',
        timeVisible: true,
      },
    })

    seriesRef.current = chartRef.current.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    return () => {
      chartRef.current?.remove()
    }
  }, [])

  // Update series data whenever `data` prop changes
  useEffect(() => {
    if (!seriesRef.current || !data?.length) return
    seriesRef.current.setData(data)
    chartRef.current?.timeScale().fitContent()
  }, [data])

  return (
    <div className={styles.wrapper}>
      <h2 className={styles.symbol}>{symbol}</h2>
      <div ref={containerRef} className={styles.chart} data-testid="chart-container" />
    </div>
  )
}

PriceChart.propTypes = {
  symbol: PropTypes.string.isRequired,
  data: PropTypes.arrayOf(
    PropTypes.shape({
      time: PropTypes.number.isRequired,
      open: PropTypes.number.isRequired,
      high: PropTypes.number.isRequired,
      low: PropTypes.number.isRequired,
      close: PropTypes.number.isRequired,
    })
  ).isRequired,
}
