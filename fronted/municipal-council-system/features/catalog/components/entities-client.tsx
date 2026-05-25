'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { entitiesApi } from '@/features/catalog/api'
import type { Entity } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { FormField } from '@/components/shared/form-field'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Loader2 } from 'lucide-react'

const ENTITY_TYPES = [
  { value: 'consolidado', label: 'Consolidado' },
  { value: 'empresa', label: 'Empresa' },
  { value: 'mipyme', label: 'Mipyme' },
  { value: 'unidad_presupuestada', label: 'Unidad presupuestada' },
]

const typeLabels: Record<string, string> = Object.fromEntries(
  ENTITY_TYPES.map((t) => [t.value, t.label]),
)

const entitySchema = z.object({
  code: z.string().min(1, 'El código es requerido'),
  name: z.string().min(1, 'El nombre es requerido'),
  type: z.string().min(1, 'El tipo es requerido'),
  description: z.string().optional(),
  is_consolidated: z.boolean().default(false),
  is_active: z.boolean().default(true),
})
type EntityValues = z.infer<typeof entitySchema>

export function EntitiesClient() {
  const qc = useQueryClient()
  const [page, setPage] = useState(0)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Entity | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Entity | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['entities', page],
    queryFn: () => entitiesApi.list({ page: page + 1 }),
  })

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<EntityValues>({
    resolver: zodResolver(entitySchema),
    defaultValues: { type: 'empresa', is_consolidated: false, is_active: true },
  })

  const watchedType = watch('type')

  const createMutation = useMutation({
    mutationFn: (values: EntityValues) => entitiesApi.create(values),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['entities'] })
      toast.success('Entidad creada correctamente')
      setDialogOpen(false)
      reset()
    },
    onError: () => toast.error('Error al crear la entidad'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: EntityValues }) =>
      entitiesApi.update(id, values),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['entities'] })
      toast.success('Entidad actualizada')
      setDialogOpen(false)
      setEditTarget(null)
      reset()
    },
    onError: () => toast.error('Error al actualizar la entidad'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => entitiesApi.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['entities'] })
      toast.success('Entidad eliminada')
      setDeleteTarget(null)
    },
    onError: () => toast.error('Error al eliminar la entidad'),
  })

  function openCreate() {
    setEditTarget(null)
    reset({ code: '', name: '', type: 'empresa', description: '', is_consolidated: false, is_active: true })
    setDialogOpen(true)
  }

  function openEdit(entity: Entity) {
    setEditTarget(entity)
    reset({
      code: entity.code,
      name: entity.name,
      type: entity.type,
      description: entity.description ?? '',
      is_consolidated: entity.is_consolidated,
      is_active: entity.is_active,
    })
    setDialogOpen(true)
  }

  async function onSubmit(values: EntityValues) {
    if (editTarget) {
      await updateMutation.mutateAsync({ id: editTarget.id, values })
    } else {
      await createMutation.mutateAsync(values)
    }
  }

  const columns: ColumnDef<Entity>[] = [
    { accessorKey: 'code', header: 'Código', size: 100 },
    { accessorKey: 'name', header: 'Nombre' },
    {
      accessorKey: 'type', header: 'Tipo',
      cell: ({ row }) => <Badge variant="outline">{typeLabels[row.original.type] ?? row.original.type}</Badge>,
    },
    { accessorKey: 'description', header: 'Descripción', cell: ({ row }) => row.original.description || '—' },
    {
      accessorKey: 'is_active', header: 'Estado',
      cell: ({ row }) => (
        <Badge variant={row.original.is_active ? 'default' : 'secondary'}>
          {row.original.is_active ? 'Activo' : 'Inactivo'}
        </Badge>
      ),
    },
    {
      id: 'actions',
      header: '',
      size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openEdit(row.original)}>
            <Pencil className="w-3.5 h-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0 text-destructive hover:text-destructive"
            onClick={() => setDeleteTarget(row.original)}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-foreground">Entidades</h2>
          <p className="text-xs text-muted-foreground">Municipios y entidades del sistema</p>
        </div>
        <Button size="sm" onClick={openCreate}>
          <Plus className="w-4 h-4 mr-1.5" />
          Nueva entidad
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={data?.results ?? []}
        isLoading={isLoading}
        totalCount={data?.count}
        pageIndex={page}
        serverPagination
        onPaginationChange={(p) => setPage(p.pageIndex)}
        emptyMessage="No hay entidades registradas."
      />

      <Dialog open={dialogOpen} onOpenChange={(v) => { setDialogOpen(v); if (!v) { setEditTarget(null); reset() } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editTarget ? 'Editar entidad' : 'Nueva entidad'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
            <FormField
              label="Código"
              id="code"
              placeholder="MUN-001"
              error={errors.code?.message}
              {...register('code')}
            />
            <FormField
              label="Nombre"
              id="name"
              placeholder="Municipio de..."
              error={errors.name?.message}
              {...register('name')}
            />
            <div className="space-y-1.5">
              <Label>Tipo de entidad</Label>
              <Select value={watch('type')} onValueChange={(v) => setValue('type', v)}>
                <SelectTrigger><SelectValue placeholder="Seleccionar tipo" /></SelectTrigger>
                <SelectContent>
                  {ENTITY_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                </SelectContent>
              </Select>
              {errors.type && <p className="text-xs text-destructive">{errors.type.message}</p>}
            </div>
            <FormField
              label="Descripción (opcional)"
              id="description"
              placeholder="Descripción breve"
              {...register('description')}
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                {...register('is_consolidated')}
                className="rounded border-border"
                disabled={watchedType !== 'consolidado'}
              />
              Entidad consolidada del municipio
            </label>
            {watchedType === 'consolidado' && !watch('is_consolidated') && (
              <p className="text-xs text-amber-600">Las entidades consolidadas deben marcarse como tal.</p>
            )}
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" {...register('is_active')} className="rounded border-border" />
              Entidad activa
            </label>
            <DialogFooter className="pt-2">
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                {editTarget ? 'Guardar cambios' : 'Crear entidad'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteTarget} onOpenChange={(v) => !v && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar entidad?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente la entidad{' '}
              <strong>{deleteTarget?.name}</strong>.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
            >
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
