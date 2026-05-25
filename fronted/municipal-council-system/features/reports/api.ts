import apiClient from '@/lib/axios'
import type { Report, Classification, Stat, PaginatedResponse } from '@/lib/types'

export const reportsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Report>>('/reports/reports/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Report>(`/reports/reports/${id}/`).then((r) => r.data),
}

export interface ChartSeries {
  key: 'bar' | 'line' | string
  data: Record<string, unknown>[]
}

export const statsApi = {
  get: (params?: Record<string, unknown>) =>
    apiClient.get<{ stats: Stat[]; chart_data: ChartSeries[] }>('/reports/stats/', { params }).then((r) => r.data),
}

export const classificationsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<Classification>>('/reports/classifications/', { params })
      .then((r) => r.data),
}
