'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { periodsApi } from '@/features/catalog/api'
import type { Period } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from '@/components/ui/alert-dialog'

const MONTHS = [
  { value: 1, label: 'Enero' }, { value: 2, label: 'Febrero' },
  { value: 3, label: 'Marzo' }, { value: 4, label: 'Abril' },
  { value: 5, label: 'Mayo' }, { value: 6, label: 'Junio' },
  { value: 7, label: 'Julio' }, { value: 8, label: 'Agosto' },
  { value: 9, label: 'Septiembre' }, { value: 10, label: 'Octubre' },
  { value: 11, label: 'Noviembre' }, { value: 12, label: 'Diciembre' },
]

const PERIOD_TYPES = [
  { value: 'mensual', label: 'Mensual' },
  { value: 'acumulado', label: 'Acumulado' },
  { value: 'anual', label: 'Anual' },
]

const periodSchema = z.object({
  year: z.coerce.number().int().min(2000, 'Año mínimo 2000').max(2100, 'Año inválido'),
  month: z.coerce.number().int().min(1).max(12),
  period_type: z.string().min(1, 'El tipo es requerido'),
  is_active: z.boolean().default(true),
})
type PeriodValues = z.infer<typeof periodSchema>

export function PeriodsClient() {
  const qc = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Period | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Period | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['periods'],
    queryFn: () => periodsApi.list(),
  })

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<PeriodValues>({
    resolver: zodResolver(periodSchema),
    defaultValues: { year: new Date().getFullYear(), month: 1, period_type: 'mensual', is_active: true },
  })

  const createMutation = useMutation({
    mutationFn: (v: PeriodValues) => periodsApi.create(v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['periods'] }); toast.success('Período creado'); setDialogOpen(false); reset() },
    onError: () => toast.error('Error al crear el período'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: PeriodValues }) => periodsApi.update(id, values),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['periods'] }); toast.success('Período actualizado'); setDialogOpen(false); setEditTarget(null); reset() },
    onError: () => toast.error('Error al actualizar el período'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => periodsApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['periods'] }); toast.success('Período eliminado'); setDeleteTarget(null) },
    onError: () => toast.error('Error al eliminar el período'),
  })

  function openCreate() {
    setEditTarget(null)
    reset({ year: new Date().getFullYear(), month: 1, period_type: 'mensual', is_active: true })
    setDialogOpen(true)
  }

  function openEdit(p: Period) {
    setEditTarget(p)
    reset({ year: p.year, month: p.month, period_type: p.period_type, is_active: p.is_active })
    setDialogOpen(true)
  }

  async function onSubmit(values: PeriodValues) {
    if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, values })
    else await createMutation.mutateAsync(values)
  }

  const typeLabels: Record<string, string> = { mensual: 'Mensual', acumulado: 'Acumulado', anual: 'Anual' }

  const columns: ColumnDef<Period>[] = [
    { accessorKey: 'name', header: 'Período' },
    { accessorKey: 'year', header: 'Año' },
    { accessorKey: 'month', header: 'Mes', cell: ({ row }) => MONTHS.find((m) => m.value === row.original.month)?.label ?? row.original.month },
    { accessorKey: 'period_type', header: 'Tipo', cell: ({ row }) => <Badge variant="secondary">{typeLabels[row.original.period_type] ?? row.original.period_type}</Badge> },
    { accessorKey: 'is_active', header: 'Estado', cell: ({ row }) => (
      <Badge variant={row.original.is_active ? 'default' : 'secondary'}>
        {row.original.is_active ? 'Activo' : 'Inactivo'}
      </Badge>
    )},
    {
      id: 'actions', header: '', size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openEdit(row.original)}><Pencil className="w-3.5 h-3.5" /></Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => setDeleteTarget(row.original)}><Trash2 className="w-3.5 h-3.5" /></Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold">Períodos</h2>
          <p className="text-xs text-muted-foreground">Períodos fiscales o de gestión</p>
        </div>
        <Button size="sm" onClick={openCreate}><Plus className="w-4 h-4 mr-1.5" />Nuevo período</Button>
      </div>

      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} emptyMessage="No hay períodos registrados." />

      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar período' : 'Nuevo período'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="year">Año</Label>
                <Input id="year" type="number" min={2000} max={2100} {...register('year')} />
                {errors.year && <p className="text-xs text-destructive">{errors.year.message}</p>}
              </div>
              <div className="space-y-1.5">
                <Label>Mes</Label>
                <Select value={String(watch('month'))} onValueChange={(v) => setValue('month', Number(v))}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar mes" /></SelectTrigger>
                  <SelectContent>
                    {MONTHS.map((m) => <SelectItem key={m.value} value={String(m.value)}>{m.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>Tipo de período</Label>
              <Select value={watch('period_type')} onValueChange={(v) => setValue('period_type', v)}>
                <SelectTrigger><SelectValue placeholder="Seleccionar tipo" /></SelectTrigger>
                <SelectContent>
                  {PERIOD_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                </SelectContent>
              </Select>
              {errors.period_type && <p className="text-xs text-destructive">{errors.period_type.message}</p>}
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" {...register('is_active')} className="rounded border-border" />
              Período activo
            </label>
            <DialogFooter className="pt-2">
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                {editTarget ? 'Guardar cambios' : 'Crear período'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteTarget} onOpenChange={(v) => !v && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar período?</AlertDialogTitle>
            <AlertDialogDescription>Se eliminará el período <strong>{deleteTarget?.name}</strong>.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>Eliminar</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
