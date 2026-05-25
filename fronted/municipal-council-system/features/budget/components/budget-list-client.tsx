'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { useRouter } from 'next/navigation'
import { Eye } from 'lucide-react'

import { budgetsApi } from '@/features/budget/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { Budget } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Borrador',
  approved: 'Aprobado',
  closed: 'Cerrado',
}

const STATUS_VARIANTS: Record<string, 'default' | 'secondary' | 'outline'> = {
  draft: 'secondary',
  approved: 'default',
  closed: 'outline',
}

export function BudgetListClient() {
  const router = useRouter()
  const [page, setPage] = useState(0)
  const [entityFilter, setEntityFilter] = useState<string>('all')
  const [periodFilter, setPeriodFilter] = useState<string>('all')

  const { data, isLoading } = useQuery({
    queryKey: ['budgets', page, entityFilter, periodFilter],
    queryFn: () =>
      budgetsApi.list({
        page: page + 1,
        entity: entityFilter === 'all' ? undefined : entityFilter,
        period: periodFilter === 'all' ? undefined : periodFilter,
      }),
  })

  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const columns: ColumnDef<Budget>[] = [
    { accessorKey: 'entity', header: 'Entidad', cell: ({ row }) => row.original.entity.name },
    { accessorKey: 'period', header: 'Período', cell: ({ row }) => row.original.period.name },
    {
      accessorKey: 'total_amount',
      header: 'Monto total',
      cell: ({ row }) =>
        new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(row.original.total_amount),
    },
    {
      accessorKey: 'status',
      header: 'Estado',
      cell: ({ row }) => (
        <Badge variant={STATUS_VARIANTS[row.original.status] ?? 'secondary'}>
          {STATUS_LABELS[row.original.status] ?? row.original.status}
        </Badge>
      ),
    },
    {
      id: 'actions',
      header: '',
      size: 60,
      cell: ({ row }) => (
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 p-0"
          onClick={() => router.push(`/dashboard/budget/${row.original.id}`)}
        >
          <Eye className="w-3.5 h-3.5" />
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Presupuestos</h2>
          <p className="text-xs text-muted-foreground">Lista de presupuestos por entidad y período</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={entityFilter} onValueChange={setEntityFilter}>
            <SelectTrigger className="h-8 w-44 text-xs">
              <SelectValue placeholder="Filtrar por entidad" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las entidades</SelectItem>
              {entities?.results.map((e) => (
                <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-40 text-xs">
              <SelectValue placeholder="Filtrar por período" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los períodos</SelectItem>
              {periods?.results.map((p) => (
                <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
              ))}
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
        emptyMessage="No hay presupuestos registrados."
      />
    </div>
  )
}
