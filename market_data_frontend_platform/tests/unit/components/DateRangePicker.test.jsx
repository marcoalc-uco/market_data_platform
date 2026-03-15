import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import DateRangePicker from '../../../src/components/DateRangePicker/DateRangePicker.jsx'

const DEFAULT_PROPS = {
  startDate: '2024-01-01',
  endDate: '2024-03-31',
  onChange: vi.fn(),
}

describe('DateRangePicker', () => {
  it('renders start date and end date inputs', () => {
    render(<DateRangePicker {...DEFAULT_PROPS} />)
    expect(screen.getByLabelText('Start date')).toBeInTheDocument()
    expect(screen.getByLabelText('End date')).toBeInTheDocument()
  })

  it('shows the current startDate value', () => {
    render(<DateRangePicker {...DEFAULT_PROPS} />)
    expect(screen.getByLabelText('Start date')).toHaveValue('2024-01-01')
  })

  it('shows the current endDate value', () => {
    render(<DateRangePicker {...DEFAULT_PROPS} />)
    expect(screen.getByLabelText('End date')).toHaveValue('2024-03-31')
  })

  it('calls onChange with updated startDate when start input changes', () => {
    const onChange = vi.fn()
    render(<DateRangePicker {...DEFAULT_PROPS} onChange={onChange} />)
    fireEvent.change(screen.getByLabelText('Start date'), { target: { value: '2024-02-01' } })
    expect(onChange).toHaveBeenCalledWith({ startDate: '2024-02-01', endDate: DEFAULT_PROPS.endDate })
  })

  it('calls onChange with updated endDate when end input changes', () => {
    const onChange = vi.fn()
    render(<DateRangePicker {...DEFAULT_PROPS} onChange={onChange} />)
    fireEvent.change(screen.getByLabelText('End date'), { target: { value: '2024-06-30' } })
    expect(onChange).toHaveBeenCalledWith({ startDate: DEFAULT_PROPS.startDate, endDate: '2024-06-30' })
  })

  it('renders "From" and "To" labels', () => {
    render(<DateRangePicker {...DEFAULT_PROPS} />)
    expect(screen.getByText('From')).toBeInTheDocument()
    expect(screen.getByText('To')).toBeInTheDocument()
  })
})
