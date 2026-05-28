'use client'

import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'

import { indicatorsApi } from '@/features/indicators/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'

interface Props {
  indicatorId: string
}

export function IndicatorDetailClient({ indicatorId }: Props) {
  const { data: indicator, isLoading } = useQuery({
    queryKey: ['indicator', indicatorId],
    queryFn: () => indicatorsApi.get(Number(indicatorId)),
  })

  if (isLoading) {
    return <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
  }

  if (!indicator) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Indicador no encontrado.</p>
        <Button variant="outline" size="sm" className="mt-4" asChild>
          <Link href="/dashboard/indicators">Volver</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" className="h-7 gap-1" asChild>
          <Link href="/dashboard/indicators"><ArrowLeft className="w-3.5 h-3.5" />Volver</Link>
        </Button>
        <div>
          <h2 className="text-base font-semibold">{indicator.indicator}</h2>
          <p className="text-xs text-muted-foreground">{indicator.name}</p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-sm">Detalles</CardTitle></CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div><dt className="text-xs text-muted-foreground">Código</dt><dd className="font-mono font-medium mt-0.5">{indicator.indicator}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Nombre</dt><dd className="font-medium mt-0.5">{indicator.name}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Unidad</dt><dd className="mt-0.5"><Badge variant="outline" className="font-mono">{indicator.unit}</Badge></dd></div>
            <div><dt className="text-xs text-muted-foreground">Grupo</dt><dd className="font-medium mt-0.5">{indicator.group_name}</dd></div>
            <div className="col-span-2"><dt className="text-xs text-muted-foreground">Descripción</dt><dd className="font-medium mt-0.5">{indicator.description || '—'}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Activo</dt><dd className="font-medium mt-0.5">{indicator.is_active ? 'Sí' : 'No'}</dd></div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Variables ({indicator.variables.length})</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="text-xs font-semibold">Nombre</TableHead>
                <TableHead className="text-xs font-semibold">Etiqueta</TableHead>
                <TableHead className="text-xs font-semibold">Activo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {indicator.variables.length === 0 ? (
                <TableRow><TableCell colSpan={3} className="text-center text-muted-foreground text-sm py-8">No tiene variables asociadas.</TableCell></TableRow>
              ) : indicator.variables.map((v) => (
                <TableRow key={v.id}>
                  <TableCell><code className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">{v.name}</code></TableCell>
                  <TableCell className="text-sm">{v.label}</TableCell>
                  <TableCell>{v.is_active ? <Badge className="bg-emerald-100 text-emerald-700">Sí</Badge> : <Badge variant="secondary">No</Badge>}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
