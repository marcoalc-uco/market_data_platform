import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InstrumentFilters from '../../../src/components/InstrumentFilters/InstrumentFilters.jsx'

describe('InstrumentFilters', () => {
  it('renders asset type select and active checkbox', () => {
    render(<InstrumentFilters filters={{}} onChange={() => {}} />)

    expect(screen.getByLabelText(/asset type/i)).toBeInTheDocument()
    expect(screen.getByRole('checkbox')).toBeInTheDocument()
  })

  it('shows "All" as the default asset type option', () => {
    render(<InstrumentFilters filters={{}} onChange={() => {}} />)

    expect(screen.getByRole('option', { name: 'All' }).selected).toBe(true)
  })

  it('calls onChange when asset type is changed', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<InstrumentFilters filters={{ asset_type: undefined }} onChange={onChange} />)

    await user.selectOptions(screen.getByLabelText(/asset type/i), 'stock')
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ asset_type: 'stock' })
    )
  })

  it('calls onChange when active checkbox is toggled', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<InstrumentFilters filters={{ is_active: undefined }} onChange={onChange} />)

    await user.click(screen.getByRole('checkbox'))
    // When checked → is_active should be truthy
    expect(onChange).toHaveBeenCalled()
  })

  it('reflects the current filter values', () => {
    render(
      <InstrumentFilters
        filters={{ asset_type: 'crypto', is_active: true }}
        onChange={() => {}}
      />
    )

    expect(screen.getByLabelText(/asset type/i)).toHaveValue('crypto')
    expect(screen.getByRole('checkbox')).toBeChecked()
  })
})
