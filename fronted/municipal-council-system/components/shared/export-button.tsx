'use client'

import { useState } from 'react'
import { Download, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import apiClient from '@/lib/axios'

interface ExportButtonProps {
  endpoint: string
  filename?: string
  params?: Record<string, string | number | undefined>
  label?: string
  variant?: 'default' | 'outline' | 'secondary' | 'ghost'
}

export function ExportButton({
  endpoint,
  filename = 'export.xlsx',
  params,
  label = 'Exportar XLSX',
  variant = 'outline',
}: ExportButtonProps) {
  const [loading, setLoading] = useState(false)

  async function handleExport() {
    setLoading(true)
    try {
      const response = await apiClient.get(endpoint, {
        params,
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Archivo exportado correctamente')
    } catch {
      toast.error('Error al exportar el archivo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button variant={variant} size="sm" onClick={handleExport} disabled={loading}>
      {loading ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        <Download className="w-4 h-4 mr-2" />
      )}
      {label}
    </Button>
  )
}
