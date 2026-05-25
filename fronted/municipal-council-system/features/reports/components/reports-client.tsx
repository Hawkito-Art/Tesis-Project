'use client'

import { useQuery } from '@tanstack/react-query'
import { FileText, ArrowRight } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { Skeleton } from '@/components/ui/skeleton'
import { reportsApi } from '@/features/reports/api'

export function ReportsClient() {
  const { data, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsApi.list(),
  })

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-base font-semibold">Reportes</h2>
        <p className="text-xs text-muted-foreground">Reportes finales disponibles</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-28 rounded-xl" />
            ))
          : data?.results.length
          ? data.results.map((report) => (
              <div
                key={report.id}
                className="bg-card border border-border rounded-xl p-5 hover:border-primary/40 hover:shadow-sm transition-all group"
              >
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-lg bg-primary/10 text-primary">
                    <FileText className="w-4 h-4" />
                  </div>
                  <ArrowRight className="w-4 h-4 text-muted-foreground/40 group-hover:text-primary transition-colors" />
                </div>
                <h3 className="mt-3 font-semibold text-sm text-foreground">{report.title}</h3>
                {report.description && (
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed line-clamp-2">
                    {report.description}
                  </p>
                )}
                <p className="text-xs text-muted-foreground mt-2">
                  {format(new Date(report.created_at), "d 'de' MMMM yyyy", { locale: es })}
                </p>
              </div>
            ))
          : (
            <div className="col-span-3 text-center py-12 text-muted-foreground text-sm">
              No hay reportes disponibles.
            </div>
          )}
      </div>
    </div>
  )
}
