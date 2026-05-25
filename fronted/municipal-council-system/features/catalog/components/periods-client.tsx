'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { format } from 'date-fns'

import { periodsApi } from '@/features/catalog/api'
import type { Period } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { FormField } from '@/components/shared/form-field'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from '@/components/ui/alert-dialog'

const periodSchema = z.object({
  name: z.string().min(1, 'El nombre es requerido'),
  start_date: z.string().min(1, 'La fecha de inicio es requerida'),
  end_date: z.string().min(1, 'La fecha de fin es requerida'),
  is_active: z.boolean().default(false),
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

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<PeriodValues>({
    resolver: zodResolver(periodSchema),
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
    reset({ name: '', start_date: '', end_date: '', is_active: false })
    setDialogOpen(true)
  }

  function openEdit(p: Period) {
    setEditTarget(p)
    reset({ name: p.name, start_date: p.start_date, end_date: p.end_date, is_active: p.is_active })
    setDialogOpen(true)
  }

  async function onSubmit(values: PeriodValues) {
    if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, values })
    else await createMutation.mutateAsync(values)
  }

  const columns: ColumnDef<Period>[] = [
    { accessorKey: 'name', header: 'Nombre' },
    { accessorKey: 'start_date', header: 'Inicio', cell: ({ row }) => format(new Date(row.original.start_date), 'dd/MM/yyyy') },
    { accessorKey: 'end_date', header: 'Fin', cell: ({ row }) => format(new Date(row.original.end_date), 'dd/MM/yyyy') },
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
            <FormField
              label="Nombre"
              id="name"
              placeholder="Ej: 2024"
              error={errors.name?.message}
              {...register('name')}
            />
            <div className="grid grid-cols-2 gap-3">
              <FormField
                label="Fecha inicio"
                id="start_date"
                type="date"
                error={errors.start_date?.message}
                {...register('start_date')}
              />
              <FormField
                label="Fecha fin"
                id="end_date"
                type="date"
                error={errors.end_date?.message}
                {...register('end_date')}
              />
            </div>
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
