import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

// vi.hoisted() runs before the vi.mock() factory is hoisted,
// allowing shared mock refs accessible inside and outside the factory.
const mocks = vi.hoisted(() => {
  const mockSetData = vi.fn()
  const mockFitContent = vi.fn()
  const mockRemove = vi.fn()
  const seriesStub = () => ({ setData: mockSetData })
  const mockAddCandlestickSeries = vi.fn(seriesStub)
  const mockAddLineSeries = vi.fn(seriesStub)
  const mockAddAreaSeries = vi.fn(seriesStub)
  const mockTimeScale = vi.fn(() => ({ fitContent: mockFitContent }))
  const mockCreateChart = vi.fn(() => ({
    addCandlestickSeries: mockAddCandlestickSeries,
    addLineSeries: mockAddLineSeries,
    addAreaSeries: mockAddAreaSeries,
    timeScale: mockTimeScale,
    remove: mockRemove,
  }))
  return {
    mockSetData,
    mockFitContent,
    mockRemove,
    mockAddCandlestickSeries,
    mockAddLineSeries,
    mockAddAreaSeries,
    mockCreateChart,
  }
})

vi.mock('lightweight-charts', () => ({
  createChart: mocks.mockCreateChart,
}))

import PriceChart from '../../../src/components/PriceChart/PriceChart.jsx'

// time is a Unix timestamp (seconds) as required by PropTypes
const CHART_DATA = [
  { time: 1705276800, open: 100, high: 110, low: 95,  close: 105 },
  { time: 1705363200, open: 105, high: 115, low: 102, close: 112 },
]

describe('PriceChart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the symbol heading', () => {
    render(<PriceChart symbol="AAPL" data={[]} />)
    expect(screen.getByRole('heading', { name: 'AAPL' })).toBeInTheDocument()
  })

  it('renders the chart container div', () => {
    render(<PriceChart symbol="AAPL" data={[]} />)
    expect(screen.getByTestId('chart-container')).toBeInTheDocument()
  })

  it('calls createChart on mount', () => {
    render(<PriceChart symbol="AAPL" data={[]} />)
    expect(mocks.mockCreateChart).toHaveBeenCalledTimes(1)
  })

  describe('chartType="candlestick" (default)', () => {
    it('calls addCandlestickSeries on mount', () => {
      render(<PriceChart symbol="AAPL" data={[]} />)
      expect(mocks.mockAddCandlestickSeries).toHaveBeenCalledTimes(1)
      expect(mocks.mockAddLineSeries).not.toHaveBeenCalled()
      expect(mocks.mockAddAreaSeries).not.toHaveBeenCalled()
    })

    it('calls setData with the full OHLCV array', () => {
      render(<PriceChart symbol="AAPL" data={CHART_DATA} />)
      expect(mocks.mockSetData).toHaveBeenCalledWith(CHART_DATA)
    })
  })

  describe('chartType="line"', () => {
    it('calls addLineSeries on mount', () => {
      render(<PriceChart symbol="AAPL" data={[]} chartType="line" />)
      expect(mocks.mockAddLineSeries).toHaveBeenCalledTimes(1)
      expect(mocks.mockAddCandlestickSeries).not.toHaveBeenCalled()
      expect(mocks.mockAddAreaSeries).not.toHaveBeenCalled()
    })

    it('maps data to {time, value} using close price', () => {
      render(<PriceChart symbol="AAPL" data={CHART_DATA} chartType="line" />)
      expect(mocks.mockSetData).toHaveBeenCalledWith([
        { time: 1705276800, value: 105 },
        { time: 1705363200, value: 112 },
      ])
    })
  })

  describe('chartType="area"', () => {
    it('calls addAreaSeries on mount', () => {
      render(<PriceChart symbol="AAPL" data={[]} chartType="area" />)
      expect(mocks.mockAddAreaSeries).toHaveBeenCalledTimes(1)
      expect(mocks.mockAddCandlestickSeries).not.toHaveBeenCalled()
      expect(mocks.mockAddLineSeries).not.toHaveBeenCalled()
    })

    it('maps data to {time, value} using close price', () => {
      render(<PriceChart symbol="AAPL" data={CHART_DATA} chartType="area" />)
      expect(mocks.mockSetData).toHaveBeenCalledWith([
        { time: 1705276800, value: 105 },
        { time: 1705363200, value: 112 },
      ])
    })
  })

  it('calls fitContent after setting data', () => {
    render(<PriceChart symbol="AAPL" data={CHART_DATA} />)
    expect(mocks.mockFitContent).toHaveBeenCalledTimes(1)
  })

  it('does not call setData when data is empty', () => {
    render(<PriceChart symbol="AAPL" data={[]} />)
    expect(mocks.mockSetData).not.toHaveBeenCalled()
  })
})
