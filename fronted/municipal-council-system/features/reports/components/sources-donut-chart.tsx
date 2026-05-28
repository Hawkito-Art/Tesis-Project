'use client'

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'

const SOURCE_COLORS: Record<string, string> = {
  imported: 'var(--color-chart-1)',
  calculated: 'var(--color-chart-3)',
  manual: 'var(--color-chart-5)',
}

const SOURCE_LABELS: Record<string, string> = {
  imported: 'Importado',
  calculated: 'Calculado',
  manual: 'Manual',
}

const FALLBACK_PALETTE = [
  'var(--color-chart-1)',
  'var(--color-chart-2)',
  'var(--color-chart-3)',
  'var(--color-chart-4)',
  'var(--color-chart-5)',
]

export function SourcesDonutChart({
  data,
}: {
  data: Record<string, number>
}) {
  const keys = Object.keys(data)

  if (keys.length === 0) {
    return <p className="text-sm text-muted-foreground">Sin datos.</p>
  }

  const total = Object.values(data).reduce((a, b) => a + b, 0)
  const chartData = keys.map((key, i) => ({
    name: key,
    label: SOURCE_LABELS[key] ?? key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
    value: data[key],
    color: SOURCE_COLORS[key] ?? FALLBACK_PALETTE[i % FALLBACK_PALETTE.length],
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="label"
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
        >
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number, _name: string) => [
            `${value} (${((value / total) * 100).toFixed(1)}%)`,
            'Registros',
          ]}
          labelFormatter={(label: string) => `Fuente: ${label}`}
        />
        <Legend
          formatter={(label: string) => label}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
