import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LatestPriceSummary from '../../../src/components/LatestPriceSummary/LatestPriceSummary.jsx'

const PRICE = {
  open: '185.50',
  high: '186.20',
  low: '184.80',
  close: '185.90',
  volume: 3000000,
}

describe('LatestPriceSummary', () => {
  it('shows loading message while isLoading is true', () => {
    render(<LatestPriceSummary price={null} isLoading={true} error={null} />)
    expect(screen.getByText(/loading latest price/i)).toBeInTheDocument()
  })

  it('shows no-data message when there is an error', () => {
    render(<LatestPriceSummary price={null} isLoading={false} error={new Error('404')} />)
    expect(screen.getByText(/no latest price available/i)).toBeInTheDocument()
  })

  it('renders nothing when price is null and no error', () => {
    const { container } = render(
      <LatestPriceSummary price={null} isLoading={false} error={null} />
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('displays formatted Open value', () => {
    render(<LatestPriceSummary price={PRICE} isLoading={false} error={null} />)
    expect(screen.getByText('185.50')).toBeInTheDocument()
  })

  it('displays formatted High value', () => {
    render(<LatestPriceSummary price={PRICE} isLoading={false} error={null} />)
    expect(screen.getByText('186.20')).toBeInTheDocument()
  })

  it('displays formatted Low value', () => {
    render(<LatestPriceSummary price={PRICE} isLoading={false} error={null} />)
    expect(screen.getByText('184.80')).toBeInTheDocument()
  })

  it('displays formatted Close value', () => {
    render(<LatestPriceSummary price={PRICE} isLoading={false} error={null} />)
    expect(screen.getByText('185.90')).toBeInTheDocument()
  })

  it('displays formatted Volume with locale separators', () => {
    render(<LatestPriceSummary price={PRICE} isLoading={false} error={null} />)
    expect(screen.getByText('3,000,000')).toBeInTheDocument()
  })

  it('renders all OHLCV labels', () => {
    render(<LatestPriceSummary price={PRICE} isLoading={false} error={null} />)
    expect(screen.getByText('Open')).toBeInTheDocument()
    expect(screen.getByText('High')).toBeInTheDocument()
    expect(screen.getByText('Low')).toBeInTheDocument()
    expect(screen.getByText('Close')).toBeInTheDocument()
    expect(screen.getByText('Volume')).toBeInTheDocument()
  })
})
