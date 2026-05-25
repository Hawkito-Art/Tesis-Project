'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { LoginForm } from '@/features/auth/components/login-form'
import { useAuth } from '@/providers/auth-provider'
import { Building2 } from 'lucide-react'

export default function LoginPage() {
  const { isLoading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace('/dashboard')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) {
    return null
  }

  if (isAuthenticated) {
    return null
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md px-6">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-primary mb-4">
            <Building2 className="w-7 h-7 text-primary-foreground" />
          </div>
          <h1 className="text-2xl font-semibold text-foreground text-balance">
            Consejo de Administración Municipal
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Ingrese sus credenciales para continuar
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-8 shadow-sm">
          <LoginForm />
        </div>

        <p className="text-center text-xs text-muted-foreground mt-6">
          SIGCAM &copy; {new Date().getFullYear()} — Sistema de Gestión Municipal
        </p>
      </div>
    </main>
  )
}
