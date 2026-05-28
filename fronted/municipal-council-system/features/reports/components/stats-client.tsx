'use client'

import { useQuery } from '@tanstack/react-query'

import { statsApi } from '@/features/reports/api'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { SourcesDonutChart } from '@/features/reports/components/sources-donut-chart'
import { AveragesBarChart } from '@/features/reports/components/averages-bar-chart'

export function StatsClient() {
  const { data, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsApi.get(),
  })

  const totals = data?.totals

  const summaryCards = totals
    ? [
        { label: 'Registros de indicadores', value: totals.indicator_records },
        { label: 'Resultados de cálculo', value: totals.calculation_results },
        { label: 'Indicadores distintos', value: totals.distinct_indicators },
        { label: 'Entidades distintas', value: totals.distinct_entities },
      ]
    : [
        { label: 'Registros de indicadores', value: '—' },
        { label: 'Resultados de cálculo', value: '—' },
        { label: 'Indicadores distintos', value: '—' },
        { label: 'Entidades distintas', value: '—' },
      ]

  const recordsBySource = data?.records_by_source
  const averages = data?.average_value_by_indicator

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-base font-semibold">Estadísticas</h2>
        <p className="text-xs text-muted-foreground">Resumen general del sistema</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((stat, i) =>
          isLoading ? (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ) : (
            <Card key={i}>
              <CardHeader className="p-4 pb-1"><CardTitle className="text-xs text-muted-foreground font-normal">{stat.label}</CardTitle></CardHeader>
              <CardContent className="p-4 pt-0"><p className="text-2xl font-bold">{String(stat.value)}</p></CardContent>
            </Card>
          ),
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {isLoading ? (
          <>
            <Skeleton className="h-64 rounded-xl" />
            <Skeleton className="h-64 rounded-xl" />
          </>
        ) : (
          <>
            <Card>
              <CardHeader><CardTitle className="text-sm">Registros por fuente</CardTitle></CardHeader>
              <CardContent>
                {recordsBySource ? (
                  <SourcesDonutChart data={recordsBySource} />
                ) : (
                  <p className="text-sm text-muted-foreground">Sin datos.</p>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">Promedio por indicador (top 10)</CardTitle></CardHeader>
              <CardContent>
                {averages ? (
                  <AveragesBarChart data={averages} />
                ) : (
                  <p className="text-sm text-muted-foreground">Sin datos.</p>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
}
