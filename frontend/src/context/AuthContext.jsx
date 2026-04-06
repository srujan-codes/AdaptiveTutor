/**
 * AuthContext — React context for authentication state.
 * Implementation: TICKET-015
 */

import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

// TODO: [TICKET-015] Implement full auth context
// - user state, login(), logout(), register()
// - Token persistence in localStorage
// - Auto-load user on mount if token exists

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const value = {
    user,
    isAuthenticated: !!user,
    login: async () => { /* TODO */ },
    logout: () => { setUser(null) },
    register: async () => { /* TODO */ },
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
