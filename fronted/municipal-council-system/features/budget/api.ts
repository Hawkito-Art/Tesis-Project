import apiClient from '@/lib/axios'
import type { Budget, BudgetItem, PaginatedResponse } from '@/lib/types'

export const budgetsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Budget>>('/budget/budgets/', { params }).then((r) => r.data),
  get: (id: number) =>
    apiClient.get<Budget>(`/budget/budgets/${id}/`).then((r) => r.data),
  create: (data: Partial<Budget>) =>
    apiClient.post<Budget>('/budget/budgets/', data).then((r) => r.data),
  update: (id: number, data: Partial<Budget>) =>
    apiClient.patch<Budget>(`/budget/budgets/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/budget/budgets/${id}/`).then((r) => r.data),
}

export const budgetItemsApi = {
  list: (budgetId: number) =>
    apiClient
      .get<PaginatedResponse<BudgetItem>>('/budget/budget-items/', { params: { budget: budgetId } })
      .then((r) => r.data),
  create: (data: Partial<BudgetItem>) =>
    apiClient.post<BudgetItem>('/budget/budget-items/', data).then((r) => r.data),
  update: (id: number, data: Partial<BudgetItem>) =>
    apiClient.patch<BudgetItem>(`/budget/budget-items/${id}/`, data).then((r) => r.data),
  remove: (id: number) =>
    apiClient.delete(`/budget/budget-items/${id}/`).then((r) => r.data),
}
