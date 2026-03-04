import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../../../src/test/testUtils.jsx'
import Instruments from '../../../src/pages/Instruments/Instruments.jsx'
import * as instrumentsApi from '../../../src/api/instruments.js'

vi.mock('../../../src/api/instruments.js')

const INSTRUMENTS = [
  { id: 1, symbol: 'AAPL', name: 'Apple Inc.', asset_type: 'stock', exchange: 'NASDAQ', is_active: true },
  { id: 2, symbol: 'BTC', name: 'Bitcoin', asset_type: 'crypto', exchange: 'CRYPTO', is_active: false },
]

describe('Instruments page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows a loading state while fetching', () => {
    instrumentsApi.getInstruments.mockImplementation(() => new Promise(() => {}))

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    expect(screen.getByText(/loading instruments/i)).toBeInTheDocument()
  })

  it('shows an error state with a retry button on API failure', async () => {
    instrumentsApi.getInstruments.mockRejectedValue(new Error('Server error'))

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent('Server error')
    )
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  })

  it('renders the instruments table with data', async () => {
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())
    expect(screen.getByText('Bitcoin')).toBeInTheDocument()
  })

  it('shows an empty state when the API returns no instruments', async () => {
    instrumentsApi.getInstruments.mockResolvedValue([])

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() =>
      expect(screen.getByText(/no instruments found/i)).toBeInTheDocument()
    )
  })

  it('opens the Add Instrument form when the button is clicked', async () => {
    const user = userEvent.setup()
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())

    await user.click(screen.getByRole('button', { name: /add instrument/i }))
    expect(screen.getByRole('heading', { name: /add instrument/i })).toBeInTheDocument()
  })

  it('opens the Edit form pre-filled when Edit is clicked', async () => {
    const user = userEvent.setup()
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())

    await user.click(screen.getByRole('button', { name: /edit aapl/i }))
    expect(screen.getByRole('heading', { name: /edit instrument/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/symbol/i)).toHaveValue('AAPL')
  })

  it('calls deleteInstrument when Delete is confirmed', async () => {
    const user = userEvent.setup()
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)
    instrumentsApi.deleteInstrument.mockResolvedValue(null)
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())

    await user.click(screen.getByRole('button', { name: /delete aapl/i }))
    expect(instrumentsApi.deleteInstrument.mock.calls[0][0]).toBe(1)
  })

  it('does not call deleteInstrument when confirm is cancelled', async () => {
    const user = userEvent.setup()
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)
    vi.spyOn(window, 'confirm').mockReturnValue(false)

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())

    await user.click(screen.getByRole('button', { name: /delete aapl/i }))
    expect(instrumentsApi.deleteInstrument).not.toHaveBeenCalled()
  })

  it('navigates to the price view when a row is clicked', async () => {
    const user = userEvent.setup()
    instrumentsApi.getInstruments.mockResolvedValue(INSTRUMENTS)

    renderWithProviders(<Instruments />, { initialEntries: ['/instruments'] })

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())

    await user.click(screen.getByText('Apple Inc.'))
    // After navigation the instruments page is no longer visible
    await waitFor(() =>
      expect(screen.queryByText(/loading instruments/i)).not.toBeInTheDocument()
    )
  })
})
