'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { ArrowLeft, Download, Loader2 } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Link from 'next/link'
import { toast } from 'sonner'

import { calculationsApi } from '@/features/calculations/api'
import { entitiesApi } from '@/features/catalog/api'
import { indicatorsApi } from '@/features/indicators/api'
import type { Calculation, CalcStatus, CalculationResult, Entity, Indicator } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { cn } from '@/lib/utils'

const STATUS_CONFIG: Record<CalcStatus, { label: string; className: string }> = {
  pendiente: { label: 'Pendiente', className: 'bg-muted text-muted-foreground' },
  en_progreso: { label: 'Procesando', className: 'bg-amber-100 text-amber-700 border border-amber-300' },
  completado: { label: 'Completado', className: 'bg-emerald-100 text-emerald-700 border border-emerald-300' },
  error: { label: 'Error', className: 'bg-red-100 text-red-700 border border-red-300' },
}

interface Props {
  calculationId: string
}

const STANDARD_VARIABLES = [
  { value: 'plan_anual', label: 'Plan Anual' },
  { value: 'ano_anterior', label: 'Año Anterior' },
  { value: 'plan_acumulado', label: 'Plan Acumulado' },
  { value: 'real_acumulado', label: 'Real Acumulado' },
  { value: 'porcentaje_r_p', label: '% R/P' },
  { value: 'real_aa', label: 'Real AA' },
  { value: 'estimado_prox_mes', label: 'Est. Próximo Mes' },
  { value: 'estimado_cierre_ano', label: 'Est. Cierre Año' },
]

export function CalculationDetailClient({ calculationId }: Props) {
  const [page, setPage] = useState(0)
  const [entityFilter, setEntityFilter] = useState('all')
  const [indicatorFilter, setIndicatorFilter] = useState('all')
  const [variableFilter, setVariableFilter] = useState('all')

  const { data: calc, isLoading: calcLoading } = useQuery({
    queryKey: ['calculation', calculationId],
    queryFn: () => calculationsApi.get(Number(calculationId)),
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'en_progreso' || data?.status === 'pendiente') return 5000
      return false
    },
  })

  const { data: results, isLoading: resultsLoading } = useQuery({
    queryKey: ['calculation-results', calculationId, page, entityFilter, indicatorFilter, variableFilter],
    queryFn: () =>
      calculationsApi.getResults(Number(calculationId), {
        page: page + 1,
        page_size: 10,
        entity: entityFilter === 'all' ? undefined : entityFilter,
        indicator: indicatorFilter === 'all' ? undefined : indicatorFilter,
        variable_name: variableFilter === 'all' ? undefined : variableFilter,
      }),
  })

  const { data: entities } = useQuery({ queryKey: ['entities'], queryFn: () => entitiesApi.list() })
  const { data: indicators } = useQuery({ queryKey: ['indicators', 0], queryFn: () => indicatorsApi.list() })

  async function handleExport() {
    try {
      await calculationsApi.exportXlsx()
      toast.success('Exportación completada')
    } catch {
      toast.error('Error al exportar')
    }
  }

  const columns: ColumnDef<CalculationResult>[] = [
    { accessorKey: 'entity_code', header: 'Entidad' },
    { accessorKey: 'indicator_code', header: 'Indicador' },
    { accessorKey: 'variable_name', header: 'Variable', cell: ({ row }) => <code className="text-xs font-mono">{row.original.variable_name}</code> },
    {
      accessorKey: 'value',
      header: 'Valor',
      cell: ({ row }) => <span className="font-mono tabular-nums">{row.original.value ?? '—'}</span>,
    },
  ]

  if (calcLoading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
  }

  if (!calc) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Cálculo no encontrado.</p>
        <Button variant="outline" size="sm" className="mt-4" asChild>
          <Link href="/dashboard/calculations/results">Volver</Link>
        </Button>
      </div>
    )
  }

  const infoRows = [
    { label: 'Estado', value: <Badge className={cn('font-medium', STATUS_CONFIG[calc.status].className)}>{STATUS_CONFIG[calc.status].label}</Badge> },
    { label: 'Nombre', value: calc.name },
    { label: 'Período', value: calc.period_display },
    { label: 'Ejecutado por', value: calc.executed_by_email || '—' },
    { label: 'Iniciado', value: calc.started_at ? format(new Date(calc.started_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—' },
    { label: 'Finalizado', value: calc.finished_at ? format(new Date(calc.finished_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" className="h-7 gap-1" asChild>
          <Link href="/dashboard/calculations/results"><ArrowLeft className="w-3.5 h-3.5" />Volver</Link>
        </Button>
        <div>
          <h2 className="text-base font-semibold">Detalle de cálculo</h2>
          <p className="text-xs text-muted-foreground">#{calc.id} — {calc.name}</p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm">Resumen</CardTitle>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={handleExport}>
            <Download className="w-3.5 h-3.5 mr-1" />
            Exportar XLSX
          </Button>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
            {infoRows.map((row) => (
              <div key={row.label}>
                <dt className="text-xs text-muted-foreground">{row.label}</dt>
                <dd className="font-medium mt-0.5">{row.value}</dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>

      <div>
        <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
          <h3 className="text-sm font-semibold">Resultados</h3>
          <div className="flex items-center gap-2 flex-wrap">
            <Select value={entityFilter} onValueChange={setEntityFilter}>
              <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Entidad" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                {entities?.results.map((e: Entity) => <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={indicatorFilter} onValueChange={setIndicatorFilter}>
              <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Indicador" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                {indicators?.results.map((i: Indicator) => <SelectItem key={i.id} value={String(i.id)}>{i.indicator}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={variableFilter} onValueChange={setVariableFilter}>
              <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Variable" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                {STANDARD_VARIABLES.map((v) => <SelectItem key={v.value} value={v.value}>{v.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DataTable
          columns={columns}
          data={results?.results ?? []}
          isLoading={resultsLoading}
          totalCount={results?.count}
          pageIndex={page}
          serverPagination
          onPaginationChange={(p) => setPage(p.pageIndex)}
          emptyMessage="No hay resultados para este cálculo."
        />
      </div>
    </div>
  )
}
