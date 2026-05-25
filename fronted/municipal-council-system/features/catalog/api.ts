import apiClient from '@/lib/axios'
import type { Entity, Period, Role, User, UserPayload, PaginatedResponse } from '@/lib/types'

// ─── Entities ─────────────────────────────────────────────────────────────────
export const entitiesApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Entity>>('/catalog/entities/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Entity>(`/catalog/entities/${id}/`).then((r) => r.data),
  create: (data: Partial<Entity>) =>
    apiClient.post<Entity>('/catalog/entities/', data).then((r) => r.data),
  update: (id: number, data: Partial<Entity>) =>
    apiClient.patch<Entity>(`/catalog/entities/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/catalog/entities/${id}/`).then((r) => r.data),
}

// ─── Periods ──────────────────────────────────────────────────────────────────
export const periodsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Period>>('/catalog/periods/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Period>(`/catalog/periods/${id}/`).then((r) => r.data),
  create: (data: Partial<Period>) =>
    apiClient.post<Period>('/catalog/periods/', data).then((r) => r.data),
  update: (id: number, data: Partial<Period>) =>
    apiClient.patch<Period>(`/catalog/periods/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/catalog/periods/${id}/`).then((r) => r.data),
}

// ─── Roles ────────────────────────────────────────────────────────────────────
export const rolesApi = {
  list: () =>
    apiClient.get<PaginatedResponse<Role>>('/catalog/roles/').then((r) => r.data),
  create: (data: Partial<Role>) =>
    apiClient.post<Role>('/catalog/roles/', data).then((r) => r.data),
  update: (id: number, data: Partial<Role>) =>
    apiClient.patch<Role>(`/catalog/roles/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/catalog/roles/${id}/`).then((r) => r.data),
}

// ─── Users ────────────────────────────────────────────────────────────────────
export const usersApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<User>>('/catalog/users/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<User>(`/catalog/users/${id}/`).then((r) => r.data),
  create: (data: UserPayload) =>
    apiClient.post<User>('/catalog/users/', data).then((r) => r.data),
  update: (id: number, data: UserPayload) =>
    apiClient.patch<User>(`/catalog/users/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/catalog/users/${id}/`).then((r) => r.data),
}
