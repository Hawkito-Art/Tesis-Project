'use client'

import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { statsApi, type ChartSeries } from '@/features/reports/api'
import { Skeleton } from '@/components/ui/skeleton'

// Placeholder data shown while API has no data yet; replaced as soon as
// the backend returns real chart_data entries.
const FALLBACK_BAR = [
  { name: 'Ene', value: 0 },
  { name: 'Feb', value: 0 },
  { name: 'Mar', value: 0 },
  { name: 'Abr', value: 0 },
  { name: 'May', value: 0 },
  { name: 'Jun', value: 0 },
]

const FALLBACK_LINE = [
  { name: 'T1', previo: 0, actual: 0 },
  { name: 'T2', previo: 0, actual: 0 },
  { name: 'T3', previo: 0, actual: 0 },
  { name: 'T4', previo: 0, actual: 0 },
]

// The backend is expected to return chart_data as an array of two ChartSeries:
// [{ key: 'bar', data: [...] }, { key: 'line', data: [...] }]
// If not present we fall back to zero-value placeholders.
function extractChartData(raw: ChartSeries[] | undefined) {
  if (!raw?.length) return { barData: FALLBACK_BAR, lineData: FALLBACK_LINE }
  const barEntry = raw.find((d) => d.key === 'bar')
  const lineEntry = raw.find((d) => d.key === 'line')
  return {
    barData: (barEntry?.data as typeof FALLBACK_BAR | undefined) ?? FALLBACK_BAR,
    lineData: (lineEntry?.data as typeof FALLBACK_LINE | undefined) ?? FALLBACK_LINE,
  }
}

// oklch chart tokens resolved to hex-compatible CSS custom properties
const CHART_1 = 'oklch(var(--chart-1))'
const CHART_2 = 'oklch(var(--chart-2))'

export function StatsClient() {
  const { data, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsApi.get(),
  })

  const summaryCards = data?.stats ?? [
    { label: 'Entidades activas', value: '—' },
    { label: 'Períodos registrados', value: '—' },
    { label: 'Indicadores calculados', value: '—' },
    { label: 'Importaciones este mes', value: '—' },
  ]

  const { barData, lineData } = extractChartData(data?.chart_data)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-base font-semibold">Estadísticas</h2>
        <p className="text-xs text-muted-foreground">Resumen general del sistema</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((stat, i) =>
          isLoading ? (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ) : (
            <div key={i} className="bg-card border border-border rounded-xl p-4">
              <p className="text-xs text-muted-foreground">{stat.label}</p>
              <p className="text-2xl font-bold text-foreground mt-1">{stat.value}</p>
            </div>
          ),
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-semibold mb-4">Importaciones por mes</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={barData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12 }} />
              <Bar dataKey="value" fill={CHART_1} radius={[3, 3, 0, 0]} name="Importaciones" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-semibold mb-4">Evolución de indicadores</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={lineData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line type="monotone" dataKey="previo" stroke={CHART_2} strokeWidth={2} dot={false} name="Período anterior" />
              <Line type="monotone" dataKey="actual" stroke={CHART_1} strokeWidth={2} dot={false} name="Período actual" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
