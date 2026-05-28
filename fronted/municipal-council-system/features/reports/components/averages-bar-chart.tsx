'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

export function AveragesBarChart({
  data,
}: {
  data: Record<string, number>
}) {
  const keys = Object.keys(data)

  if (keys.length === 0) {
    return <p className="text-sm text-muted-foreground">Sin datos.</p>
  }

  const items = Object.entries(data)
    .map(([code, avg]) => ({ code, avg }))
    .sort((a, b) => b.avg - a.avg)
    .slice(0, 10)

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={items}
        layout="vertical"
        margin={{ left: 120, right: 16, top: 8, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis
          type="category"
          dataKey="code"
          tick={{ fontSize: 11 }}
          width={110}
          tickFormatter={(code: string) =>
            code.length > 14 ? code.slice(0, 13) + '…' : code
          }
        />
        <Tooltip
          formatter={(value: number) => [value.toFixed(4), 'Promedio']}
        />
        <Bar
          dataKey="avg"
          fill="var(--color-primary)"
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
