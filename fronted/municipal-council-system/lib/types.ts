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
  is_active: boolean
  is_staff: boolean
  email_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface UserPayload {
  email?: string
  first_name?: string
  last_name?: string
  password?: string
  is_active?: boolean
  is_staff?: boolean
  email_verified?: boolean
}

// ─── Catalog ──────────────────────────────────────────────────────────────────
export interface Entity {
  id: number
  code: string
  name: string
  type: string
  description?: string
  is_consolidated: boolean
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface Period {
  id: number
  name: string
  year: number
  month: number
  period_type: string
  is_active: boolean
  created_at?: string
}

export interface Role {
  id: number
  name: string
  description?: string
  is_active?: boolean
  created_at?: string
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
export type ImportJobStatus = 'pendiente' | 'en_progreso' | 'completado' | 'error'

export interface ImportJob {
  id: number
  document: number
  document_name: string
  document_import_type: string
  entity: number | null
  entity_detail: { id: number; code: string; name: string } | null
  period: number | null
  period_detail: { id: number; name: string; year: number; month: number } | null
  status: ImportJobStatus
  total_rows: number
  processed_rows: number
  error_rows: number
  error_log: string
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface ImportJobDetail {
  id: number
  import_job: number
  row_number: number
  raw_data: Record<string, unknown>
  is_valid: boolean
  error_message: string
  created_at: string
}

// ─── Indicators ───────────────────────────────────────────────────────────────
export type GroupType = 'fundamental' | 'limite' | 'otro'

export interface IndicatorGroup {
  id: number
  name: string
  group_type: GroupType
  order: number
  is_active: boolean
  created_at: string
}

export type IndicatorUnit = 'MP' | 'U' | 'p' | 'peso' | 'Coef'

export interface IndicatorVariable {
  id: number
  indicator: number
  name: string
  label: string
  description: string
  is_active: boolean
}

export interface Indicator {
  id: number
  indicator: string
  name: string
  description: string
  unit: IndicatorUnit
  group: number
  group_name: string
  variables: IndicatorVariable[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export type RecordSource = 'manual' | 'imported' | 'calculated'

export interface IndicatorRecord {
  id: number
  entity: number
  indicator: number
  period: number
  variable_name: string
  value: string | null
  source: RecordSource
  source_display: string
  import_job: number | null
  import_job_id: number | null
  calculation: number | null
  calculation_id: number | null
  entity_code: string
  indicator_code: string
  period_display: string
  created_at: string
  updated_at: string
}

// ─── Calculations ─────────────────────────────────────────────────────────────
export type CalcStatus = 'pendiente' | 'en_progreso' | 'completado' | 'error'

export interface Calculation {
  id: number
  name: string
  description: string
  period: number
  period_display: string
  status: CalcStatus
  executed_by: number | null
  executed_by_email: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
  results?: CalculationResult[]
}

export interface CalculationResult {
  id: number
  calculation: number
  entity: number
  indicator: number
  variable_name: string
  value: string | null
  entity_code: string
  indicator_code: string
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
