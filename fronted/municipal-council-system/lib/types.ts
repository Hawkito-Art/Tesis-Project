// ─── Auth ─────────────────────────────────────────────────────────────────────
export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string | null
  entity: Entity | null
  is_active: boolean
}

/** Write payload for create/update — sends FK IDs instead of nested objects */
export interface UserPayload {
  email?: string
  first_name?: string
  last_name?: string
  role?: number | null
  entity?: number | null
  is_active?: boolean
}

// ─── Catalog ──────────────────────────────────────────────────────────────────
export interface Entity {
  id: number
  name: string
  code: string
  description?: string
  created_at?: string
  updated_at?: string
}

export interface Period {
  id: number
  name: string
  start_date: string
  end_date: string
  is_active: boolean
}

export interface Role {
  id: number
  name: string
  permissions?: string[]
}

// ─── Budget ───────────────────────────────────────────────────────────────────
export interface Budget {
  id: number
  entity: Entity
  period: Period
  total_amount: number
  status: string
  created_at: string
}

export interface BudgetItem {
  id: number
  budget: number
  code: string
  name: string
  amount: number
  executed: number
  percentage?: number
}

// ─── Ingestion ────────────────────────────────────────────────────────────────
export type ImportJobStatus = 'pending' | 'processing' | 'completed' | 'error'

export interface ImportJob {
  id: number
  filename: string
  import_type: string
  status: ImportJobStatus
  created_at: string
  updated_at: string
  error_log?: string
  entity?: Entity
  period?: Period
}

// ─── Indicators ───────────────────────────────────────────────────────────────
export interface IndicatorGroup {
  id: number
  name: string
  description?: string
}

export interface Variable {
  id: number
  name: string
  code: string
  type: string
}

export interface Indicator {
  id: number
  name: string
  code: string
  formula: string
  group: IndicatorGroup
  variables: Variable[]
}

export interface IndicatorRecord {
  id: number
  indicator: Indicator
  entity: Entity
  period: Period
  value: number
  recorded_at: string
}

// ─── Calculations ─────────────────────────────────────────────────────────────
export type CalcType = 'full' | 'partial' | 'projection'

export interface CalcResult {
  id: number
  entity: Entity
  period: Period
  calc_type: CalcType
  result_data: Record<string, unknown>
  created_at: string
}

// ─── Reports ──────────────────────────────────────────────────────────────────
export interface Report {
  id: number
  title: string
  description: string
  entity?: Entity
  period?: Period
  created_at: string
}

export interface Stat {
  label: string
  value: number | string
  change?: number
}

export interface Classification {
  id: number
  entity: Entity
  period: Period
  category: string
  score: number
  rank: number
}

// ─── Shared ───────────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  message: string
  detail?: string
  errors?: Record<string, string[]>
}
