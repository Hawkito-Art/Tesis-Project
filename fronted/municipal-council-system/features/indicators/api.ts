import apiClient from '@/lib/axios'
import type {
  Indicator,
  IndicatorGroup,
  IndicatorRecord,
  Variable,
  PaginatedResponse,
} from '@/lib/types'

export const indicatorGroupsApi = {
  list: () =>
    apiClient.get<PaginatedResponse<IndicatorGroup>>('/indicators/groups/').then((r) => r.data),
  create: (data: Partial<IndicatorGroup>) =>
    apiClient.post<IndicatorGroup>('/indicators/groups/', data).then((r) => r.data),
  update: (id: number, data: Partial<IndicatorGroup>) =>
    apiClient.patch<IndicatorGroup>(`/indicators/groups/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/indicators/groups/${id}/`).then((r) => r.data),
}

export const indicatorsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Indicator>>('/indicators/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Indicator>(`/indicators/${id}/`).then((r) => r.data),
  create: (data: Partial<Indicator>) =>
    apiClient.post<Indicator>('/indicators/', data).then((r) => r.data),
  update: (id: number, data: Partial<Indicator>) =>
    apiClient.patch<Indicator>(`/indicators/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/indicators/${id}/`).then((r) => r.data),
}

export const variablesApi = {
  list: () =>
    apiClient.get<PaginatedResponse<Variable>>('/indicators/variables/').then((r) => r.data),
  create: (data: Partial<Variable>) =>
    apiClient.post<Variable>('/indicators/variables/', data).then((r) => r.data),
  update: (id: number, data: Partial<Variable>) =>
    apiClient.patch<Variable>(`/indicators/variables/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/indicators/variables/${id}/`).then((r) => r.data),
}

export const recordsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<IndicatorRecord>>('/indicators/records/', { params })
      .then((r) => r.data),
  bulkCreate: (records: Partial<IndicatorRecord>[]) =>
    apiClient.post('/indicators/records/bulk/', { records }).then((r) => r.data),
}
