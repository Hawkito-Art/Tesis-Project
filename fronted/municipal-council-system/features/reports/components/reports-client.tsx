'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { useRouter } from 'next/navigation'
import { Eye, Plus } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { reportsApi } from '@/features/reports/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { Report } from '@/lib/types'
import { DataTable } from '@/components/shared/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Form, FormControl, FormField, FormItem, FormLabel, FormMessage,
} from '@/components/ui/form'
import { Checkbox } from '@/components/ui/checkbox'

const STATUS_LABELS: Record<string, string> = { generated: 'Generado', error: 'Error' }
const STATUS_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive'> = {
  generated: 'default', error: 'destructive',
}
const TYPE_LABELS: Record<string, string> = { operational: 'Operativo', executive: 'Ejecutivo' }

const generateSchema = z.object({
  entity: z.string({ required_error: 'Seleccioná una entidad' }),
  period: z.string({ required_error: 'Seleccioná un período' }),
  report_type: z.enum(['operational', 'executive']),
  include_stats: z.boolean(),
  include_classifications: z.boolean(),
})

type GenerateForm = z.infer<typeof generateSchema>

export function ReportsClient() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(0)
  const [entityFilter, setEntityFilter] = useState('all')
  const [periodFilter, setPeriodFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [open, setOpen] = useState(false)

  const form = useForm<GenerateForm>({
    resolver: zodResolver(generateSchema),
    defaultValues: { report_type: 'operational', include_stats: true, include_classifications: true },
  })

  const { data, isLoading } = useQuery({
    queryKey: ['reports', page, entityFilter, periodFilter, typeFilter, statusFilter],
    queryFn: () => reportsApi.list({
      page: page + 1,
      entity: entityFilter === 'all' ? undefined : entityFilter,
      period: periodFilter === 'all' ? undefined : periodFilter,
      report_type: typeFilter === 'all' ? undefined : typeFilter,
      status: statusFilter === 'all' ? undefined : statusFilter,
    }),
  })

  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const createMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => reportsApi.create(payload),
    onSuccess: (report) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setOpen(false)
      form.reset()
      router.push(`/dashboard/reports/${report.id}`)
    },
  })

  const columns: ColumnDef<Report>[] = [
    { accessorKey: 'entity_code', header: 'Entidad' },
    { accessorKey: 'period_display', header: 'Período' },
    {
      accessorKey: 'report_type',
      header: 'Tipo',
      cell: ({ row }) => TYPE_LABELS[row.original.report_type] ?? row.original.report_type,
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
    { accessorKey: 'generated_by_email', header: 'Generado por' },
    {
      accessorKey: 'generated_at',
      header: 'Fecha',
      cell: ({ row }) => new Date(row.original.generated_at).toLocaleDateString('es-AR'),
    },
    {
      id: 'actions',
      size: 60,
      cell: ({ row }) => (
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0"
          onClick={() => router.push(`/dashboard/reports/${row.original.id}`)}>
          <Eye className="w-3.5 h-3.5" />
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Reportes</h2>
          <p className="text-xs text-muted-foreground">Reportes generados por entidad y período</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={entityFilter} onValueChange={setEntityFilter}>
            <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Entidad" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {entities?.results.map((e) => (
                <SelectItem key={e.id} value={String(e.id)}>{e.code}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-36 text-xs"><SelectValue placeholder="Período" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {periods?.results.map((p) => (
                <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="h-8 w-32 text-xs"><SelectValue placeholder="Tipo" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="operational">Operativo</SelectItem>
              <SelectItem value="executive">Ejecutivo</SelectItem>
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="h-8 w-32 text-xs"><SelectValue placeholder="Estado" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="generated">Generado</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-8 text-xs"><Plus className="w-3.5 h-3.5 mr-1" />Generar reporte</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Generar reporte</DialogTitle></DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit((vals) => createMutation.mutate({
                  entity: Number(vals.entity),
                  period: Number(vals.period),
                  report_type: vals.report_type,
                  include_stats: vals.include_stats,
                  include_classifications: vals.include_classifications,
                }))} className="space-y-4">
                  <FormField control={form.control} name="entity" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Entidad</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl><SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger></FormControl>
                        <SelectContent>
                          {entities?.results.map((e) => (
                            <SelectItem key={e.id} value={String(e.id)}>{e.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="period" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Período</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl><SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger></FormControl>
                        <SelectContent>
                          {periods?.results.map((p) => (
                            <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="report_type" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tipo de reporte</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="operational">Operativo</SelectItem>
                          <SelectItem value="executive">Ejecutivo</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="include_stats" render={({ field }) => (
                    <FormItem className="flex items-center gap-2">
                      <FormControl><Checkbox checked={field.value} onCheckedChange={field.onChange} /></FormControl>
                      <FormLabel className="!mt-0">Incluir estadísticas</FormLabel>
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="include_classifications" render={({ field }) => (
                    <FormItem className="flex items-center gap-2">
                      <FormControl><Checkbox checked={field.value} onCheckedChange={field.onChange} /></FormControl>
                      <FormLabel className="!mt-0">Incluir clasificaciones</FormLabel>
                    </FormItem>
                  )} />
                  <Button type="submit" className="w-full" disabled={createMutation.isPending}>
                    {createMutation.isPending ? 'Generando…' : 'Generar'}
                  </Button>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
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
        emptyMessage="No hay reportes generados."
      />
    </div>
  )
}
