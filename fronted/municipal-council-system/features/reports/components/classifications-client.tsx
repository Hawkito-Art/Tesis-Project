'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'

import { classificationsApi } from '@/features/reports/api'
import { periodsApi } from '@/features/catalog/api'
import type { Classification } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { ExportButton } from '@/components/shared/export-button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

function RankBadge({ rank }: { rank: number }) {
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold',
        rank === 1 && 'bg-amber-400/20 text-amber-700',
        rank === 2 && 'bg-slate-200 text-slate-600',
        rank === 3 && 'bg-orange-200/60 text-orange-700',
        rank > 3 && 'bg-muted text-muted-foreground',
      )}
    >
      {rank}
    </span>
  )
}

export function ClassificationsClient() {
  const [page, setPage] = useState(0)
  const [periodFilter, setPeriodFilter] = useState('all')

  const { data, isLoading } = useQuery({
    queryKey: ['classifications', page, periodFilter],
    queryFn: () => classificationsApi.list({ page: page + 1, period: periodFilter === 'all' ? undefined : periodFilter }),
  })

  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const columns: ColumnDef<Classification>[] = [
    { accessorKey: 'rank', header: 'Posición', size: 80, cell: ({ row }) => <RankBadge rank={row.original.rank} /> },
    { accessorKey: 'entity', header: 'Entidad', cell: ({ row }) => row.original.entity?.name ?? '—' },
    { accessorKey: 'period', header: 'Período', cell: ({ row }) => row.original.period?.name ?? '—' },
    { accessorKey: 'category', header: 'Categoría', cell: ({ row }) => <Badge variant="outline">{row.original.category}</Badge> },
    { accessorKey: 'score', header: 'Puntaje', cell: ({ row }) => <span className="font-mono font-semibold">{row.original.score.toFixed(2)}</span> },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Clasificaciones</h2>
          <p className="text-xs text-muted-foreground">Ranking de entidades por período</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Filtrar período" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {periods?.results.map((p) => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
            </SelectContent>
          </Select>
          <ExportButton endpoint="/reports/classifications/export/" filename="clasificaciones.xlsx" params={{ period: periodFilter === 'all' ? undefined : periodFilter }} />
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
        emptyMessage="No hay clasificaciones disponibles."
      />
    </div>
  )
}
