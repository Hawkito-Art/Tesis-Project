'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { Loader2, Upload } from 'lucide-react'
import { toast } from 'sonner'

import { ingestionApi } from '@/features/ingestion/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import { FileUpload } from '@/components/shared/file-upload'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'

const IMPORT_TYPES = [
  { value: 'budget', label: 'Presupuesto' },
  { value: 'indicators', label: 'Indicadores' },
  { value: 'records', label: 'Registros de indicadores' },
]

export function UploadClient() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [importType, setImportType] = useState('')
  const [entityId, setEntityId] = useState('')
  const [periodId, setPeriodId] = useState('')
  const [loading, setLoading] = useState(false)

  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file || !importType) {
      toast.error('Seleccione un archivo y un tipo de importación')
      return
    }
    setLoading(true)
    try {
      await ingestionApi.upload(
        file,
        importType,
        entityId ? Number(entityId) : undefined,
        periodId ? Number(periodId) : undefined,
      )
      toast.success('Archivo cargado correctamente. Puede seguir el progreso en Trabajos.')
      router.push('/dashboard/ingestion/jobs')
    } catch {
      toast.error('Error al cargar el archivo. Verifique el formato e inténtelo nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-5 max-w-xl">
      <div>
        <h2 className="text-base font-semibold">Cargar archivo</h2>
        <p className="text-xs text-muted-foreground">Importe datos desde un archivo Excel</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-card border border-border rounded-xl p-6 space-y-5">
        <FileUpload onFileSelect={setFile} />

        <div className="space-y-1.5">
          <Label>Tipo de importación</Label>
          <Select value={importType} onValueChange={setImportType}>
            <SelectTrigger>
              <SelectValue placeholder="Seleccionar tipo" />
            </SelectTrigger>
            <SelectContent>
              {IMPORT_TYPES.map((t) => (
                <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label>Entidad (opcional)</Label>
            <Select value={entityId} onValueChange={setEntityId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Sin especificar</SelectItem>
                {entities?.results.map((e) => (
                  <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Período (opcional)</Label>
            <Select value={periodId} onValueChange={setPeriodId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Sin especificar</SelectItem>
                {periods?.results.map((p) => (
                  <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button type="submit" className="w-full" disabled={loading || !file || !importType}>
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
          Cargar archivo
        </Button>
      </form>
    </div>
  )
}
