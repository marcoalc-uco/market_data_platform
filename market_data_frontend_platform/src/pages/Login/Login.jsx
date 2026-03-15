import { useAuth } from '../../hooks/useAuth.js'
import LoginForm from '../../components/LoginForm/LoginForm.jsx'
import styles from './Login.module.css'

export default function Login() {
  const { login, isLoading, error } = useAuth()

  return (
    <main className={styles.page}>
      <LoginForm onSubmit={login} isLoading={isLoading} error={error} />
    </main>
  )
}
