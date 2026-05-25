'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'

import { recordsApi, indicatorsApi } from '@/features/indicators/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { IndicatorRecord } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function RecordsClient() {
  const [page, setPage] = useState(0)
  const [indicatorFilter, setIndicatorFilter] = useState('')
  const [entityFilter, setEntityFilter] = useState('')
  const [periodFilter, setPeriodFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['indicator-records', page, indicatorFilter, entityFilter, periodFilter],
    queryFn: () =>
      recordsApi.list({
        page: page + 1,
        indicator: indicatorFilter || undefined,
        entity: entityFilter || undefined,
        period: periodFilter || undefined,
      }),
  })

  const { data: indicators } = useQuery({ queryKey: ['indicators', 0], queryFn: () => indicatorsApi.list() })
  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const columns: ColumnDef<IndicatorRecord>[] = [
    { accessorKey: 'indicator', header: 'Indicador', cell: ({ row }) => row.original.indicator?.name ?? '—' },
    { accessorKey: 'entity', header: 'Entidad', cell: ({ row }) => row.original.entity?.name ?? '—' },
    { accessorKey: 'period', header: 'Período', cell: ({ row }) => row.original.period?.name ?? '—' },
    { accessorKey: 'value', header: 'Valor', cell: ({ row }) => <span className="font-mono">{row.original.value}</span> },
    {
      accessorKey: 'recorded_at', header: 'Fecha de registro',
      cell: ({ row }) => format(new Date(row.original.recorded_at), 'dd/MM/yyyy'),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Registros de indicadores</h2>
          <p className="text-xs text-muted-foreground">Valores registrados por indicador, entidad y período</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={indicatorFilter} onValueChange={setIndicatorFilter}>
            <SelectTrigger className="h-8 w-44 text-xs"><SelectValue placeholder="Indicador" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todos</SelectItem>
              {indicators?.results.map((i) => <SelectItem key={i.id} value={String(i.id)}>{i.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={entityFilter} onValueChange={setEntityFilter}>
            <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Entidad" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todas</SelectItem>
              {entities?.results.map((e) => <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Período" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="">Todos</SelectItem>
              {periods?.results.map((p) => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
            </SelectContent>
          </Select>
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
        emptyMessage="No hay registros de indicadores."
      />
    </div>
  )
}
