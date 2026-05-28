import apiClient from '@/lib/axios'
import type { ImportJob, ImportJobDetail, PaginatedResponse } from '@/lib/types'

export const ingestionApi = {
  upload: (name: string, file: File, importType: string, entityId?: number, periodId?: number) => {
    const form = new FormData()
    form.append('name', name)
    form.append('file', file)
    form.append('import_type', importType)
    if (entityId) form.append('entity', String(entityId))
    if (periodId) form.append('period', String(periodId))
    return apiClient
      .post<{ document: unknown; import_job: ImportJob }>('/ingestion/documents/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data.import_job)
  },

  listJobs: (params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<ImportJob>>('/ingestion/import-jobs/', { params })
      .then((r) => r.data),

  getJob: (id: number) =>
    apiClient.get<ImportJob>(`/ingestion/import-jobs/${id}/`).then((r) => r.data),

  processJob: (id: number, entityId: number, periodId: number) =>
    apiClient
      .post<{ import_job: ImportJob; upsert: { created: number; updated: number; total: number } }>(
        `/ingestion/import-jobs/${id}/`,
        { entity: entityId, period: periodId },
      )
      .then((r) => r.data),

  getJobDetails: (id: number, params?: Record<string, unknown>) =>
    apiClient
      .get<PaginatedResponse<ImportJobDetail>>(`/ingestion/import-jobs/${id}/details/`, { params })
      .then((r) => r.data),

  retryJob: (id: number) =>
    apiClient.post<ImportJob>(`/ingestion/import-jobs/${id}/retry/`).then((r) => r.data),
}
