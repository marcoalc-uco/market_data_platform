import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { login as loginRequest } from '../api/auth.js'

export function useAuth() {
  const navigate = useNavigate()

  const loginMutation = useMutation({
    mutationFn: loginRequest,
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token)
      navigate('/instruments')
    },
  })

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return {
    login: loginMutation.mutate,
    logout,
    isAuthenticated: Boolean(localStorage.getItem('token')),
    isLoading: loginMutation.isPending,
    error: loginMutation.error,
  }
}
