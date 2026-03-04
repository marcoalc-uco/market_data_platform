import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute.jsx'
import Login from './pages/Login/Login.jsx'
import styles from './App.module.css'

export default function App() {
  return (
    <div className={styles.app}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/instruments" element={<div>Instruments (Phase 4)</div>} />
          <Route path="/instruments/:id/prices" element={<div>Prices (Phase 5)</div>} />
        </Route>
        <Route path="*" element={<Navigate to="/instruments" replace />} />
      </Routes>
    </div>
  )
}
