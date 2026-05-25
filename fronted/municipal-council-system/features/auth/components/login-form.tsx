'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2, Eye, EyeOff } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/providers/auth-provider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FormField } from '@/components/shared/form-field'

const loginSchema = z.object({
  email: z.string().email('Correo electrónico inválido'),
  password: z.string().min(1, 'La contraseña es requerida'),
})

type LoginValues = z.infer<typeof loginSchema>

export function LoginForm() {
  const { login } = useAuth()
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
  })

  async function onSubmit(values: LoginValues) {
    try {
      await login(values)
      toast.success('Sesión iniciada correctamente')
    } catch {
      toast.error('Credenciales incorrectas. Verifique su correo y contraseña.')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <FormField
        label="Correo electrónico"
        id="email"
        type="email"
        placeholder="usuario@municipio.gob"
        autoComplete="email"
        error={errors.email?.message}
        {...register('email')}
      />

      <div className="space-y-1.5">
        <Label htmlFor="password">Contraseña</Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••"
            autoComplete="current-password"
            className="pr-10"
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? 'password-error' : undefined}
            {...register('password')}
          />
          <button
            type="button"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        {errors.password && (
          <p id="password-error" role="alert" className="flex items-center gap-1 text-xs text-destructive">
            <span className="inline-block w-3 h-3 shrink-0">&#9888;</span>
            {errors.password.message}
          </p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
        Iniciar sesión
      </Button>
    </form>
  )
}
