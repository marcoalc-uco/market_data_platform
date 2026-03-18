import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent } from '@testing-library/react'
import { renderWithProviders } from '../../../src/test/testUtils.jsx'
import PriceView from '../../../src/pages/PriceView/PriceView.jsx'

// Mock lightweight-charts — requires a real browser canvas.
// Include all three series types so chartType switching doesn't throw.
const seriesStub = () => ({ setData: vi.fn() })
vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addCandlestickSeries: vi.fn(seriesStub),
    addLineSeries: vi.fn(seriesStub),
    addAreaSeries: vi.fn(seriesStub),
    timeScale: vi.fn(() => ({ fitContent: vi.fn() })),
    remove: vi.fn(),
  })),
}))

// Mock react-router-dom: useParams returns { id: '42' }, useNavigate is a spy
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ id: '42' }),
    useNavigate: () => mockNavigate,
  }
})

// Mock the data hooks
vi.mock('../../../src/hooks/usePrices.js', () => ({ usePrices: vi.fn() }))
vi.mock('../../../src/hooks/useLatestPrice.js', () => ({ useLatestPrice: vi.fn() }))
vi.mock('../../../src/hooks/useInstrument.js', () => ({ useInstrument: vi.fn() }))

// Mock ChatBox — heavy SSE component not under test here
vi.mock('../../../src/components/ChatBox/ChatBox.jsx', () => ({
  default: () => <div data-testid="chatbox-mock" />,
}))

import { usePrices } from '../../../src/hooks/usePrices.js'
import { useLatestPrice } from '../../../src/hooks/useLatestPrice.js'
import { useInstrument } from '../../../src/hooks/useInstrument.js'

const PRICES = [
  {
    id: 1,
    instrument_id: 42,
    timestamp: '2024-01-15T00:00:00',
    open: '100.00',
    high: '110.00',
    low: '95.00',
    close: '105.00',
    volume: 5000000,
  },
]

const LATEST_PRICE = {
  open: '105.00',
  high: '110.00',
  low: '103.00',
  close: '108.00',
  volume: 4000000,
}

/** Helper: set up all hooks for a "data loaded" scenario. */
function setupLoadedState({ assetType = 'stock' } = {}) {
  usePrices.mockReturnValue({ data: PRICES, isLoading: false, error: null })
  useLatestPrice.mockReturnValue({ data: LATEST_PRICE, isLoading: false, error: null })
  useInstrument.mockReturnValue({ data: { name: 'Test Corp', asset_type: assetType } })
}

describe('PriceView page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Default: instrument not yet loaded
    useInstrument.mockReturnValue({ data: null })
  })

  it('shows a loading state while prices are fetching', () => {
    usePrices.mockReturnValue({ data: undefined, isLoading: true, error: null })
    useLatestPrice.mockReturnValue({ data: undefined, isLoading: false, error: null })
    renderWithProviders(<PriceView />)
    expect(screen.getByRole('status')).toHaveTextContent(/loading chart data/i)
  })

  it('shows an error message when the prices query fails', () => {
    usePrices.mockReturnValue({ data: undefined, isLoading: false, error: new Error('Server error') })
    useLatestPrice.mockReturnValue({ data: undefined, isLoading: false, error: null })
    renderWithProviders(<PriceView />)
    expect(screen.getByRole('alert')).toHaveTextContent(/failed to load prices/i)
  })

  it('shows "no data" message when API returns empty array', () => {
    usePrices.mockReturnValue({ data: [], isLoading: false, error: null })
    useLatestPrice.mockReturnValue({ data: undefined, isLoading: false, error: null })
    renderWithProviders(<PriceView />)
    expect(screen.getByText(/no price data available/i)).toBeInTheDocument()
  })

  it('renders the PriceChart when data is available', () => {
    setupLoadedState()
    renderWithProviders(<PriceView />)
    expect(screen.getByTestId('chart-container')).toBeInTheDocument()
  })

  it('renders the LatestPriceSummary with price values', () => {
    setupLoadedState()
    renderWithProviders(<PriceView />)
    expect(screen.getByText('108.00')).toBeInTheDocument()
    expect(screen.getByText('4,000,000')).toBeInTheDocument()
  })

  it('renders the DateRangePicker', () => {
    usePrices.mockReturnValue({ data: [], isLoading: false, error: null })
    useLatestPrice.mockReturnValue({ data: undefined, isLoading: false, error: null })
    renderWithProviders(<PriceView />)
    expect(screen.getByLabelText('Start date')).toBeInTheDocument()
    expect(screen.getByLabelText('End date')).toBeInTheDocument()
  })

  it('renders the page title containing the instrument id', () => {
    usePrices.mockReturnValue({ data: [], isLoading: false, error: null })
    useLatestPrice.mockReturnValue({ data: undefined, isLoading: false, error: null })
    renderWithProviders(<PriceView />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('#42')
  })

  it('calls navigate("/instruments") when the back button is clicked', () => {
    usePrices.mockReturnValue({ data: [], isLoading: false, error: null })
    useLatestPrice.mockReturnValue({ data: undefined, isLoading: false, error: null })
    renderWithProviders(<PriceView />)
    fireEvent.click(screen.getByText(/back to instruments/i))
    expect(mockNavigate).toHaveBeenCalledWith('/instruments')
  })

  // ── Chart type selector ────────────────────────────────────────────────

  it('renders the three chart-type buttons when data is available', () => {
    setupLoadedState()
    renderWithProviders(<PriceView />)
    expect(screen.getByRole('button', { name: /candles/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /line/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /mountain/i })).toBeInTheDocument()
  })

  it('defaults to "candlestick" for stock instruments', () => {
    setupLoadedState({ assetType: 'stock' })
    renderWithProviders(<PriceView />)
    expect(screen.getByRole('button', { name: /candles/i })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: /mountain/i })).toHaveAttribute('aria-pressed', 'false')
  })

  it('defaults to "area" for index instruments', () => {
    setupLoadedState({ assetType: 'index' })
    renderWithProviders(<PriceView />)
    expect(screen.getByRole('button', { name: /mountain/i })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: /candles/i })).toHaveAttribute('aria-pressed', 'false')
  })

  it('switches to "line" when the Line button is clicked', () => {
    setupLoadedState()
    renderWithProviders(<PriceView />)
    fireEvent.click(screen.getByRole('button', { name: /line/i }))
    expect(screen.getByRole('button', { name: /line/i })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: /candles/i })).toHaveAttribute('aria-pressed', 'false')
  })
})
