'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'

import { ingestionApi } from '@/features/ingestion/api'
import type { ImportJob, ImportJobDetail, ImportJobStatus } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const STATUS_CONFIG: Record<ImportJobStatus, { label: string; className: string }> = {
  pendiente: { label: 'Pendiente', className: 'bg-muted text-muted-foreground' },
  en_progreso: { label: 'Procesando', className: 'bg-amber-100 text-amber-700 border border-amber-300' },
  completado: { label: 'Completado', className: 'bg-emerald-100 text-emerald-700 border border-emerald-300' },
  error: { label: 'Error', className: 'bg-red-100 text-red-700 border border-red-300' },
}

interface JobDetailClientProps {
  jobId: string
}

export function JobDetailClient({ jobId }: JobDetailClientProps) {
  const [page, setPage] = useState(0)
  const [onlyErrors, setOnlyErrors] = useState(false)

  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: ['import-job', jobId],
    queryFn: () => ingestionApi.getJob(Number(jobId)),
  })

  const { data: details, isLoading: detailsLoading } = useQuery({
    queryKey: ['import-job-details', jobId, page, onlyErrors],
    queryFn: () =>
      ingestionApi.getJobDetails(Number(jobId), {
        page: page + 1,
        page_size: 10,
        ...(onlyErrors ? { is_valid: false } : {}),
      }),
  })

  const columns: ColumnDef<ImportJobDetail>[] = [
    { accessorKey: 'row_number', header: 'Fila', size: 60 },
    {
      id: 'indicator_name',
      header: 'Indicador',
      cell: ({ row }) => {
        const raw = row.original.raw_data as Record<string, unknown> | undefined
        return String(raw?.indicator_name ?? '—')
      },
    },
    {
      accessorKey: 'is_valid',
      header: 'Válido',
      size: 80,
      cell: ({ row }) =>
        row.original.is_valid ? (
          <Badge className="bg-emerald-100 text-emerald-700 border border-emerald-300">Válido</Badge>
        ) : (
          <Badge className="bg-red-100 text-red-700 border border-red-300">Error</Badge>
        ),
    },
    { accessorKey: 'error_message', header: 'Mensaje' },
  ]

  if (jobLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!job) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Trabajo no encontrado.</p>
        <Button variant="outline" size="sm" className="mt-4" asChild>
          <Link href="/dashboard/ingestion/jobs">Volver</Link>
        </Button>
      </div>
    )
  }

  const infoRows = [
    { label: 'Estado', value: <Badge className={cn('font-medium', STATUS_CONFIG[job.status].className)}>{STATUS_CONFIG[job.status].label}</Badge> },
    { label: 'Archivo', value: job.document_name },
    { label: 'Total filas', value: job.total_rows },
    { label: 'Procesadas', value: job.processed_rows },
    { label: 'Errores', value: job.error_rows },
    { label: 'Iniciado', value: job.started_at ? format(new Date(job.started_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—' },
    { label: 'Finalizado', value: job.finished_at ? format(new Date(job.finished_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" className="h-7 gap-1" asChild>
          <Link href="/dashboard/ingestion/jobs">
            <ArrowLeft className="w-3.5 h-3.5" />
            Volver
          </Link>
        </Button>
        <div>
          <h2 className="text-base font-semibold">Detalle de importación</h2>
          <p className="text-xs text-muted-foreground">Job #{job.id} — {job.document_name}</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Resumen</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            {infoRows.map((row) => (
              <div key={row.label}>
                <dt className="text-xs text-muted-foreground">{row.label}</dt>
                <dd className="font-medium mt-0.5">{row.value}</dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Detalles por fila</h3>
        <Button
          variant="outline"
          size="sm"
          className="h-7 text-xs"
          onClick={() => { setOnlyErrors(!onlyErrors); setPage(0) }}
        >
          {onlyErrors ? 'Mostrar todas' : 'Solo errores'}
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={details?.results ?? []}
        isLoading={detailsLoading}
        totalCount={details?.count}
        pageIndex={page}
        serverPagination
        onPaginationChange={(p) => setPage(p.pageIndex)}
        emptyMessage={onlyErrors ? 'No hay errores en este trabajo.' : 'No hay detalles disponibles.'}
      />
    </div>
  )
}
