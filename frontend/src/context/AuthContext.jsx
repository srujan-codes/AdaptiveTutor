/**
 * AuthContext — global auth state provider.
 *
 * Provides: user, login(), register(), logout(), isAuthenticated, loading
 * Token is persisted in localStorage. On mount it re-hydrates via GET /auth/me.
 */
import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { authApi } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true) // true until hydration done

  // ── Hydrate from token on mount ─────────────────────
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }
    authApi.me()
      .then((res) => setUser(res.data))
      .catch(() => {
        // Invalid / expired token — clean up
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      })
      .finally(() => setLoading(false))
  }, [])

  // ── Login ────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const res = await authApi.login({ email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }, [])

  // ── Register ─────────────────────────────────────────
  const register = useCallback(async (email, username, password) => {
    const res = await authApi.register({ email, username, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }, [])

  // ── Logout ───────────────────────────────────────────
  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
  }, [])

  // ── Refresh user after difficulty change ─────────────
  const refreshUser = useCallback(async () => {
    try {
      const res = await authApi.me()
      setUser(res.data)
    } catch { /* ignore */ }
  }, [])

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
