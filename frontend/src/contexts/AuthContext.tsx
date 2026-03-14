/**
 * AuthContext - user state, login, logout, token management.
 * WO-16: Authentication Integration with Amplify
 * Uses Amplify/Cognito when configured; mock auth for local dev when not.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import { fetchAuthSession, signIn as amplifySignIn, signOut as amplifySignOut } from 'aws-amplify/auth'
import { isAmplifyConfigured } from '@/lib/amplify'
import { setOn401Handler } from '@/lib/api'

export interface User {
  id: string
  email: string
  name?: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  getToken: () => string | null
}

const AuthContext = createContext<AuthContextValue | null>(null)

const STORAGE_KEY = 'gravitational_auth'

function loadStored(): { user: User; token: string } | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as { user: User; token: string }
  } catch {
    return null
  }
}

function saveStored(data: { user: User; token: string } | null) {
  if (data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

function getInitialState(): AuthState {
  const stored = loadStored()
  if (stored) {
    return {
      user: stored.user,
      token: stored.token,
      isLoading: false,
      isAuthenticated: true,
    }
  }
  return { user: null, token: null, isLoading: false, isAuthenticated: false }
}

function payloadToUser(payload: Record<string, unknown>): User {
  const sub = (payload.sub as string) || ''
  const email = (payload.email as string) || (payload['cognito:username'] as string) || ''
  const groups = (payload['cognito:groups'] as string[]) || []
  let role = 'researcher'
  if (groups.includes('admin')) role = 'admin'
  else if (groups.includes('viewer')) role = 'viewer'
  return {
    id: sub,
    email,
    name: (payload.name as string) || email.split('@')[0],
    role,
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() =>
    isAmplifyConfigured ? { user: null, token: null, isLoading: true, isAuthenticated: false } : getInitialState()
  )

  useEffect(() => {
    if (!isAmplifyConfigured) return
    let cancelled = false
    async function restoreSession() {
      try {
        const session = await fetchAuthSession()
        if (cancelled) return
        const idToken = session.tokens?.idToken
        if (idToken) {
          const payload = idToken.payload as Record<string, unknown>
          const user = payloadToUser(payload)
          const token = idToken.toString()
          setState({ user, token, isLoading: false, isAuthenticated: true })
        } else {
          setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
        }
      } catch {
        if (cancelled) return
        setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
      }
    }
    restoreSession()
    return () => { cancelled = true }
  }, [])

  // WO-16: Periodic token refresh (Cognito tokens ~1h expiry, refresh every 50 min)
  useEffect(() => {
    if (!isAmplifyConfigured || !state.isAuthenticated) return
    const REFRESH_INTERVAL_MS = 50 * 60 * 1000
    const id = setInterval(async () => {
      try {
        const session = await fetchAuthSession()
        const idToken = session.tokens?.idToken
        if (idToken) {
          const payload = idToken.payload as Record<string, unknown>
          const user = payloadToUser(payload)
          const token = idToken.toString()
          setState((prev) => (prev.isAuthenticated ? { ...prev, user, token } : prev))
        } else {
          setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
        }
      } catch {
        setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
      }
    }, REFRESH_INTERVAL_MS)
    return () => clearInterval(id)
  }, [isAmplifyConfigured, state.isAuthenticated])

  const logout = useCallback(async () => {
    if (isAmplifyConfigured) {
      try {
        await amplifySignOut()
      } catch {
        // ignore
      }
    }
    saveStored(null)
    setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    if (isAmplifyConfigured) {
      const { nextStep } = await amplifySignIn({ username: email, password })
      if (nextStep?.signInStep && nextStep.signInStep !== 'DONE') {
        throw new Error(`Additional sign-in step required (e.g. MFA). Not yet implemented.`)
      }
      const session = await fetchAuthSession()
      const idToken = session.tokens?.idToken
      if (!idToken) throw new Error('No session after sign in')
      const payload = idToken.payload as Record<string, unknown>
      const user = payloadToUser(payload)
      const token = idToken.toString()
      setState({ user, token, isLoading: false, isAuthenticated: true })
      return
    }
    const user: User = {
      id: `mock-${Date.now()}`,
      email,
      name: email.split('@')[0],
      role: 'researcher',
    }
    const token = `mock-jwt-${Date.now()}`
    saveStored({ user, token })
    setState({ user, token, isLoading: false, isAuthenticated: true })
  }, [])

  const getToken = useCallback(() => state.token, [state.token])

  // WO-16: Handle 401 - clear session so ProtectedRoute redirects to login
  useEffect(() => {
    setOn401Handler(() => {
      saveStored(null)
      setState({ user: null, token: null, isLoading: false, isAuthenticated: false })
    })
    return () => setOn401Handler(null)
  }, [])

  const value: AuthContextValue = {
    ...state,
    login,
    logout,
    getToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
