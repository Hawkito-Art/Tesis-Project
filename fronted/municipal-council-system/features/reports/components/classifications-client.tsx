'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Calculator } from 'lucide-react'

import { classificationsApi } from '@/features/reports/api'
import { entitiesApi, periodsApi } from '@/features/catalog/api'
import type { Classification } from '@/lib/types'
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

const VALUE_LABELS: Record<string, string> = {
  alto_desempeno: 'Alto desempeño',
  desempeno_medio: 'Desempeño medio',
  desempeno_bajo: 'Desempeño bajo',
  sin_datos: 'Sin datos',
}
const VALUE_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  alto_desempeno: 'default',
  desempeno_medio: 'secondary',
  desempeno_bajo: 'destructive',
  sin_datos: 'outline',
}

const calculateSchema = z.object({
  entity: z.string({ required_error: 'Seleccioná una entidad' }),
  period: z.string({ required_error: 'Seleccioná un período' }),
})
type CalculateForm = z.infer<typeof calculateSchema>

export function ClassificationsClient() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(0)
  const [periodFilter, setPeriodFilter] = useState('all')
  const [open, setOpen] = useState(false)

  const form = useForm<CalculateForm>({ resolver: zodResolver(calculateSchema) })

  const { data, isLoading } = useQuery({
    queryKey: ['classifications', page, periodFilter],
    queryFn: () => classificationsApi.list({
      page: page + 1,
      period: periodFilter === 'all' ? undefined : periodFilter,
    }),
  })

  const { data: entities } = useQuery({ queryKey: ['entities', 0], queryFn: () => entitiesApi.list() })
  const { data: periods } = useQuery({ queryKey: ['periods'], queryFn: () => periodsApi.list() })

  const calculateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => classificationsApi.calculate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classifications'] })
      setOpen(false)
      form.reset()
    },
  })

  const columns: ColumnDef<Classification>[] = [
    { accessorKey: 'entity_code', header: 'Entidad' },
    { accessorKey: 'period_display', header: 'Período' },
    { accessorKey: 'classification_type', header: 'Tipo' },
    {
      accessorKey: 'value',
      header: 'Valor',
      cell: ({ row }) => (
        <Badge variant={VALUE_VARIANTS[row.original.value] ?? 'outline'}>
          {VALUE_LABELS[row.original.value] ?? row.original.value}
        </Badge>
      ),
    },
    { accessorKey: 'rule_version', header: 'Versión', size: 90 },
    {
      accessorKey: 'created_at',
      header: 'Creado',
      cell: ({ row }) => new Date(row.original.created_at).toLocaleDateString('es-AR'),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-base font-semibold">Clasificaciones</h2>
          <p className="text-xs text-muted-foreground">Clasificaciones de entidades por período</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={periodFilter} onValueChange={setPeriodFilter}>
            <SelectTrigger className="h-8 w-40 text-xs"><SelectValue placeholder="Filtrar período" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {periods?.results.map((p) => (
                <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-8 text-xs"><Calculator className="w-3.5 h-3.5 mr-1" />Calcular clasificación</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Calcular clasificación</DialogTitle></DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit((vals) => calculateMutation.mutate({
                  entity: Number(vals.entity),
                  period: Number(vals.period),
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
                  <Button type="submit" className="w-full" disabled={calculateMutation.isPending}>
                    {calculateMutation.isPending ? 'Calculando…' : 'Calcular'}
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
        emptyMessage="No hay clasificaciones disponibles."
      />
    </div>
  )
}
