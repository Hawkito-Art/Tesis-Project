'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { variablesApi, indicatorsApi } from '@/features/indicators/api'
import type { IndicatorVariable } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

const schema = z.object({
  indicator: z.coerce.number({ required_error: 'Seleccione un indicador' }),
  name: z.string().min(1, 'Requerido'),
  label: z.string().min(1, 'Requerido'),
  description: z.string().optional().default(''),
  is_active: z.boolean().default(true),
})
type Values = z.infer<typeof schema>

export function VariablesClient() {
  const qc = useQueryClient()
  const [page, setPage] = useState(0)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<IndicatorVariable | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<IndicatorVariable | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['variables', page],
    queryFn: () => variablesApi.list({ page: page + 1 }),
  })
  const { data: indicators } = useQuery({
    queryKey: ['indicators', 0],
    queryFn: () => indicatorsApi.list(),
  })

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) })

  const createMutation = useMutation({
    mutationFn: (v: Values) => variablesApi.create(v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['variables'] }); toast.success('Variable creada'); setDialogOpen(false); reset() },
    onError: () => toast.error('Error'),
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, v }: { id: number; v: Values }) => variablesApi.update(id, v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['variables'] }); toast.success('Variable actualizada'); setDialogOpen(false); setEditTarget(null); reset() },
    onError: () => toast.error('Error'),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => variablesApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['variables'] }); toast.success('Variable eliminada'); setDeleteTarget(null) },
    onError: () => toast.error('Error'),
  })

  const columns: ColumnDef<IndicatorVariable>[] = [
    {
      id: 'indicator_code',
      header: 'Indicador',
      cell: ({ row }) => {
        const ind = indicators?.results.find((i) => i.id === row.original.indicator)
        return ind?.indicator ?? `#${row.original.indicator}`
      },
    },
    { accessorKey: 'name', header: 'Nombre', cell: ({ row }) => <code className="text-xs font-mono">{row.original.name}</code> },
    { accessorKey: 'label', header: 'Etiqueta' },
    {
      accessorKey: 'is_active',
      header: 'Activo',
      size: 60,
      cell: ({ row }) => (row.original.is_active ? 'Sí' : 'No'),
    },
    {
      id: 'actions', header: '', size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => {
            setEditTarget(row.original)
            reset({ indicator: row.original.indicator, name: row.original.name, label: row.original.label, description: row.original.description ?? '', is_active: row.original.is_active })
            setDialogOpen(true)
          }}><Pencil className="w-3.5 h-3.5" /></Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => setDeleteTarget(row.original)}><Trash2 className="w-3.5 h-3.5" /></Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div><h2 className="text-base font-semibold">Variables</h2><p className="text-xs text-muted-foreground">Variables estándar asociadas a indicadores</p></div>
        <Button size="sm" onClick={() => { setEditTarget(null); reset(); setDialogOpen(true) }}><Plus className="w-4 h-4 mr-1.5" />Nueva variable</Button>
      </div>
      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} totalCount={data?.count} pageIndex={page} serverPagination onPaginationChange={(p) => setPage(p.pageIndex)} emptyMessage="No hay variables registradas." />
      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar variable' : 'Nueva variable'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Indicador</Label>
              <Select value={String(watch('indicator') ?? '')} onValueChange={(v) => setValue('indicator', Number(v))}>
                <SelectTrigger><SelectValue placeholder="Seleccionar indicador" /></SelectTrigger>
                <SelectContent>
                  {indicators?.results.map((i) => <SelectItem key={i.id} value={String(i.id)}>{i.indicator} — {i.name}</SelectItem>)}
                </SelectContent>
              </Select>
              {errors.indicator && <p className="text-xs text-destructive">{errors.indicator.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5"><Label>Nombre interno</Label><Input placeholder="plan_anual" {...register('name')} className="font-mono text-sm" />{errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}</div>
              <div className="space-y-1.5"><Label>Etiqueta</Label><Input placeholder="Plan Anual" {...register('label')} />{errors.label && <p className="text-xs text-destructive">{errors.label.message}</p>}</div>
            </div>
            <div className="space-y-1.5"><Label>Descripción (opcional)</Label><Textarea placeholder="Descripción de la variable" {...register('description')} /></div>
            <div className="flex items-center gap-2">
              <Checkbox id="is_active" checked={watch('is_active')} onCheckedChange={(v) => setValue('is_active', v === true)} />
              <Label htmlFor="is_active" className="text-sm">Activo</Label>
            </div>
            <DialogFooter><Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button><Button type="submit" disabled={isSubmitting}>{isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}{editTarget ? 'Guardar' : 'Crear'}</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <AlertDialog open={!!deleteTarget} onOpenChange={(v) => !v && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader><AlertDialogTitle>¿Eliminar variable?</AlertDialogTitle><AlertDialogDescription>Se eliminará <strong>{deleteTarget?.name}</strong>.</AlertDialogDescription></AlertDialogHeader>
          <AlertDialogFooter><AlertDialogCancel>Cancelar</AlertDialogCancel><AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>Eliminar</AlertDialogAction></AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
