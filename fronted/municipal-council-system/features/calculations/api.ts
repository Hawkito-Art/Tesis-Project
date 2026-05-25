import apiClient from '@/lib/axios'
import type { Calculation, CalculationResult, PaginatedResponse } from '@/lib/types'

export const calculationsApi = {
  run: (params: { entity: number; period: number; name?: string; description?: string }) =>
    apiClient.post<Calculation>('/calculations/run/', params).then((r) => r.data),

  list: (params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<Calculation>>('/calculations/', { params })
      .then((r) => r.data),

  get: (id: number) =>
    apiClient.get<Calculation>(`/calculations/${id}/`).then((r) => r.data),

  getResults: (id: number, params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<CalculationResult>>(`/calculations/${id}/results/`, { params })
      .then((r) => r.data),

  exportXlsx: (entityId?: number, periodId?: number) => {
    const body: Record<string, number> = {}
    if (entityId) body.entity = entityId
    if (periodId) body.period = periodId
    return apiClient
      .post('/exports/xlsx/', body, { responseType: 'blob' })
      .then((r) => {
        const url = window.URL.createObjectURL(
          new Blob([r.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          }),
        )
        const a = document.createElement('a')
        a.href = url
        a.download = `indicadores-${entityId ?? 'todas'}-${periodId ?? 'todos'}.xlsx`
        a.click()
        window.URL.revokeObjectURL(url)
      })
  },
}
