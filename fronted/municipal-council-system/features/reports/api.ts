import apiClient from '@/lib/axios'
import type { Report, Classification, StatsPayload, PaginatedResponse } from '@/lib/types'

export const reportsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Report>>('/reports/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Report>(`/reports/${id}/`).then((r) => r.data),
  create: (data: Record<string, unknown>) =>
    apiClient.post<Report>('/reports/', data).then((r) => r.data),
}

export const statsApi = {
  get: (params?: Record<string, unknown>) =>
    apiClient.get<StatsPayload>('/stats/', { params }).then((r) => r.data),
}

export const classificationsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<Classification>>('/classifications/', { params })
      .then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Classification>(`/classifications/${id}/`).then((r) => r.data),
  calculate: (data: Record<string, unknown>) =>
    apiClient.post<Classification>('/classifications/calculate/', data).then((r) => r.data),
}
