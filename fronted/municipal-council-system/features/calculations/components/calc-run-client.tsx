'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, Play, CheckCircle, ArrowRight } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'

import { calculationsApi } from '@/features/calculations/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { Calculation, Entity, Period } from '@/lib/types'

export function CalcRunClient() {
  const qc = useQueryClient()
  const [entityId, setEntityId] = useState('')
  const [periodId, setPeriodId] = useState('')
  const [calcName, setCalcName] = useState('')
  const [result, setResult] = useState<Calculation | null>(null)

  const { data: entities } = useQuery({ queryKey: ['entities'], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const runMutation = useMutation({
    mutationFn: () =>
      calculationsApi.run({
        entity: Number(entityId),
        period: Number(periodId),
        name: calcName || undefined,
      }),
    onSuccess: (data) => {
      setResult(data)
      qc.invalidateQueries({ queryKey: ['calculations'] })
      toast.success('Cálculo ejecutado correctamente')
    },
    onError: (error) => {
      const detail = (error as { response?: { data?: { error?: { detail?: string } } } })?.response?.data?.error?.detail
      toast.error(detail || 'Error al ejecutar el cálculo')
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!entityId || !periodId) {
      toast.error('Seleccione entidad y período')
      return
    }
    setResult(null)
    runMutation.mutate()
  }

  return (
    <div className="space-y-5 max-w-lg">
      <div>
        <h2 className="text-base font-semibold">Ejecutar cálculo</h2>
        <p className="text-xs text-muted-foreground">Seleccione los parámetros y ejecute el proceso de cálculo automático</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-card border border-border rounded-xl p-6 space-y-5">
        <div className="space-y-1.5">
          <Label>Entidad</Label>
          <Select value={entityId} onValueChange={setEntityId}>
            <SelectTrigger><SelectValue placeholder="Seleccionar entidad" /></SelectTrigger>
            <SelectContent>
              {entities?.results.map((e: Entity) => <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label>Período</Label>
          <Select value={periodId} onValueChange={setPeriodId}>
            <SelectTrigger><SelectValue placeholder="Seleccionar período" /></SelectTrigger>
            <SelectContent>
              {periods?.results.map((p: Period) => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label>Nombre del cálculo (opcional)</Label>
          <Input placeholder="Ej: Cierre mensual" value={calcName} onChange={(e) => setCalcName(e.target.value)} />
        </div>

        {result && (
          <div className="flex items-center justify-between text-sm text-emerald-600 bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              <span>Cálculo completado: <strong>{result.name}</strong></span>
            </div>
            <Button variant="link" size="sm" className="h-auto p-0 text-emerald-700" asChild>
              <Link href={`/dashboard/calculations/${result.id}`}>
                Ver detalles <ArrowRight className="w-3 h-3 ml-1" />
              </Link>
            </Button>
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
