'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

import { recordsApi, indicatorsApi, indicatorGroupsApi } from '@/features/indicators/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { IndicatorRecord, Indicator, Entity, Period, IndicatorGroup } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const SOURCE_BADGE: Record<string, { label: string; className: string }> = {
  manual: { label: 'Manual', className: 'bg-blue-100 text-blue-700 border border-blue-300' },
  imported: { label: 'Importado', className: 'bg-emerald-100 text-emerald-700 border border-emerald-300' },
  calculated: { label: 'Calculado', className: 'bg-amber-100 text-amber-700 border border-amber-300' },
}

export function RecordsClient() {
  const [page, setPage] = useState(0)
  const [indicatorFilter, setIndicatorFilter] = useState('all')
  const [entityFilter, setEntityFilter] = useState('all')
  const [periodFilter, setPeriodFilter] = useState('all')
  const [variableFilter, setVariableFilter] = useState('all')
  const [groupFilter, setGroupFilter] = useState('all')

  const { data, isLoading } = useQuery({
    queryKey: ['indicator-records', page, indicatorFilter, entityFilter, periodFilter, variableFilter, groupFilter],
    queryFn: () =>
      recordsApi.list({
        page: page + 1,
        indicator: indicatorFilter === 'all' ? undefined : indicatorFilter,
        entity: entityFilter === 'all' ? undefined : entityFilter,
        period: periodFilter === 'all' ? undefined : periodFilter,
        variable_name: variableFilter === 'all' ? undefined : variableFilter,
        group: groupFilter === 'all' ? undefined : groupFilter,
      }),
  })

  const { data: indicators } = useQuery({ queryKey: ['indicators', 0], queryFn: () => indicatorsApi.list() })
  const { data: entities } = useQuery({ queryKey: ['entities'], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })
  const { data: groups } = useQuery({ queryKey: ['indicator-groups'], queryFn: () => indicatorGroupsApi.list() })

  const columns: ColumnDef<IndicatorRecord>[] = [
    { accessorKey: 'indicator_code', header: 'Indicador' },
    { accessorKey: 'entity_code', header: 'Entidad' },
    { accessorKey: 'period_display', header: 'Período' },
    { accessorKey: 'variable_name', header: 'Variable', cell: ({ row }) => <code className="text-xs font-mono">{row.original.variable_name}</code> },
    {
      accessorKey: 'value',
      header: 'Valor',
      cell: ({ row }) => <span className="font-mono tabular-nums">{row.original.value ?? '—'}</span>,
    },
    {
      accessorKey: 'source_display',
      header: 'Origen',
      cell: ({ row }) => {
        const cfg = SOURCE_BADGE[row.original.source] ?? SOURCE_BADGE.manual
        return <Badge className={cn('font-medium', cfg.className)}>{cfg.label}</Badge>
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Registrado',
      cell: ({ row }) => format(new Date(row.original.created_at), "dd/MM/yyyy HH:mm", { locale: es }),
    },
  ]

  const variableOptions = indicators?.results
    .flatMap((i: Indicator) => i.variables)
    .filter((v, i, a) => a.findIndex((x) => x.name === v.name) === i)

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
              <SelectItem value="all">Todos</SelectItem>
              {indicators?.results.map((i: Indicator) => <SelectItem key={i.id} value={String(i.id)}>{i.indicator}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={entityFilter} onValueChange={setEntityFilter}>
            <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Entidad" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {entities?.results.map((e: Entity) => <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Período" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {periods?.results.map((p: Period) => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={variableFilter} onValueChange={setVariableFilter}>
            <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Variable" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {variableOptions?.map((v) => <SelectItem key={v.name} value={v.name}>{v.label}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={groupFilter} onValueChange={setGroupFilter}>
            <SelectTrigger className="h-8 w-44 text-xs"><SelectValue placeholder="Grupo" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {groups?.results.map((g: IndicatorGroup) => <SelectItem key={g.id} value={String(g.id)}>{g.name}</SelectItem>)}
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
