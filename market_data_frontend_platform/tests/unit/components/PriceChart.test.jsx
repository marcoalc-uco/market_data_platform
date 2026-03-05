import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

// vi.hoisted() runs before the vi.mock() factory is hoisted,
// allowing shared mock refs accessible inside and outside the factory.
const mocks = vi.hoisted(() => {
  const mockSetData = vi.fn()
  const mockFitContent = vi.fn()
  const mockRemove = vi.fn()
  const mockAddCandlestickSeries = vi.fn(() => ({ setData: mockSetData }))
  const mockTimeScale = vi.fn(() => ({ fitContent: mockFitContent }))
  const mockCreateChart = vi.fn(() => ({
    addCandlestickSeries: mockAddCandlestickSeries,
    timeScale: mockTimeScale,
    remove: mockRemove,
  }))
  return { mockSetData, mockFitContent, mockRemove, mockAddCandlestickSeries, mockCreateChart }
})

vi.mock('lightweight-charts', () => ({
  createChart: mocks.mockCreateChart,
}))

import PriceChart from '../../../src/components/PriceChart/PriceChart.jsx'

const CHART_DATA = [
  { time: '2024-01-15', open: 100, high: 110, low: 95, close: 105 },
  { time: '2024-01-16', open: 105, high: 115, low: 102, close: 112 },
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

  it('calls addCandlestickSeries on mount', () => {
    render(<PriceChart symbol="AAPL" data={[]} />)
    expect(mocks.mockAddCandlestickSeries).toHaveBeenCalledTimes(1)
  })

  it('calls setData with the provided data', () => {
    render(<PriceChart symbol="AAPL" data={CHART_DATA} />)
    expect(mocks.mockSetData).toHaveBeenCalledWith(CHART_DATA)
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
