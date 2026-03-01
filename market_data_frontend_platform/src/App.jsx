import { Routes, Route, Navigate } from 'react-router-dom'
import styles from './App.module.css'

export default function App() {
  return (
    <div className={styles.app}>
      <Routes>
        <Route path="*" element={<Navigate to="/instruments" replace />} />
      </Routes>
    </div>
  )
}
