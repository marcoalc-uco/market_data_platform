import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InstrumentForm from '../../../src/components/InstrumentForm/InstrumentForm.jsx'

const INSTRUMENT = {
  id: 1,
  symbol: 'AAPL',
  name: 'Apple Inc.',
  asset_type: 'stock',
  exchange: 'NASDAQ',
  is_active: true,
}

describe('InstrumentForm', () => {
  it('renders in create mode when no instrument is passed', () => {
    render(<InstrumentForm onSubmit={() => {}} onClose={() => {}} />)
    expect(screen.getByRole('heading', { name: /add instrument/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/symbol/i)).toHaveValue('')
    expect(screen.getByLabelText(/exchange/i)).toHaveValue('')
  })

  it('renders in edit mode with pre-filled values when instrument is passed', () => {
    render(
      <InstrumentForm instrument={INSTRUMENT} onSubmit={() => {}} onClose={() => {}} />
    )
    expect(screen.getByRole('heading', { name: /edit instrument/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/symbol/i)).toHaveValue('AAPL')
    expect(screen.getByLabelText(/name/i)).toHaveValue('Apple Inc.')
    expect(screen.getByLabelText(/exchange/i)).toHaveValue('NASDAQ')
  })

  it('disables symbol and asset_type in edit mode (immutable fields)', () => {
    render(
      <InstrumentForm instrument={INSTRUMENT} onSubmit={() => {}} onClose={() => {}} />
    )
    expect(screen.getByLabelText(/symbol/i)).toBeDisabled()
    expect(screen.getByLabelText(/asset type/i)).toBeDisabled()
  })

  it('symbol and asset_type are editable in create mode', () => {
    render(<InstrumentForm onSubmit={() => {}} onClose={() => {}} />)
    expect(screen.getByLabelText(/symbol/i)).not.toBeDisabled()
    expect(screen.getByLabelText(/asset type/i)).not.toBeDisabled()
  })

  it('calls onSubmit with current field values on submit', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<InstrumentForm onSubmit={onSubmit} onClose={() => {}} />)

    await user.type(screen.getByLabelText(/symbol/i), 'BTC')
    await user.type(screen.getByLabelText(/name/i), 'Bitcoin')
    await user.type(screen.getByLabelText(/exchange/i), 'CRYPTO')
    await user.click(screen.getByRole('button', { name: /save/i }))

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ symbol: 'BTC', name: 'Bitcoin', exchange: 'CRYPTO' })
    )
  })

  it('calls onClose when Cancel is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(<InstrumentForm onSubmit={() => {}} onClose={onClose} />)

    await user.click(screen.getByRole('button', { name: /cancel/i }))
    expect(onClose).toHaveBeenCalled()
  })

  it('disables buttons and shows Saving… when isLoading is true', () => {
    render(<InstrumentForm onSubmit={() => {}} onClose={() => {}} isLoading />)
    expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled()
  })

  it('displays the error message when error prop is set', () => {
    render(
      <InstrumentForm
        onSubmit={() => {}}
        onClose={() => {}}
        error={{ message: 'Symbol already exists' }}
      />
    )
    expect(screen.getByRole('alert')).toHaveTextContent('Symbol already exists')
  })
})
