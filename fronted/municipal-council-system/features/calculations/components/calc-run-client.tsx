'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Loader2, Play, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

import { calculationsApi } from '@/features/calculations/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const CALC_TYPES = [
  { value: 'full', label: 'Cálculo completo' },
  { value: 'partial', label: 'Cálculo parcial' },
  { value: 'projection', label: 'Proyección' },
]

export function CalcRunClient() {
  const [entityId, setEntityId] = useState('')
  const [periodId, setPeriodId] = useState('')
  const [calcType, setCalcType] = useState('')
  const [success, setSuccess] = useState(false)

  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const runMutation = useMutation({
    mutationFn: () =>
      calculationsApi.run({
        entity: Number(entityId),
        period: Number(periodId),
        calc_type: calcType,
      }),
    onSuccess: () => {
      setSuccess(true)
      toast.success('Cálculo ejecutado correctamente')
    },
    onError: () => toast.error('Error al ejecutar el cálculo'),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!entityId || !periodId || !calcType) {
      toast.error('Complete todos los campos')
      return
    }
    setSuccess(false)
    runMutation.mutate()
  }

  return (
    <div className="space-y-5 max-w-lg">
      <div>
        <h2 className="text-base font-semibold">Ejecutar cálculo</h2>
        <p className="text-xs text-muted-foreground">Seleccione los parámetros y ejecute el proceso de cálculo</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-card border border-border rounded-xl p-6 space-y-5">
        <div className="space-y-1.5">
          <Label>Entidad</Label>
          <Select value={entityId} onValueChange={setEntityId}>
            <SelectTrigger>
              <SelectValue placeholder="Seleccionar entidad" />
            </SelectTrigger>
            <SelectContent>
              {entities?.results.map((e) => (
                <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label>Período</Label>
          <Select value={periodId} onValueChange={setPeriodId}>
            <SelectTrigger>
              <SelectValue placeholder="Seleccionar período" />
            </SelectTrigger>
            <SelectContent>
              {periods?.results.map((p) => (
                <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label>Tipo de cálculo</Label>
          <Select value={calcType} onValueChange={setCalcType}>
            <SelectTrigger>
              <SelectValue placeholder="Seleccionar tipo" />
            </SelectTrigger>
            <SelectContent>
              {CALC_TYPES.map((t) => (
                <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {success && (
          <div className="flex items-center gap-2 text-sm text-emerald-600 bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3">
            <CheckCircle className="w-4 h-4" />
            El cálculo se ejecutó correctamente.
          </div>
        )}

        <Button type="submit" className="w-full" disabled={runMutation.isPending}>
          {runMutation.isPending
            ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Ejecutando...</>
            : <><Play className="w-4 h-4 mr-2" />Ejecutar cálculo</>}
        </Button>
      </form>
    </div>
  )
}
