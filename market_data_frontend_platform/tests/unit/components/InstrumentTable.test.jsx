import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InstrumentTable from '../../../src/components/InstrumentTable/InstrumentTable.jsx'

const INSTRUMENTS = [
  { id: 1, symbol: 'AAPL', name: 'Apple Inc.', asset_type: 'stock', exchange: 'NASDAQ', is_active: true },
  { id: 2, symbol: 'BTC', name: 'Bitcoin', asset_type: 'crypto', exchange: 'CRYPTO', is_active: false },
]

const noop = () => {}

describe('InstrumentTable', () => {
  it('renders column headers', () => {
    render(
      <InstrumentTable
        instruments={INSTRUMENTS}
        onEdit={noop}
        onDelete={noop}
        onRowClick={noop}
      />
    )
    expect(screen.getByText('Symbol')).toBeInTheDocument()
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Asset Type')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('renders each instrument row', () => {
    render(
      <InstrumentTable
        instruments={INSTRUMENTS}
        onEdit={noop}
        onDelete={noop}
        onRowClick={noop}
      />
    )
    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('Bitcoin')).toBeInTheDocument()
  })

  it('shows Yes/No for is_active', () => {
    render(
      <InstrumentTable
        instruments={INSTRUMENTS}
        onEdit={noop}
        onDelete={noop}
        onRowClick={noop}
      />
    )
    expect(screen.getByText('Yes')).toBeInTheDocument()
    expect(screen.getByText('No')).toBeInTheDocument()
  })

  it('shows empty state when instruments array is empty', () => {
    render(
      <InstrumentTable
        instruments={[]}
        onEdit={noop}
        onDelete={noop}
        onRowClick={noop}
      />
    )
    expect(screen.getByText(/no instruments found/i)).toBeInTheDocument()
  })

  it('calls onRowClick with instrument id when a row is clicked', async () => {
    const user = userEvent.setup()
    const onRowClick = vi.fn()

    render(
      <InstrumentTable
        instruments={INSTRUMENTS}
        onEdit={noop}
        onDelete={noop}
        onRowClick={onRowClick}
      />
    )

    await user.click(screen.getByText('AAPL'))
    expect(onRowClick).toHaveBeenCalledWith(1)
  })

  it('calls onEdit with the instrument when Edit is clicked', async () => {
    const user = userEvent.setup()
    const onEdit = vi.fn()

    render(
      <InstrumentTable
        instruments={INSTRUMENTS}
        onEdit={onEdit}
        onDelete={noop}
        onRowClick={noop}
      />
    )

    await user.click(screen.getByRole('button', { name: /edit aapl/i }))
    expect(onEdit).toHaveBeenCalledWith(INSTRUMENTS[0])
  })

  it('calls onDelete with instrument id when Delete is clicked', async () => {
    const user = userEvent.setup()
    const onDelete = vi.fn()

    render(
      <InstrumentTable
        instruments={INSTRUMENTS}
        onEdit={noop}
        onDelete={onDelete}
        onRowClick={noop}
      />
    )

    await user.click(screen.getByRole('button', { name: /delete aapl/i }))
    expect(onDelete).toHaveBeenCalledWith(1)
  })
})
