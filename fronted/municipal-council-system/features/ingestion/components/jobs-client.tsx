'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

import { ingestionApi } from '@/features/ingestion/api'
import type { ImportJob, ImportJobStatus } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const STATUS_CONFIG: Record<ImportJobStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; className: string }> = {
  pending: { label: 'Pendiente', variant: 'secondary', className: '' },
  processing: { label: 'Procesando', variant: 'outline', className: 'border-amber-400 text-amber-600' },
  completed: { label: 'Completado', variant: 'default', className: 'bg-emerald-500 hover:bg-emerald-500' },
  error: { label: 'Error', variant: 'destructive', className: '' },
}

const IMPORT_TYPE_LABELS: Record<string, string> = {
  budget: 'Presupuesto',
  indicators: 'Indicadores',
  records: 'Registros',
}

export function JobsClient() {
  const qc = useQueryClient()
  const [page, setPage] = useState(0)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['import-jobs', page],
    queryFn: () => ingestionApi.listJobs({ page: page + 1 }),
    refetchInterval: 10000, // poll every 10 s
  })

  const retryMutation = useMutation({
    mutationFn: (id: number) => ingestionApi.retryJob(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['import-jobs'] }); toast.success('Trabajo reiniciado') },
    onError: () => toast.error('Error al reintentar el trabajo'),
  })

  const columns: ColumnDef<ImportJob>[] = [
    { accessorKey: 'id', header: 'ID', size: 60 },
    { accessorKey: 'filename', header: 'Archivo' },
    {
      accessorKey: 'import_type',
      header: 'Tipo',
      cell: ({ row }) => IMPORT_TYPE_LABELS[row.original.import_type] ?? row.original.import_type,
    },
    {
      accessorKey: 'status',
      header: 'Estado',
      cell: ({ row }) => {
        const cfg = STATUS_CONFIG[row.original.status] ?? STATUS_CONFIG.pending
        return (
          <Badge variant={cfg.variant} className={cn(cfg.className)}>
            {cfg.label}
          </Badge>
        )
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Fecha',
      cell: ({ row }) =>
        format(new Date(row.original.created_at), "dd/MM/yyyy HH:mm", { locale: es }),
    },
    {
      id: 'actions',
      header: '',
      size: 80,
      cell: ({ row }) =>
        row.original.status === 'error' ? (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1.5 text-xs"
            onClick={() => retryMutation.mutate(row.original.id)}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reintentar
          </Button>
        ) : null,
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
