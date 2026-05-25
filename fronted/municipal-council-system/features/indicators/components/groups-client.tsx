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
import type { IndicatorGroup } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

const schema = z.object({
  name: z.string().min(1, 'Requerido'),
  description: z.string().optional(),
})
type Values = z.infer<typeof schema>

export function GroupsClient() {
  const qc = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<IndicatorGroup | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<IndicatorGroup | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['indicator-groups'], queryFn: () => indicatorGroupsApi.list() })
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) })

  const createMutation = useMutation({ mutationFn: (v: Values) => indicatorGroupsApi.create(v), onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicator-groups'] }); toast.success('Grupo creado'); setDialogOpen(false); reset() }, onError: () => toast.error('Error') })
  const updateMutation = useMutation({ mutationFn: ({ id, v }: { id: number; v: Values }) => indicatorGroupsApi.update(id, v), onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicator-groups'] }); toast.success('Grupo actualizado'); setDialogOpen(false); setEditTarget(null); reset() }, onError: () => toast.error('Error') })
  const deleteMutation = useMutation({ mutationFn: (id: number) => indicatorGroupsApi.remove(id), onSuccess: () => { qc.invalidateQueries({ queryKey: ['indicator-groups'] }); toast.success('Grupo eliminado'); setDeleteTarget(null) }, onError: () => toast.error('Error') })

  const columns: ColumnDef<IndicatorGroup>[] = [
    { accessorKey: 'name', header: 'Nombre' },
    { accessorKey: 'description', header: 'Descripción', cell: ({ row }) => row.original.description || '—' },
    {
      id: 'actions', header: '', size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => { setEditTarget(row.original); reset({ name: row.original.name, description: row.original.description ?? '' }); setDialogOpen(true) }}><Pencil className="w-3.5 h-3.5" /></Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => setDeleteTarget(row.original)}><Trash2 className="w-3.5 h-3.5" /></Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div><h2 className="text-base font-semibold">Grupos de indicadores</h2><p className="text-xs text-muted-foreground">Agrupaciones de indicadores económicos</p></div>
        <Button size="sm" onClick={() => { setEditTarget(null); reset({ name: '', description: '' }); setDialogOpen(true) }}><Plus className="w-4 h-4 mr-1.5" />Nuevo grupo</Button>
      </div>
      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} emptyMessage="No hay grupos registrados." />
      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar grupo' : 'Nuevo grupo'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <div className="space-y-1.5"><Label>Nombre</Label><Input placeholder="Nombre del grupo" {...register('name')} />{errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}</div>
            <div className="space-y-1.5"><Label>Descripción (opcional)</Label><Input placeholder="Descripción" {...register('description')} /></div>
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
