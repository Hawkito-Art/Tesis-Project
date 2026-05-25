import apiClient from '@/lib/axios'
import type { CalcResult, PaginatedResponse } from '@/lib/types'

export const calculationsApi = {
  run: (params: { entity: number; period: number; calc_type: string }) =>
    apiClient.post<{ job_id?: string; result?: CalcResult }>('/calculations/run/', params).then((r) => r.data),
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<CalcResult>>('/calculations/results/', { params }).then((r) => r.data),
}
