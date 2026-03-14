/**
 * Login page - standalone sign-in view.
 * WO-16: Redirects to original URL after login when coming from ProtectedRoute.
 */

import { useLocation, useNavigate } from 'react-router-dom'
import { LoginForm } from '@/components/auth/LoginForm'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from || '/'

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-8">
      <div className="w-full max-w-sm space-y-6 text-center">
        <h1 className="text-2xl font-bold text-foreground">
          ArchiMeades · Gravitational Physics
        </h1>
        <p className="text-muted-foreground text-sm">
          Sign in to access theories, simulations, and research tools.
        </p>
        <LoginForm onSuccess={() => navigate(from, { replace: true })} />
      </div>
    </div>
  )
}
