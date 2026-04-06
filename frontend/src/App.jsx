/**
 * App.jsx — root with React Router and protected routes.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Lesson from './pages/Lesson'
import Quiz from './pages/Quiz'
import Performance from './pages/Performance'

/** Redirect authenticated users away from public routes */
function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <FullPageSpinner />
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children
}

/** Redirect unauthenticated users to login */
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <FullPageSpinner />
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function FullPageSpinner() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg-primary)'
    }}>
      <div className="spinner" style={{ width: 40, height: 40 }} />
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<PublicRoute><Landing /></PublicRoute>} />
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />

      {/* Protected */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/lesson/:lessonId" element={<ProtectedRoute><Lesson /></ProtectedRoute>} />
      <Route path="/quiz/:lessonId" element={<ProtectedRoute><Quiz /></ProtectedRoute>} />
      <Route path="/performance" element={<ProtectedRoute><Performance /></ProtectedRoute>} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
