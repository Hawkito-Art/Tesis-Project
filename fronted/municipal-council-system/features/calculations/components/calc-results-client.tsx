'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { Download, ExternalLink } from 'lucide-react'
import Link from 'next/link'

import { calculationsApi } from '@/features/calculations/api'
import { periodsApi } from '@/features/catalog/api'
import type { Calculation, CalcStatus, Period } from '@/lib/types'
import { Label } from '@/components/ui/label'
import { DataTable } from '@/components/shared/data-table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

const STATUS_CONFIG: Record<CalcStatus, { label: string; className: string }> = {
  pendiente: { label: 'Pendiente', className: 'bg-muted text-muted-foreground' },
  en_progreso: { label: 'Procesando', className: 'bg-amber-100 text-amber-700 border border-amber-300' },
  completado: { label: 'Completado', className: 'bg-emerald-100 text-emerald-700 border border-emerald-300' },
  error: { label: 'Error', className: 'bg-red-100 text-red-700 border border-red-300' },
}

export function CalcResultsClient() {
  const [page, setPage] = useState(0)
  const [periodFilter, setPeriodFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  const { data, isLoading } = useQuery({
    queryKey: ['calculations', page, periodFilter, statusFilter],
    queryFn: () =>
      calculationsApi.list({
        page: page + 1,
        period: periodFilter === 'all' ? undefined : periodFilter,
        status: statusFilter === 'all' ? undefined : statusFilter,
      }),
  })

  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  async function handleExport() {
    try {
      await calculationsApi.exportXlsx()
      toast.success('Exportación completada')
    } catch {
      toast.error('Error al exportar')
    }
  }

  const columns: ColumnDef<Calculation>[] = [
    { accessorKey: 'id', header: 'ID', size: 50 },
    { accessorKey: 'name', header: 'Nombre' },
    { accessorKey: 'period_display', header: 'Período' },
    {
      accessorKey: 'status',
      header: 'Estado',
      cell: ({ row }) => {
        const cfg = STATUS_CONFIG[row.original.status] ?? STATUS_CONFIG.pendiente
        return <Badge className={cn('font-medium', cfg.className)}>{cfg.label}</Badge>
      },
    },
    { accessorKey: 'executed_by_email', header: 'Ejecutado por' },
    {
      accessorKey: 'started_at',
      header: 'Iniciado',
      cell: ({ row }) => row.original.started_at ? format(new Date(row.original.started_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—',
    },
    {
      accessorKey: 'finished_at',
      header: 'Finalizado',
      cell: ({ row }) => row.original.finished_at ? format(new Date(row.original.finished_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—',
    },
    {
      accessorKey: 'created_at',
      header: 'Creado',
      cell: ({ row }) => format(new Date(row.original.created_at), "dd/MM/yyyy HH:mm", { locale: es }),
    },
    {
      id: 'actions',
      header: '',
      size: 80,
      cell: ({ row }) => (
        <div className="flex items-center gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" asChild>
            <Link href={`/dashboard/calculations/${row.original.id}`}><ExternalLink className="w-3.5 h-3.5" /></Link>
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Cálculos ejecutados</h2>
          <p className="text-xs text-muted-foreground">Historial de ejecuciones del motor de cálculo</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap">
            <Select value={periodFilter} onValueChange={setPeriodFilter}>
              <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Filtrar período" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                {periods?.results.map((p: Period) => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Filtrar estado" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="pendiente">Pendiente</SelectItem>
                <SelectItem value="en_progreso">Procesando</SelectItem>
                <SelectItem value="completado">Completado</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={handleExport}>
            <Download className="w-3.5 h-3.5 mr-1.5" />
            Exportar XLSX
          </Button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data?.results ?? []}
        isLoading={isLoading}
        totalCount={data?.count}
        pageIndex={page}
        serverPagination
        onPaginationChange={(p) => setPage(p.pageIndex)}
        emptyMessage="No hay cálculos ejecutados."
      />
    </div>
  )
}
