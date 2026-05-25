'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { variablesApi } from '@/features/indicators/api'
import type { Variable } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'

const TYPES = ['numeric', 'percentage', 'currency', 'text']

const schema = z.object({
  name: z.string().min(1, 'Requerido'),
  code: z.string().min(1, 'Requerido'),
  type: z.string().min(1, 'Requerido'),
})
type Values = z.infer<typeof schema>

export function VariablesClient() {
  const qc = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Variable | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Variable | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['variables'], queryFn: () => variablesApi.list() })
  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<Values>({ resolver: zodResolver(schema) })

  const createMutation = useMutation({ mutationFn: (v: Values) => variablesApi.create(v), onSuccess: () => { qc.invalidateQueries({ queryKey: ['variables'] }); toast.success('Variable creada'); setDialogOpen(false); reset() }, onError: () => toast.error('Error') })
  const updateMutation = useMutation({ mutationFn: ({ id, v }: { id: number; v: Values }) => variablesApi.update(id, v), onSuccess: () => { qc.invalidateQueries({ queryKey: ['variables'] }); toast.success('Variable actualizada'); setDialogOpen(false); setEditTarget(null); reset() }, onError: () => toast.error('Error') })
  const deleteMutation = useMutation({ mutationFn: (id: number) => variablesApi.remove(id), onSuccess: () => { qc.invalidateQueries({ queryKey: ['variables'] }); toast.success('Variable eliminada'); setDeleteTarget(null) }, onError: () => toast.error('Error') })

  const columns: ColumnDef<Variable>[] = [
    { accessorKey: 'code', header: 'Código', size: 100 },
    { accessorKey: 'name', header: 'Nombre' },
    { accessorKey: 'type', header: 'Tipo', cell: ({ row }) => <span className="capitalize">{row.original.type}</span> },
    {
      id: 'actions', header: '', size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => { setEditTarget(row.original); reset({ name: row.original.name, code: row.original.code, type: row.original.type }); setDialogOpen(true) }}><Pencil className="w-3.5 h-3.5" /></Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => setDeleteTarget(row.original)}><Trash2 className="w-3.5 h-3.5" /></Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div><h2 className="text-base font-semibold">Variables</h2><p className="text-xs text-muted-foreground">Variables estándar usadas en indicadores</p></div>
        <Button size="sm" onClick={() => { setEditTarget(null); reset(); setDialogOpen(true) }}><Plus className="w-4 h-4 mr-1.5" />Nueva variable</Button>
      </div>
      <DataTable columns={columns} data={data?.results ?? []} isLoading={isLoading} emptyMessage="No hay variables registradas." />
      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader><DialogTitle>{editTarget ? 'Editar variable' : 'Nueva variable'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(async (v) => { if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, v }); else await createMutation.mutateAsync(v) })} className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5"><Label>Código</Label><Input placeholder="VAR-001" {...register('code')} />{errors.code && <p className="text-xs text-destructive">{errors.code.message}</p>}</div>
              <div className="space-y-1.5">
                <Label>Tipo</Label>
                <Select value={watch('type') ?? ''} onValueChange={(v) => setValue('type', v)}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>{TYPES.map((t) => <SelectItem key={t} value={t} className="capitalize">{t}</SelectItem>)}</SelectContent>
                </Select>
                {errors.type && <p className="text-xs text-destructive">{errors.type.message}</p>}
              </div>
            </div>
            <div className="space-y-1.5"><Label>Nombre</Label><Input placeholder="Nombre de la variable" {...register('name')} />{errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}</div>
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
