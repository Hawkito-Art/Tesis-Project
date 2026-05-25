'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { AlertCircle } from 'lucide-react'

interface FormFieldProps extends React.ComponentProps<'input'> {
  label: string
  error?: string
  hint?: string
}

export function FormField({ label, error, hint, id, className, ...props }: FormFieldProps) {
  const fieldId = id ?? label.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="space-y-1.5">
      <Label htmlFor={fieldId}>{label}</Label>
      <Input
        id={fieldId}
        aria-invalid={!!error}
        aria-describedby={error ? `${fieldId}-error` : hint ? `${fieldId}-hint` : undefined}
        className={className}
        {...props}
      />
      {hint && !error && (
        <p id={`${fieldId}-hint`} className="text-xs text-muted-foreground">{hint}</p>
      )}
      {error && (
        <p id={`${fieldId}-error`} role="alert" className="flex items-center gap-1 text-xs text-destructive">
          <AlertCircle className="w-3 h-3 shrink-0" />
          {error}
        </p>
      )}
    </div>
  )
}
