import apiClient from '@/lib/axios'
import type { Entity, Period, Role, User, UserPayload, PaginatedResponse } from '@/lib/types'

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

export const rolesApi = {
  list: () =>
    apiClient.get<PaginatedResponse<Role>>('/roles/').then((r) => r.data),
  create: (data: Partial<Role>) =>
    apiClient.post<Role>('/roles/', data).then((r) => r.data),
  update: (id: number, data: Partial<Role>) =>
    apiClient.patch<Role>(`/roles/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/roles/${id}/`).then((r) => r.data),
}

export const usersApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<User>>('/users/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<User>(`/users/${id}/`).then((r) => r.data),
  create: (data: UserPayload) =>
    apiClient.post<User>('/users/', data).then((r) => r.data),
  update: (id: number, data: UserPayload) =>
    apiClient.patch<User>(`/users/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/users/${id}/`).then((r) => r.data),
}
