import apiClient from '@/lib/axios'
import type { ImportJob, PaginatedResponse } from '@/lib/types'

export const ingestionApi = {
  upload: (file: File, importType: string, entityId?: number, periodId?: number) => {
    const form = new FormData()
    form.append('file', file)
    form.append('import_type', importType)
    if (entityId) form.append('entity', String(entityId))
    if (periodId) form.append('period', String(periodId))
    return apiClient
      .post<ImportJob>('/ingestion/upload/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data)
  },
  listJobs: (params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<ImportJob>>('/ingestion/jobs/', { params })
      .then((r) => r.data),
  retryJob: (id: number) =>
    apiClient.post<ImportJob>(`/ingestion/jobs/${id}/retry/`).then((r) => r.data),
}
