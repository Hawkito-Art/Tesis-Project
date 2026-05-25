'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2, ExternalLink } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'

import { indicatorsApi, indicatorGroupsApi } from '@/features/indicators/api'
import type { Indicator, IndicatorUnit } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

const UNIT_OPTIONS: IndicatorUnit[] = ['MP', 'U', 'p', 'peso', 'Coef']

const schema = z.object({
  indicator: z.string().min(1, 'Requerido'),
  name: z.string().min(1, 'Requerido'),
  unit: z.enum(['MP', 'U', 'p', 'peso', 'Coef']),
  group: z.coerce.number({ required_error: 'Seleccione un grupo' }),
  description: z.string().optional().default(''),
  is_active: z.boolean().default(true),
})
type Values = z.infer<typeof schema>

export function IndicatorsClient() {
  const qc = useQueryClient()
  const [page, setPage] = useState(0)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Indicator | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Indicator | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['indicators', page], queryFn: () => indicatorsApi.list({ page: page + 1 }) })
  const { data: groups } = useQuery({ queryKey: ['indicator-groups'], queryFn: () => indicatorGroupsApi.list() })

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) })

  const createMutation = useMutation({
    mutationFn: (v: Values) => indicatorsApi.create(v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicators'] }); toast.success('Indicador creado'); setDialogOpen(false); reset() },
    onError: () => toast.error('Error'),
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, v }: { id: number; v: Values }) => indicatorsApi.update(id, v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicators'] }); toast.success('Indicador actualizado'); setDialogOpen(false); setEditTarget(null); reset() },
    onError: () => toast.error('Error'),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => indicatorsApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicators'] }); toast.success('Indicador eliminado'); setDeleteTarget(null) },
    onError: () => toast.error('Error'),
  })

  const columns: ColumnDef<Indicator>[] = [
    { accessorKey: 'indicator', header: 'Código', size: 120 },
    { accessorKey: 'name', header: 'Nombre' },
    {
      accessorKey: 'unit',
      header: 'U/M',
      size: 60,
      cell: ({ row }) => <Badge variant="outline" className="text-xs font-mono">{row.original.unit}</Badge>,
    },
    { accessorKey: 'group_name', header: 'Grupo' },
    {
      accessorKey: 'is_active',
      header: 'Activo',
      size: 60,
      cell: ({ row }) => (row.original.is_active ? 'Sí' : 'No'),
    },
    {
      id: 'actions', header: '', size: 100,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" asChild>
            <Link href={`/dashboard/indicators/${row.original.id}`}><ExternalLink className="w-3.5 h-3.5" /></Link>
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => {
            setEditTarget(row.original)
            reset({ indicator: row.original.indicator, name: row.original.name, unit: row.original.unit, group: row.original.group, description: row.original.description ?? '', is_active: row.original.is_active })
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
        <div><h2 className="text-base font-semibold">Indicadores</h2><p className="text-xs text-muted-foreground">Indicadores económicos con unidades y variables</p></div>
        <Button size="sm" onClick={() => { setEditTarget(null); reset(); setDialogOpen(true) }}><Plus className="w-4 h-4 mr-1.5" />Nuevo indicador</Button>
      </div>
      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} totalCount={data?.count} pageIndex={page} serverPagination onPaginationChange={(p) => setPage(p.pageIndex)} emptyMessage="No hay indicadores registrados." />

      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar indicador' : 'Nuevo indicador'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5"><Label>Código</Label><Input placeholder="VENTAS_TOT" {...register('indicator')} className="font-mono text-sm" />{errors.indicator && <p className="text-xs text-destructive">{errors.indicator.message}</p>}</div>
              <div className="space-y-1.5">
                <Label>Unidad</Label>
                <Select value={watch('unit')} onValueChange={(v) => setValue('unit', v as IndicatorUnit)}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>{UNIT_OPTIONS.map((u) => <SelectItem key={u} value={u}>{u}</SelectItem>)}</SelectContent>
                </Select>
                {errors.unit && <p className="text-xs text-destructive">{errors.unit.message}</p>}
              </div>
            </div>
            <div className="space-y-1.5"><Label>Nombre</Label><Input placeholder="Nombre del indicador" {...register('name')} />{errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}</div>
            <div className="space-y-1.5">
              <Label>Grupo</Label>
              <Select value={String(watch('group') ?? '')} onValueChange={(v) => setValue('group', Number(v))}>
                <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                <SelectContent>{groups?.results.map((g) => <SelectItem key={g.id} value={String(g.id)}>{g.name}</SelectItem>)}</SelectContent>
              </Select>
              {errors.group && <p className="text-xs text-destructive">{errors.group.message}</p>}
            </div>
            <div className="space-y-1.5"><Label>Descripción (opcional)</Label><Textarea placeholder="Descripción del indicador" {...register('description')} /></div>
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
          <AlertDialogHeader><AlertDialogTitle>¿Eliminar indicador?</AlertDialogTitle><AlertDialogDescription>Se eliminará <strong>{deleteTarget?.name}</strong>.</AlertDialogDescription></AlertDialogHeader>
          <AlertDialogFooter><AlertDialogCancel>Cancelar</AlertDialogCancel><AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>Eliminar</AlertDialogAction></AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
