import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute.jsx'
import Login from './pages/Login/Login.jsx'
import Instruments from './pages/Instruments/Instruments.jsx'
import PriceView from './pages/PriceView/PriceView.jsx'
import styles from './App.module.css'

export default function App() {
  return (
    <div className={styles.app}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/instruments" element={<Instruments />} />
          <Route path="/instruments/:id/prices" element={<PriceView />} />
        </Route>
        <Route path="*" element={<Navigate to="/instruments" replace />} />
      </Routes>
    </div>
  )
}
