'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'

import { calculationsApi } from '@/features/calculations/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { CalcResult } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { ExportButton } from '@/components/shared/export-button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'

const TYPE_LABELS: Record<string, string> = { full: 'Completo', partial: 'Parcial', projection: 'Proyección' }

export function CalcResultsClient() {
  const [page, setPage] = useState(0)
  const [entityFilter, setEntityFilter] = useState('all')
  const [periodFilter, setPeriodFilter] = useState('all')

  const { data, isLoading } = useQuery({
    queryKey: ['calc-results', page, entityFilter, periodFilter],
    queryFn: () =>
      calculationsApi.list({ page: page + 1, entity: entityFilter === 'all' ? undefined : entityFilter, period: periodFilter === 'all' ? undefined : periodFilter }),
  })

  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const columns: ColumnDef<CalcResult>[] = [
    { accessorKey: 'entity', header: 'Entidad', cell: ({ row }) => row.original.entity?.name ?? '—' },
    { accessorKey: 'period', header: 'Período', cell: ({ row }) => row.original.period?.name ?? '—' },
    { accessorKey: 'calc_type', header: 'Tipo', cell: ({ row }) => <Badge variant="secondary">{TYPE_LABELS[row.original.calc_type] ?? row.original.calc_type}</Badge> },
    { accessorKey: 'created_at', header: 'Fecha', cell: ({ row }) => format(new Date(row.original.created_at), 'dd/MM/yyyy HH:mm') },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Resultados de cálculos</h2>
          <p className="text-xs text-muted-foreground">Historial de resultados generados</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={entityFilter} onValueChange={setEntityFilter}>
            <SelectTrigger className="h-8 w-44 text-xs"><SelectValue placeholder="Filtrar entidad" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {entities?.results.map((e) => <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Filtrar período" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {periods?.results.map((p) => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <ExportButton
            endpoint="/calculations/export/"
            filename="resultados.xlsx"
            params={{ entity: entityFilter === 'all' ? undefined : entityFilter, period: periodFilter === 'all' ? undefined : periodFilter }}
          />
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
        emptyMessage="No hay resultados de cálculos."
      />
    </div>
  )
}
