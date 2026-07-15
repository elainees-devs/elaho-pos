import { createContext, useContext, useState, useCallback, type ReactNode } from "react"

interface AuthContextValue {
  isAuthenticated: boolean
  login: (tokens: { access: string; refresh: string }) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem("access_token")
  })

  const login = useCallback((tokens: { access: string; refresh: string }) => {
    localStorage.setItem("access_token", tokens.access)
    localStorage.setItem("refresh_token", tokens.refresh)
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setIsAuthenticated(false)
  }, [])

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
