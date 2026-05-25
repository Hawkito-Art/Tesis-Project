'use client'

import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, setAccessToken } from '@/lib/axios'
import type { User, LoginCredentials } from '@/lib/types'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await apiClient.get<User>('/accounts/me/')
      setUser(data)
    } catch {
      setUser(null)
    }
  }, [])

  // On mount: attempt to refresh token (cookie-based), then fetch user
  useEffect(() => {
    const init = async () => {
      try {
        // Development mode: skip real auth, use mock user
        if (process.env.NODE_ENV === 'development') {
          setUser({
            id: 1,
            email: 'admin@test.com',
            first_name: 'Admin',
            last_name: 'Usuario',
            role: { id: 1, name: 'Administrator', permissions: [] },
            entity: { id: 1, name: 'Municipalidad Central' },
            is_active: true,
          })
          setIsLoading(false)
          return
        }

        const { data } = await apiClient.post<{ access: string }>(
          '/accounts/token/refresh/',
        )
        setAccessToken(data.access)
        await fetchMe()
      } catch {
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }
    init()
  }, [fetchMe])

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      // Development mode: skip real auth and go straight to dashboard
      if (process.env.NODE_ENV === 'development') {
        router.push('/dashboard')
        return
      }
      const { data } = await apiClient.post<{ access: string; refresh: string }>(
        '/accounts/token/',
        credentials,
      )
      setAccessToken(data.access)
      await fetchMe()
      router.push('/dashboard')
    },
    [fetchMe, router],
  )

  const logout = useCallback(async () => {
    try {
      await apiClient.post('/accounts/logout/')
    } catch {
      // ignore
    } finally {
      setAccessToken(null)
      setUser(null)
      router.push('/login')
    }
  }, [router])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
