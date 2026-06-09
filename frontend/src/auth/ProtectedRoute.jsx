import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthProvider'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, onboardingCompleted, loading } = useAuth()

  if (loading) return null

  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (!onboardingCompleted) return <Navigate to="/onboarding" replace />

  return children
}
