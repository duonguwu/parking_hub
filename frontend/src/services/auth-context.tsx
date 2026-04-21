import { useState, useEffect, createContext, useContext, useCallback } from 'react'
import type { ReactNode } from 'react'
import { authApi, type User } from '@/services/api'

interface AuthState {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: { username: string; password: string; name: string; email: string; phone: string }) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    authApi.me().then((u) => {
      setUser(u)
      setLoading(false)
    })
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const u = await authApi.login(username, password)
    setUser(u)
  }, [])

  const register = useCallback(async (data: { username: string; password: string; name: string; email: string; phone: string }) => {
    const u = await authApi.register(data)
    setUser(u)
  }, [])

  const logout = useCallback(async () => {
    await authApi.logout()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
