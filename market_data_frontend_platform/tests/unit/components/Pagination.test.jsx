import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Pagination from '../../../src/components/Pagination/Pagination.jsx'

describe('Pagination', () => {
  it('shows the current page number', () => {
    render(<Pagination skip={0} limit={20} hasMore={false} onChange={() => {}} />)
    expect(screen.getByText('Page 1')).toBeInTheDocument()
  })

  it('calculates page number from skip and limit', () => {
    render(<Pagination skip={40} limit={20} hasMore={true} onChange={() => {}} />)
    expect(screen.getByText('Page 3')).toBeInTheDocument()
  })

  it('disables the Prev button when skip is 0', () => {
    render(<Pagination skip={0} limit={20} hasMore={true} onChange={() => {}} />)
    expect(screen.getByRole('button', { name: /prev/i })).toBeDisabled()
  })

  it('disables the Next button when hasMore is false', () => {
    render(<Pagination skip={0} limit={20} hasMore={false} onChange={() => {}} />)
    expect(screen.getByRole('button', { name: /next/i })).toBeDisabled()
  })

  it('calls onChange with incremented skip when Next is clicked', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<Pagination skip={0} limit={20} hasMore={true} onChange={onChange} />)

    await user.click(screen.getByRole('button', { name: /next/i }))
    expect(onChange).toHaveBeenCalledWith({ skip: 20, limit: 20 })
  })

  it('calls onChange with decremented skip when Prev is clicked', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<Pagination skip={20} limit={20} hasMore={false} onChange={onChange} />)

    await user.click(screen.getByRole('button', { name: /prev/i }))
    expect(onChange).toHaveBeenCalledWith({ skip: 0, limit: 20 })
  })
})
