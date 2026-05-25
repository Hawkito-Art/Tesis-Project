'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { indicatorGroupsApi } from '@/features/indicators/api'
import type { IndicatorGroup, GroupType } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const GROUP_TYPE_OPTIONS: { value: GroupType; label: string }[] = [
  { value: 'fundamental', label: 'Fundamental' },
  { value: 'limite', label: 'Límite' },
  { value: 'otro', label: 'Otro' },
]

const GROUP_TYPE_BADGE: Record<GroupType, { label: string; className: string }> = {
  fundamental: { label: 'Fundamental', className: 'bg-blue-100 text-blue-700 border border-blue-300' },
  limite: { label: 'Límite', className: 'bg-amber-100 text-amber-700 border border-amber-300' },
  otro: { label: 'Otro', className: 'bg-gray-100 text-gray-700 border border-gray-300' },
}

const schema = z.object({
  name: z.string().min(1, 'Requerido'),
  group_type: z.enum(['fundamental', 'limite', 'otro']),
  order: z.coerce.number().int().min(0).default(0),
  is_active: z.boolean().default(true),
})
type Values = z.infer<typeof schema>

export function GroupsClient() {
  const qc = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<IndicatorGroup | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<IndicatorGroup | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['indicator-groups'], queryFn: () => indicatorGroupsApi.list() })
  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) })

  const createMutation = useMutation({
    mutationFn: (v: Values) => indicatorGroupsApi.create(v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicator-groups'] }); toast.success('Grupo creado'); setDialogOpen(false); reset() },
    onError: () => toast.error('Error'),
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, v }: { id: number; v: Values }) => indicatorGroupsApi.update(id, v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicator-groups'] }); toast.success('Grupo actualizado'); setDialogOpen(false); setEditTarget(null); reset() },
    onError: () => toast.error('Error'),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => indicatorGroupsApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicator-groups'] }); toast.success('Grupo eliminado'); setDeleteTarget(null) },
    onError: () => toast.error('Error'),
  })

  const columns: ColumnDef<IndicatorGroup>[] = [
    { accessorKey: 'name', header: 'Nombre' },
    {
      accessorKey: 'group_type',
      header: 'Tipo',
      cell: ({ row }) => {
        const cfg = GROUP_TYPE_BADGE[row.original.group_type]
        return <Badge className={cn('font-medium', cfg.className)}>{cfg.label}</Badge>
      },
    },
    { accessorKey: 'order', header: 'Orden', size: 60 },
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
            reset({ name: row.original.name, group_type: row.original.group_type, order: row.original.order, is_active: row.original.is_active })
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
        <div><h2 className="text-base font-semibold">Grupos de indicadores</h2><p className="text-xs text-muted-foreground">Agrupaciones de indicadores económicos</p></div>
        <Button size="sm" onClick={() => { setEditTarget(null); reset(); setDialogOpen(true) }}><Plus className="w-4 h-4 mr-1.5" />Nuevo grupo</Button>
      </div>
      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} emptyMessage="No hay grupos registrados." />
      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar grupo' : 'Nuevo grupo'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <div className="space-y-1.5"><Label>Nombre</Label><Input placeholder="Nombre del grupo" {...register('name')} />{errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}</div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Tipo</Label>
                <Select value={watch('group_type')} onValueChange={(v) => setValue('group_type', v as GroupType)}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>{GROUP_TYPE_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}</SelectContent>
                </Select>
                {errors.group_type && <p className="text-xs text-destructive">{errors.group_type.message}</p>}
              </div>
              <div className="space-y-1.5"><Label>Orden</Label><Input type="number" min={0} {...register('order')} />{errors.order && <p className="text-xs text-destructive">{errors.order.message}</p>}</div>
            </div>
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
          <AlertDialogHeader><AlertDialogTitle>¿Eliminar grupo?</AlertDialogTitle><AlertDialogDescription>Se eliminará <strong>{deleteTarget?.name}</strong>.</AlertDialogDescription></AlertDialogHeader>
          <AlertDialogFooter><AlertDialogCancel>Cancelar</AlertDialogCancel><AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>Eliminar</AlertDialogAction></AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
