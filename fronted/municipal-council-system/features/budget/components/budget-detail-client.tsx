'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { budgetsApi, budgetItemsApi } from '@/features/budget/api'
import type { BudgetItem } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

const fmt = (n: number | string) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(n))

const STATUS_LABELS: Record<string, string> = { draft: 'Borrador', approved: 'Aprobado', closed: 'Cerrado' }
const STATUS_VARIANTS: Record<string, 'default' | 'secondary' | 'outline'> = { draft: 'secondary', approved: 'default', closed: 'outline' }

export function BudgetDetailClient({ budgetId }: { budgetId: number }) {
  const router = useRouter()
  const queryClient = useQueryClient()

  const { data: budget, isLoading: loadingBudget } = useQuery({
    queryKey: ['budget', budgetId],
    queryFn: () => budgetsApi.get(budgetId),
  })

  const statusMutation = useMutation({
    mutationFn: (status: string) => budgetsApi.update(budgetId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budget', budgetId] })
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
    },
  })

  const { data: items, isLoading: loadingItems } = useQuery({
    queryKey: ['budget-items', budgetId],
    queryFn: () => budgetItemsApi.list(budgetId),
    enabled: !!budgetId,
  })

  const columns: ColumnDef<BudgetItem>[] = [
    { accessorKey: 'code', header: 'Código', size: 100 },
    { accessorKey: 'name', header: 'Nombre' },
    { accessorKey: 'item_type', header: 'Tipo', size: 90, cell: ({ row }) => row.original.item_type === 'ingreso' ? 'Ingreso' : 'Gasto' },
    { accessorKey: 'planned_amount', header: 'Monto planificado', cell: ({ row }) => fmt(row.original.planned_amount) },
    { accessorKey: 'actual_amount', header: 'Monto real', cell: ({ row }) => fmt(row.original.actual_amount) },
    {
      id: 'percentage',
      header: 'Ejecución',
      cell: ({ row }) => {
        const planned = Number(row.original.planned_amount)
        const actual = Number(row.original.actual_amount)
        const pct = planned > 0
          ? ((actual / planned) * 100).toFixed(1)
          : '0.0'
        const numPct = parseFloat(pct)
        return (
          <div className="flex items-center gap-2 min-w-[80px]">
            <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all"
                style={{ width: `${Math.min(numPct, 100)}%` }}
              />
            </div>
            <span className="text-xs text-muted-foreground w-10 text-right">{pct}%</span>
          </div>
        )
      },
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h2 className="text-base font-semibold">Detalle de presupuesto</h2>
          <p className="text-xs text-muted-foreground">Partidas presupuestarias</p>
        </div>
      </div>

      {/* Summary card */}
      <div className="bg-card border border-border rounded-xl p-5">
        {loadingBudget ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-14" />
            ))}
          </div>
        ) : budget ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Entidad</p>
              <p className="text-sm font-semibold mt-0.5">{budget.entity_code}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Período</p>
              <p className="text-sm font-semibold mt-0.5">{budget.period_display}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Monto total</p>
              <p className="text-sm font-semibold mt-0.5">{fmt(budget.total_amount)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Estado</p>
              <div className="flex items-center gap-2 mt-0.5">
                <Badge variant={STATUS_VARIANTS[budget.status] ?? 'secondary'}>
                  {STATUS_LABELS[budget.status] ?? budget.status}
                </Badge>
                {budget.status === 'draft' && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-6 text-xs"
                    disabled={statusMutation.isPending}
                    onClick={() => statusMutation.mutate('approved')}
                  >
                    Aprobar
                  </Button>
                )}
                {budget.status === 'approved' && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-6 text-xs"
                    disabled={statusMutation.isPending}
                    onClick={() => statusMutation.mutate('closed')}
                  >
                    Cerrar
                  </Button>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Items table */}
      <div>
        <h3 className="text-sm font-semibold mb-3">Partidas presupuestarias</h3>
        <DataTable
          columns={columns}
          data={items?.results ?? []}
          isLoading={loadingItems}
          emptyMessage="No hay partidas para este presupuesto."
        />
        {items && items.results.length > 0 && (
          <div className="flex justify-end gap-6 mt-3 pt-3 border-t border-border text-sm">
            <div>
              <span className="text-muted-foreground">Total planificado: </span>
              <span className="font-semibold">{fmt(items.results.reduce((s, i) => s + Number(i.planned_amount), 0))}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Total real: </span>
              <span className="font-semibold">{fmt(items.results.reduce((s, i) => s + Number(i.actual_amount), 0))}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
