'use client'

import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, setAccessToken } from '@/lib/axios'
import type { User, LoginCredentials } from '@/lib/types'

const REFRESH_TOKEN_KEY = 'refresh_token'
const COOKIE_NAME = 'is_logged_in'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

function setLoggedInCookie() {
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString()
  document.cookie = `${COOKIE_NAME}=true; path=/; expires=${expires}; SameSite=Lax`
}

function clearLoggedInCookie() {
  document.cookie = `${COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const fetchMe = useCallback(async () => {
    try {
      const { data } = await apiClient.get<User>('/auth/me/')
      setUser(data)
    } catch {
      setUser(null)
    }
  }, [])

  useEffect(() => {
    const init = async () => {
      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (!refreshToken) {
          setIsLoading(false)
          return
        }

        const { data } = await apiClient.post<{ access: string }>(
          '/auth/refresh/',
          { refresh: refreshToken },
        )
        setAccessToken(data.access)
        await fetchMe()
      } catch {
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        clearLoggedInCookie()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }
    init()
  }, [fetchMe])

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const { data } = await apiClient.post<{ access: string; refresh: string }>(
        '/auth/login/',
        credentials,
      )
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh)
      setLoggedInCookie()
      setAccessToken(data.access)
      await fetchMe()
      router.push('/dashboard')
    },
    [fetchMe, router],
  )

  const logout = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      if (refreshToken) {
        await apiClient.post('/auth/logout/', { refresh: refreshToken })
      }
    } catch {
      // ignore
    } finally {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      clearLoggedInCookie()
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
