'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, ChevronDown, ChevronRight } from 'lucide-react'
import { useRouter } from 'next/navigation'

import { reportsApi } from '@/features/reports/api'
import type { Report } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const STATUS_LABELS: Record<string, string> = { generated: 'Generado', error: 'Error' }
const STATUS_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive'> = {
  generated: 'default', error: 'destructive',
}
const TYPE_LABELS: Record<string, string> = { operational: 'Operativo', executive: 'Ejecutivo' }

function SummaryCards({ report }: { report: Report }) {
  const s = report.summary as Record<string, unknown>
  const items = [
    { label: 'Registros totales', value: String(s.total_records ?? '—') },
    { label: 'Con valor', value: String(s.records_with_value ?? '—') },
    { label: 'Resultados de cálculo', value: String(s.total_calculation_results ?? '—') },
    { label: 'Último cálculo', value: String(s.latest_calculation_id ?? '—') },
  ]
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {items.map((item) => (
        <Card key={item.label}>
          <CardHeader className="p-3 pb-1"><CardTitle className="text-xs text-muted-foreground font-normal">{item.label}</CardTitle></CardHeader>
          <CardContent className="p-3 pt-0"><p className="text-lg font-bold">{item.value}</p></CardContent>
        </Card>
      ))}
    </div>
  )
}

function SourcesTable({ report }: { report: Report }) {
  const sources = (report.summary as Record<string, unknown>)?.records_by_source as Record<string, unknown> | undefined
  if (!sources || !Object.keys(sources).length) return null
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Registros por fuente</CardTitle></CardHeader>
      <CardContent>
        <table className="w-full text-sm">
          <thead><tr className="text-muted-foreground border-b"><th className="text-left py-1">Fuente</th><th className="text-right py-1">Cantidad</th></tr></thead>
          <tbody>
            {Object.entries(sources).map(([src, count]) => (
              <tr key={src} className="border-b last:border-0">
                <td className="py-1.5 capitalize">{src}</td>
                <td className="text-right py-1.5 font-mono">{String(count)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}

function IndicatorsTable({ report }: { report: Report }) {
  const indicators = (report.detail as Record<string, unknown>)?.indicators as Record<string, Record<string, unknown>> | undefined
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  if (!indicators) return null
  const codes = Object.keys(indicators)

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Indicadores ({codes.length})</CardTitle></CardHeader>
      <CardContent>
        {codes.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin indicadores en este reporte.</p>
        ) : (
          <div className="text-sm space-y-1">
            {codes.map((code) => {
              const vars = indicators[code]
              const isOpen = expanded.has(code)
              return (
                <div key={code}>
                  <button className="flex items-center gap-1.5 w-full text-left py-1.5 font-medium hover:text-primary"
                    onClick={() => setExpanded((prev) => { const n = new Set(prev); isOpen ? n.delete(code) : n.add(code); return n })}>
                    {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    {code}
                  </button>
                  {isOpen && (
                    <div className="ml-5 space-y-0.5 text-muted-foreground">
                      {Object.entries(vars).map(([vname, val]) => (
                        <div key={vname} className="flex justify-between py-0.5">
                          <span>{vname}</span>
                          <span className="font-mono">{val !== null ? String(val) : '—'}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ClassificationsSection({ report }: { report: Report }) {
  const classifications = (report.detail as Record<string, unknown>)?.classifications as Record<string, unknown> | undefined
  if (!classifications) return null
  const items = classifications.items as Record<string, unknown>[] | undefined

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Clasificaciones</CardTitle></CardHeader>
      <CardContent>
        {!items || items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin clasificaciones en este reporte.</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-muted-foreground border-b"><th className="text-left py-1">Tipo</th><th className="text-left py-1">Valor</th><th className="text-left py-1">Versión</th></tr></thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-1.5">{String(item.classification_type)}</td>
                  <td className="py-1.5"><Badge variant="outline">{String(item.value)}</Badge></td>
                  <td className="py-1.5 font-mono text-xs">{String(item.rule_version)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  )
}

function MetadataSection({ report }: { report: Report }) {
  const [open, setOpen] = useState(false)
  return (
    <Card>
      <CardHeader className="cursor-pointer" onClick={() => setOpen(!open)}>
        <div className="flex items-center gap-1.5">
          {open ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          <CardTitle className="text-sm">Metadatos</CardTitle>
        </div>
      </CardHeader>
      {open && (
        <CardContent>
          <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-60">
            {JSON.stringify(report.metadata, null, 2)}
          </pre>
        </CardContent>
      )}
    </Card>
  )
}

export function ReportsDetailClient({ reportId }: { reportId: number }) {
  const router = useRouter()

  const { data: report, isLoading } = useQuery({
    queryKey: ['report', reportId],
    queryFn: () => reportsApi.get(reportId),
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20" />)}
        </div>
        <Skeleton className="h-40" />
      </div>
    )
  }

  if (!report) {
    return <p className="text-sm text-muted-foreground">Reporte no encontrado.</p>
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h2 className="text-base font-semibold">Detalle de reporte</h2>
          <p className="text-xs text-muted-foreground">
            {report.entity_code} · {report.period_display}
          </p>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl p-5">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Entidad</p>
            <p className="text-sm font-semibold mt-0.5">{report.entity_code}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Período</p>
            <p className="text-sm font-semibold mt-0.5">{report.period_display}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Tipo</p>
            <p className="text-sm font-semibold mt-0.5">{TYPE_LABELS[report.report_type] ?? report.report_type}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Estado</p>
            <div className="mt-0.5">
              <Badge variant={STATUS_VARIANTS[report.status] ?? 'secondary'}>
                {STATUS_LABELS[report.status] ?? report.status}
              </Badge>
            </div>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Generado por</p>
            <p className="text-sm font-semibold mt-0.5">{report.generated_by_email ?? '—'}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Generado el</p>
            <p className="text-sm font-semibold mt-0.5">{new Date(report.generated_at).toLocaleString('es-AR')}</p>
          </div>
        </div>
      </div>

      <SummaryCards report={report} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SourcesTable report={report} />
        <ClassificationsSection report={report} />
      </div>

      <IndicatorsTable report={report} />
      <MetadataSection report={report} />
    </div>
  )
}
