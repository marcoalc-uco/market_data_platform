import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../../../src/test/testUtils.jsx'
import Login from '../../../src/pages/Login/Login.jsx'

const mockLogin = vi.fn()

vi.mock('../../../src/hooks/useAuth.js', () => ({
  useAuth: vi.fn(),
}))

import { useAuth } from '../../../src/hooks/useAuth.js'

describe('Login page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useAuth.mockReturnValue({ login: mockLogin, isLoading: false, error: null })
  })

  it('renders the LoginForm with username and password inputs', () => {
    renderWithProviders(<Login />)
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('renders the submit button', () => {
    renderWithProviders(<Login />)
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('calls login from useAuth on form submit', async () => {
    const user = userEvent.setup()
    renderWithProviders(<Login />)

    await user.type(screen.getByLabelText(/username/i), 'admin')
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.click(screen.getByRole('button', { name: /login/i }))

    expect(mockLogin).toHaveBeenCalledWith({ username: 'admin', password: 'secret' })
  })

  it('shows loading state when isLoading is true', () => {
    useAuth.mockReturnValue({ login: mockLogin, isLoading: true, error: null })
    renderWithProviders(<Login />)
    expect(screen.getByRole('button')).toBeDisabled()
    expect(screen.getByRole('button')).toHaveTextContent(/logging in/i)
  })

  it('displays error message when login fails', () => {
    useAuth.mockReturnValue({
      login: mockLogin,
      isLoading: false,
      error: new Error('Invalid credentials'),
    })
    renderWithProviders(<Login />)
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials')
  })
})
