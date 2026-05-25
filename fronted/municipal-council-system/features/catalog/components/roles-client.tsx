'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { rolesApi } from '@/features/catalog/api'
import type { Role } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { FormField } from '@/components/shared/form-field'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

const roleSchema = z.object({ name: z.string().min(1, 'El nombre es requerido') })
type RoleValues = z.infer<typeof roleSchema>

export function RolesClient() {
  const qc = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Role | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Role | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['roles'], queryFn: () => rolesApi.list() })

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<RoleValues>({ resolver: zodResolver(roleSchema) })

  const createMutation = useMutation({
    mutationFn: (v: RoleValues) => rolesApi.create(v),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['roles'] }); toast.success('Rol creado'); setDialogOpen(false); reset() },
    onError: () => toast.error('Error al crear el rol'),
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: RoleValues }) => rolesApi.update(id, values),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['roles'] }); toast.success('Rol actualizado'); setDialogOpen(false); setEditTarget(null); reset() },
    onError: () => toast.error('Error al actualizar el rol'),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => rolesApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['roles'] }); toast.success('Rol eliminado'); setDeleteTarget(null) },
    onError: () => toast.error('Error al eliminar el rol'),
  })

  const columns: ColumnDef<Role>[] = [
    { accessorKey: 'id', header: 'ID', size: 60 },
    { accessorKey: 'name', header: 'Nombre' },
    {
      id: 'actions', header: '', size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => { setEditTarget(row.original); reset({ name: row.original.name }); setDialogOpen(true) }}><Pencil className="w-3.5 h-3.5" /></Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => setDeleteTarget(row.original)}><Trash2 className="w-3.5 h-3.5" /></Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div><h2 className="text-base font-semibold">Roles</h2><p className="text-xs text-muted-foreground">Roles del sistema</p></div>
        <Button size="sm" onClick={() => { setEditTarget(null); reset({ name: '' }); setDialogOpen(true) }}><Plus className="w-4 h-4 mr-1.5" />Nuevo rol</Button>
      </div>

      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} emptyMessage="No hay roles registrados." />

      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar rol' : 'Nuevo rol'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, values: v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <FormField
              label="Nombre del rol"
              id="rolname"
              placeholder="Ej: Administrador"
              error={errors.name?.message}
              {...register('name')}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={isSubmitting}>{isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}{editTarget ? 'Guardar' : 'Crear'}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteTarget} onOpenChange={(v) => !v && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader><AlertDialogTitle>¿Eliminar rol?</AlertDialogTitle><AlertDialogDescription>Se eliminará el rol <strong>{deleteTarget?.name}</strong>.</AlertDialogDescription></AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>Eliminar</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
