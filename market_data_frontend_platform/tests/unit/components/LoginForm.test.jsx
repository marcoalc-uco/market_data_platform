import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginForm from '../../../src/components/LoginForm/LoginForm.jsx'

function renderLoginForm(props = {}) {
  return render(
    <LoginForm
      onSubmit={props.onSubmit ?? vi.fn()}
      isLoading={props.isLoading ?? false}
      error={props.error ?? null}
    />
  )
}

describe('LoginForm', () => {
  it('renders username and password inputs', () => {
    renderLoginForm()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('renders a submit button', () => {
    renderLoginForm()
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('calls onSubmit with username and password', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    renderLoginForm({ onSubmit })

    await user.type(screen.getByLabelText(/username/i), 'admin')
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.click(screen.getByRole('button', { name: /login/i }))

    expect(onSubmit).toHaveBeenCalledOnce()
    expect(onSubmit).toHaveBeenCalledWith({ username: 'admin', password: 'secret' })
  })

  it('disables submit button while isLoading', () => {
    renderLoginForm({ isLoading: true })
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('shows loading text while isLoading', () => {
    renderLoginForm({ isLoading: true })
    expect(screen.getByRole('button')).toHaveTextContent(/logging in/i)
  })

  it('displays error message when error is provided', () => {
    renderLoginForm({ error: new Error('Invalid credentials') })
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials')
  })

  it('does not display error alert when error is null', () => {
    renderLoginForm({ error: null })
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })
})
