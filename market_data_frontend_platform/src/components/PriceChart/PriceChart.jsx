import { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { createChart } from 'lightweight-charts'
import styles from './PriceChart.module.css'

/**
 * Price chart for OHLCV data powered by lightweight-charts.
 *
 * Chart types:
 *   - "candlestick" — OHLC candlestick (default, good for stocks)
 *   - "line"        — Simple close-price line
 *   - "area"        — Filled area / mountain chart (good for indices / ETFs)
 *
 * @param {Object}   props
 * @param {string}   props.symbol    - Instrument symbol label (e.g. "AAPL").
 * @param {Array}    props.data      - Array of { time, open, high, low, close }.
 * @param {string}   [props.chartType="candlestick"] - "candlestick" | "line" | "area".
 */
export default function PriceChart({ symbol, data, chartType = 'candlestick' }) {
  const containerRef = useRef(null)
  const chartRef = useRef(null)
  const seriesRef = useRef(null)

  // Initialise chart once on mount (or when chartType changes), destroy on unmount
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

    if (chartType === 'area') {
      seriesRef.current = chartRef.current.addAreaSeries({
        lineColor: '#2962FF',
        topColor: 'rgba(41, 98, 255, 0.3)',
        bottomColor: 'rgba(41, 98, 255, 0.02)',
        lineWidth: 2,
      })
    } else if (chartType === 'line') {
      seriesRef.current = chartRef.current.addLineSeries({
        color: '#2962FF',
        lineWidth: 2,
      })
    } else {
      // candlestick (default)
      seriesRef.current = chartRef.current.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      })
    }

    return () => {
      chartRef.current?.remove()
    }
  }, [chartType])

  // Update series data whenever `data` prop changes
  useEffect(() => {
    if (!seriesRef.current || !data?.length) return

    if (chartType === 'candlestick') {
      seriesRef.current.setData(data)
    } else {
      // line and area series expect { time, value }
      seriesRef.current.setData(data.map((p) => ({ time: p.time, value: p.close })))
    }
    chartRef.current?.timeScale().fitContent()
  }, [data, chartType])

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
  chartType: PropTypes.oneOf(['candlestick', 'line', 'area']),
}
