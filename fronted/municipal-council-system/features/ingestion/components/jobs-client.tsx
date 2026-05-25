'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { RefreshCw, Play, RotateCcw, ExternalLink } from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'

import { ingestionApi } from '@/features/ingestion/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { ImportJob, ImportJobStatus, Entity, Period } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
  DialogFooter, DialogTrigger,
} from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

const STATUS_CONFIG: Record<ImportJobStatus, { label: string; className: string }> = {
  pendiente: { label: 'Pendiente', className: 'bg-muted text-muted-foreground' },
  en_progreso: { label: 'Procesando', className: 'bg-amber-100 text-amber-700 border border-amber-300' },
  completado: { label: 'Completado', className: 'bg-emerald-100 text-emerald-700 border border-emerald-300' },
  error: { label: 'Error', className: 'bg-red-100 text-red-700 border border-red-300' },
}

export function JobsClient() {
  const qc = useQueryClient()
  const [page, setPage] = useState(0)
  const [processJobId, setProcessJobId] = useState<number | null>(null)
  const [entityId, setEntityId] = useState('')
  const [periodId, setPeriodId] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['import-jobs', page],
    queryFn: () => ingestionApi.listJobs({ page: page + 1 }),
    refetchInterval: 10000,
  })

  const { data: entities } = useQuery({
    queryKey: ['entities'],
    queryFn: () => entitiesApi.list(),
  })

  const { data: periods } = useQuery({
    queryKey: ['periods'],
    queryFn: () => periodsApi.list(),
  })

  const retryMutation = useMutation({
    mutationFn: (id: number) => ingestionApi.retryJob(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['import-jobs'] })
      toast.success('Trabajo reiniciado correctamente')
    },
    onError: () => toast.error('Error al reintentar el trabajo'),
  })

  const processMutation = useMutation({
    mutationFn: ({ id, entity, period }: { id: number; entity: number; period: number }) =>
      ingestionApi.processJob(id, entity, period),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['import-jobs'] })
      setProcessJobId(null)
      setEntityId('')
      setPeriodId('')
      toast.success('Trabajo procesado correctamente')
    },
    onError: () => toast.error('Error al procesar el trabajo'),
  })

  function handleProcess() {
    if (!processJobId || !entityId || !periodId) {
      toast.error('Seleccione entidad y período')
      return
    }
    processMutation.mutate({
      id: processJobId,
      entity: Number(entityId),
      period: Number(periodId),
    })
  }

  const columns: ColumnDef<ImportJob>[] = [
    { accessorKey: 'id', header: 'ID', size: 60 },
    { accessorKey: 'document_name', header: 'Archivo', id: 'document_name' },
    {
      accessorKey: 'status',
      header: 'Estado',
      cell: ({ row }) => {
        const cfg = STATUS_CONFIG[row.original.status] ?? STATUS_CONFIG.pendiente
        return <Badge className={cn('font-medium', cfg.className)}>{cfg.label}</Badge>
      },
    },
    { accessorKey: 'total_rows', header: 'Filas', size: 60 },
    { accessorKey: 'processed_rows', header: 'Procesadas', size: 80 },
    { accessorKey: 'error_rows', header: 'Errores', size: 60 },
    {
      accessorKey: 'created_at',
      header: 'Fecha',
      cell: ({ row }) =>
        format(new Date(row.original.created_at), "dd/MM/yyyy HH:mm", { locale: es }),
    },
    {
      id: 'actions',
      header: '',
      size: 120,
      cell: ({ row }) => {
        const job = row.original
        if (job.status === 'pendiente') {
          return (
            <Dialog open={processJobId === job.id} onOpenChange={(open) => {
              setProcessJobId(open ? job.id : null)
              if (!open) { setEntityId(''); setPeriodId('') }
            }}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm" className="h-7 gap-1.5 text-xs">
                  <Play className="w-3.5 h-3.5" />
                  Procesar
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Procesar importación</DialogTitle>
                  <DialogDescription>
                    Seleccione la entidad y el período para procesar los datos.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-2">
                  <div className="space-y-1.5">
                    <Label>Entidad</Label>
                    <Select value={entityId} onValueChange={setEntityId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar entidad" />
                      </SelectTrigger>
                      <SelectContent>
                        {entities?.results.map((e: Entity) => (
                          <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1.5">
                    <Label>Período</Label>
                    <Select value={periodId} onValueChange={setPeriodId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar período" />
                      </SelectTrigger>
                      <SelectContent>
                        {periods?.results.map((p: Period) => (
                          <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => { setProcessJobId(null); setEntityId(''); setPeriodId('') }}>
                    Cancelar
                  </Button>
                  <Button onClick={handleProcess} disabled={processMutation.isPending}>
                    Procesar
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )
        }
        if (job.status === 'en_progreso' || job.status === 'completado') {
          return (
            <Button variant="ghost" size="sm" className="h-7 gap-1.5 text-xs" asChild>
              <Link href={`/dashboard/ingestion/jobs/${job.id}`}>
                <ExternalLink className="w-3.5 h-3.5" />
                Ver detalles
              </Link>
            </Button>
          )
        }
        if (job.status === 'error') {
          return (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1.5 text-xs"
              onClick={() => retryMutation.mutate(job.id)}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reintentar
            </Button>
          )
        }
        return null
      },
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold">Trabajos de importación</h2>
          <p className="text-xs text-muted-foreground">Historial de importaciones masivas</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Actualizar
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
        emptyMessage="No hay trabajos de importación."
      />
    </div>
  )
}
