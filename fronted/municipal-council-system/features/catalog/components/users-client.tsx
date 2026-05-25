'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { usersApi, rolesApi, entitiesApi } from '@/features/catalog/api'
import type { User } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { FormField } from '@/components/shared/form-field'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

const userSchema = z.object({
  email: z.string().email('Correo inválido'),
  first_name: z.string().min(1, 'Requerido'),
  last_name: z.string().min(1, 'Requerido'),
  role: z.coerce.number().optional(),
  entity: z.coerce.number().optional(),
})
type UserValues = z.infer<typeof userSchema>

export function UsersClient() {
  const qc = useQueryClient()
  const [page, setPage] = useState(0)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<User | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['users', page], queryFn: () => usersApi.list({ page: page + 1 }) })
  const { data: rolesData } = useQuery({ queryKey: ['roles'], queryFn: () => rolesApi.list() })
  const { data: entitiesData } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<UserValues>({ resolver: zodResolver(userSchema) })

  const createMutation = useMutation({
    mutationFn: (v: UserValues) => usersApi.create({ ...v, role: v.role ?? null, entity: v.entity ?? null }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); toast.success('Usuario creado'); setDialogOpen(false); reset() },
    onError: () => toast.error('Error al crear el usuario'),
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: UserValues }) => usersApi.update(id, { ...values, role: values.role ?? null, entity: values.entity ?? null }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); toast.success('Usuario actualizado'); setDialogOpen(false); setEditTarget(null); reset() },
    onError: () => toast.error('Error al actualizar el usuario'),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => usersApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); toast.success('Usuario eliminado'); setDeleteTarget(null) },
    onError: () => toast.error('Error al eliminar el usuario'),
  })

  function openCreate() {
    setEditTarget(null)
    reset({ email: '', first_name: '', last_name: '' })
    setDialogOpen(true)
  }

  function openEdit(u: User) {
    setEditTarget(u)
    reset({ email: u.email, first_name: u.first_name, last_name: u.last_name, role: u.role?.id, entity: u.entity?.id })
    setDialogOpen(true)
  }

  const columns: ColumnDef<User>[] = [
    { accessorKey: 'email', header: 'Correo' },
    { accessorKey: 'first_name', header: 'Nombre', cell: ({ row }) => `${row.original.first_name} ${row.original.last_name}` },
    { accessorKey: 'role', header: 'Rol', cell: ({ row }) => row.original.role?.name ?? '—' },
    { accessorKey: 'entity', header: 'Entidad', cell: ({ row }) => row.original.entity?.name ?? '—' },
    { accessorKey: 'is_active', header: 'Estado', cell: ({ row }) => <Badge variant={row.original.is_active ? 'default' : 'secondary'}>{row.original.is_active ? 'Activo' : 'Inactivo'}</Badge> },
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
        <div><h2 className="text-base font-semibold">Usuarios</h2><p className="text-xs text-muted-foreground">Gestión de usuarios del sistema</p></div>
        <Button size="sm" onClick={openCreate}><Plus className="w-4 h-4 mr-1.5" />Nuevo usuario</Button>
      </div>

      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} totalCount={data?.count} pageIndex={page} serverPagination onPaginationChange={(p) => setPage(p.pageIndex)} emptyMessage="No hay usuarios registrados." />

      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar usuario' : 'Nuevo usuario'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, values: v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <FormField
                label="Nombre"
                id="first_name"
                placeholder="Nombre"
                error={errors.first_name?.message}
                {...register('first_name')}
              />
              <FormField
                label="Apellido"
                id="last_name"
                placeholder="Apellido"
                error={errors.last_name?.message}
                {...register('last_name')}
              />
            </div>
            <FormField
              label="Correo electrónico"
              id="user-email"
              type="email"
              placeholder="usuario@municipio.gob"
              error={errors.email?.message}
              {...register('email')}
            />
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Rol</Label>
                <Select value={String(watch('role') ?? '')} onValueChange={(v) => setValue('role', Number(v))}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>{rolesData?.results.map((r) => <SelectItem key={r.id} value={String(r.id)}>{r.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Entidad</Label>
                <Select value={String(watch('entity') ?? '')} onValueChange={(v) => setValue('entity', Number(v))}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>{entitiesData?.results.map((e) => <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={isSubmitting}>{isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}{editTarget ? 'Guardar' : 'Crear'}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteTarget} onOpenChange={(v) => !v && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader><AlertDialogTitle>¿Eliminar usuario?</AlertDialogTitle><AlertDialogDescription>Se eliminará <strong>{deleteTarget?.email}</strong>.</AlertDialogDescription></AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>Eliminar</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
