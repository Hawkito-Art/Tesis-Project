# Spec: Integración completa del módulo Indicadores

## Resumen

Integrar el frontend de Indicadores con el backend real. Actualmente el frontend tiene tipos inventados, campos de formulario que no existen en backend, endpoints que llaman a rutas incorrectas, y faltan features completas (cálculos, exportación, detalle de indicador, registros).

---

## Gap Analysis

### Gaps de tipos (`lib/types.ts`)

| # | Tipo | Problema | Severidad |
|---|------|----------|-----------|
| T1 | `IndicatorGroup` | Frontend: `{ id, name, description? }` — Backend: `{ id, name, group_type, order, is_active, created_at }` | ALTO |
| T2 | `Variable` | Frontend: `{ id, name, code, type }` — Backend: `{ id, indicator, name, label, description, is_active }`. No existe `code` ni `type`. | ALTO |
| T3 | `Indicator` | Frontend: `{ id, name, code, formula, group, variables }` — Backend: `{ id, indicator, name, description, unit, group, group_name, variables, is_active, created_at, updated_at }`. No existe `code` (es `indicator`). No existe `formula`. | ALTO |
| T4 | `IndicatorRecord` | Frontend: `{ id, indicator, entity, period, value, recorded_at }` — Backend: `{ id, entity, indicator, period, variable_name, value, source, source_display, import_job, import_job_id, calculation, calculation_id, entity_code, indicator_code, period_display, created_at, updated_at }`. Faltan: `variable_name`, `source`, `source_display`, `entity_code`, `indicator_code`, `period_display`, `updated_at`. Sobra: `recorded_at`. | ALTO |
| T5 | `CalcResult` / `CalcType` | Frontend inventó `calc_type`, `result_data` — Backend no tiene esos campos. `Calculation` tiene `name`,`description`,`period`,`status`. `CalculationResult` es tabla por indicador/variable. | ALTO |

### Gaps de API (`api.ts`)

| # | API | Problema | Severidad |
|---|-----|----------|-----------|
| A1 | `variablesApi.list()` | No acepta `params` — backend soporta filtrado por `indicator`, `name`, `is_active`, search, ordering | MEDIO |
| A2 | `recordsApi.bulkCreate()` | POSTea a `/indicators/records/bulk/` — ese endpoint NO existe en backend. Backend solo tiene GET list read-only para records. | CRÍTICO |
| A3 | `calculationsApi.run()` | POSTea a `/calculations/run/` (sin `/api`) y envía `calc_type` que backend ignora | ALTO |
| A4 | `calculationsApi.list()` | GETea a `/calculations/results/` (sin `/api`) — ese endpoint NO existe. Backend tiene `GET /api/calculations/<pk>/results/` | CRÍTICO |
| A5 | Export endpoint | Frontend llama a `/calculations/export/` — backend expone en `POST /api/exports/xlsx/` | ALTO |

### Gaps de componentes/UI

| # | Componente | Problema | Severidad |
|---|-----------|----------|-----------|
| C1 | `indicators-client.tsx` | Formulario tiene `code`, `formula` que no existen en backend. Falta: `unit` (select), `description`, `is_active`. El campo `group` se envía como `group` pero backend espera `group` (PK) — bien ese. | ALTO |
| C2 | `groups-client.tsx` | Formulario tiene `description` que no existe en backend. Falta: `group_type` (select: fundamental/limite/otro), `order`, `is_active` | ALTO |
| C3 | `variables-client.tsx` | Formulario tiene `code`, `type` que no existen. Falta: `indicator` (FK, requerido), `label`, `description`, `is_active` | ALTO |
| C4 | `records-client.tsx` | Columnas muestran `indicator.name`, `entity.name`, `period.name`, `recorded_at` — backend retorna IDs planos, no objetos anidados para indicator/entity/period. Faltan columnas: `variable_name`, `source_display` | ALTO |
| C5 | `calc-run-client.tsx` | Envía `calc_type` que backend ignora | ALTO |
| C6 | `calc-results-client.tsx` | Muestra tabla de CalcResults (tipo inventado) pero backend retorna cálculo por indicador/variable | ALTO |

### Gaps de features faltantes

| # | Feature | Descripción | Severidad |
|---|---------|-------------|-----------|
| F1 | Detalle de indicador | No hay página para ver un indicador individual con sus variables asociadas | MEDIO |
| F2 | Panel de resultados de cálculo | No hay UI para ver resultados de un cálculo específico (GET /api/calculations/<pk>/results/) | ALTO |
| F3 | Exportar XLSX | No hay botón de exportación funcional que llame al endpoint correcto | ALTO |
| F4 | Listado de cálculos ejecutados | Backend no tiene endpoint `GET /api/calculations/` — necesario para que el frontend muestre el historial | ALTO |
| F5 | Vista de registros de indicadores completa | La UI actual de records no permite ver source, no permite crear/editar (aunque backend no tiene create endpoint) | MEDIO |
| F6 | Cambiar `unit` de select de texto | El backend tiene choices MP/U/p/peso/Coef — frontend debe mostrar eso | BAJO |

### Gaps de backend

| # | Backend | Qué falta | Severidad |
|---|---------|-----------|-----------|
| B1 | `GET /api/calculations/` | No existe listado de Calculations, necesario para frontend de historial | ALTO |
| B2 | `services.py` (indicators) | Archivo existe pero está vacío — debería contener lógica de negocio de indicadores | BAJO (no bloqueante) |
| B3 | Calculation no tiene `calc_type` | Si se necesita clasificar cálculos, hay que agregarlo al modelo | DECISIÓN |

---

## Tareas de implementación

### Fase 1: Backend — Endpoints faltantes

#### Tarea 1.1: Backend — Agregar `GET /api/calculations/` (listado de cálculos)

**Archivo**: `backend/tesis/apps/calculations/views.py`

Nueva clase `CalculationListContractAPIView`:
- `GET` → listado paginado de `Calculation`, ordenado por `-created_at`
- `select_related('period', 'executed_by')` para evitar N+1
- Permission: `IsAuthenticated, CalculationPermission`
- Serializer: `CalculationSerializer` (sin results anidados para performance — o crear `CalculationListSerializer`)

**Archivo**: `backend/tesis/apps/calculations/serializers.py`

Opcional: `CalculationListSerializer` sin `results` anidados, con `period_display`, `executed_by_email`.

**Archivo**: `backend/tesis/apps/calculations/urls.py`

```python
path('', CalculationListContractAPIView.as_view(), name='calculations-list'),
```

**Tests**: Verificar que lista paginada, requiere auth, respeta permisos.

---

#### Tarea 1.2: Backend — Refactor `CalculationRunSerializer` (sacar `calc_type` si llega del frontend)

**Archivo**: `backend/tesis/apps/calculations/serializers.py`

No requiere cambios mayores — solo verificar que el serializer actual ignore campos extra. DRF por defecto ignora campos no declarados, así que esto ya funciona. Documentar.

---

#### Tarea 1.3: Backend — Verificar que `recordsApi.bulkCreate()` no tiene contraparte

Decisión: NO implementar bulk create de records por ahora. El flujo correcto es:
1. Subir Excel con Ingestion → procesar → crea IndicatorRecords automáticamente
2. Si se necesita crear records manuales, sería un endpoint POST a `/api/indicators/records/`

Se agrega nota en el spec sobre esto.

---

### Fase 2: Frontend — Tipos (`lib/types.ts`)

#### Tarea 2.1: Corregir `IndicatorGroup`

```typescript
export interface IndicatorGroup {
  id: number
  name: string
  group_type: 'fundamental' | 'limite' | 'otro'
  order: number
  is_active: boolean
  created_at: string
}
```

#### Tarea 2.2: Corregir `Variable` → `IndicatorVariable`

```typescript
export interface IndicatorVariable {
  id: number
  indicator: number
  name: string
  label: string
  description: string
  is_active: boolean
}
```

Renombrar de `Variable` a `IndicatorVariable` en TODOS los archivos que la usen.

#### Tarea 2.3: Corregir `Indicator`

```typescript
export type IndicatorUnit = 'MP' | 'U' | 'p' | 'peso' | 'Coef'

export interface Indicator {
  id: number
  indicator: string        // código único, ej: "VENTAS_TOT"
  name: string             // nombre legible
  description: string
  unit: IndicatorUnit
  group: number            // FK a IndicatorGroup (PLANO, no anidado)
  group_name: string       // read-only del backend
  variables: IndicatorVariable[]
  is_active: boolean
  created_at: string
  updated_at: string
}
```

NOTA: Backend retorna `group_name` (string) como campo extra, no `group` como objeto anidado. El frontend debe leer `group_name` para mostrar el nombre, no `group.name`.

#### Tarea 2.4: Corregir `IndicatorRecord`

```typescript
export type RecordSource = 'manual' | 'imported' | 'calculated'

export interface IndicatorRecord {
  id: number
  entity: number
  indicator: number
  period: number
  variable_name: string
  value: string | null     // DecimalField → string en JSON
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
```

#### Tarea 2.5: Corregir `CalcResult` / agregar tipos de cálculos

```typescript
export interface Calculation {
  id: number
  name: string
  description: string
  period: number
  period_display: string
  status: 'pendiente' | 'en_progreso' | 'completado' | 'error'
  executed_by: number | null
  executed_by_email: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
  updated_at: string
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
```

Eliminar `CalcType` y `CalcResult` viejos.

---

#### Tarea 2.6: Agregar `PaginatedResponse` si no existe

Ya existe en `lib/types.ts:170`:
```typescript
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
```

Sin cambios.

---

### Fase 3: Frontend — API layer (`api.ts`)

#### Tarea 3.1: Corregir `features/indicators/api.ts`

```typescript
export const variablesApi = {
  list: (params?: Record<string, unknown>) =>                         // <-- agregar params
    apiClient.get<PaginatedResponse<IndicatorVariable>>('/indicators/variables/', { params }).then((r) => r.data),
  // ... create, update, remove igual
}

// ELIMINAR recordsApi.bulkCreate() — no existe en backend
export const recordsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<IndicatorRecord>>('/indicators/records/', { params }).then((r) => r.data),
}
```

#### Tarea 3.2: Corregir `features/calculations/api.ts`

```typescript
import apiClient from '@/lib/axios'
import type { Calculation, CalculationResult, PaginatedResponse } from '@/lib/types'

export const calculationsApi = {
  run: (params: { entity: number; period: number; name?: string; description?: string }) =>
    apiClient.post<Calculation>('/calculations/run/', params).then((r) => r.data),

  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Calculation>>('/calculations/', { params }).then((r) => r.data),

  get: (id: number) =>
    apiClient.get<Calculation>(`/calculations/${id}/`).then((r) => r.data),

  getResults: (id: number, params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<CalculationResult>>(`/calculations/${id}/results/`, { params }).then((r) => r.data),

  exportXlsx: (entityId?: number, periodId?: number) => {
    const body: Record<string, number> = {}
    if (entityId) body.entity = entityId
    if (periodId) body.period = periodId
    return apiClient
      .post('/exports/xlsx/', body, { responseType: 'blob' })
      .then((r) => {
        const url = window.URL.createObjectURL(new Blob([r.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }))
        const a = document.createElement('a')
        a.href = url
        a.download = `indicadores-${entityId ?? 'todas'}-${periodId ?? 'todos'}.xlsx`
        a.click()
        window.URL.revokeObjectURL(url)
      })
  },
}
```

---

### Fase 4: Frontend — Componentes (Groups)

#### Tarea 4.1: Reescribir `groups-client.tsx`

Campos correctos del formulario:
- `name` (input, requerido)
- `group_type` (select: fundamental / limite / otro, requerido)
- `order` (input number, default 0)
- `is_active` (checkbox, default true)

Columnas de la tabla:
- `name`
- `group_type` (badge: fundamental=azul, limite=ámbar, otro=gris)
- `order`
- `is_active` (badge sí/no)
- `actions`

---

### Fase 5: Frontend — Componentes (Indicators)

#### Tarea 5.1: Reescribir `indicators-client.tsx`

Campos correctos del formulario:
- `indicator` (input, requerido — es el código tipo `VENTAS_TOT`)
- `name` (input, requerido)
- `unit` (select: MP / U / p / peso / Coef, requerido)
- `group` (select de grupos activos, requerido)
- `description` (textarea, opcional)
- `is_active` (checkbox, default true)

Columnas de la tabla:
- `indicator` (código)
- `name`
- `unit` (badge)
- `group_name` (usando `row.original.group_name`)
- `is_active`
- `actions`

Eliminar `formula` del schema y del formulario — no existe en backend.

#### Tarea 5.2: Crear página de detalle de indicador

**Archivos**:
- `app/dashboard/indicators/[indicatorId]/page.tsx`
- `features/indicators/components/indicator-detail-client.tsx`

Contenido:
- Mostrar datos del indicador: `indicator` (código), `name`, `unit`, `group_name`, `description`, `is_active`
- Tabla de variables asociadas (del array `variables`)
  - Columnas: `name`, `label`, `description`, `is_active`
  - Permitir crear/editar/eliminar variables inline
- Botón "Volver" a lista

---

### Fase 6: Frontend — Componentes (Variables)

#### Tarea 6.1: Reescribir `variables-client.tsx`

Campos correctos del formulario:
- `indicator` (select de indicadores activos, requerido)
- `name` (input, requerido — nombre interno tipo `plan_anual`)
- `label` (input, requerido — etiqueta legible tipo "Plan Anual")
- `description` (textarea, opcional)
- `is_active` (checkbox, default true)

Columnas de la tabla:
- `indicator` → mostrar código del indicador
- `name`
- `label`
- `is_active`
- `actions`

Usar serverPagination con `{ page: page + 1 }`.

---

### Fase 7: Frontend — Componentes (Records)

#### Tarea 7.1: Reescribir `records-client.tsx`

Columnas correctas:
- `indicator_code` (de `row.original.indicator_code`)
- `entity_code` (de `row.original.entity_code`)
- `period_display` (de `row.original.period_display`)
- `variable_name`
- `value` (font-mono)
- `source_display` (badge: Manual=azul, Imported=verde, Calculated=ámbar)

Filtros actualizar:
- Entity select → usa `entity` (ID) → backend filtra por `entity`
- Indicator select → usa `indicator` (ID) → backend filtra por `indicator`
- Period select → usa `period` (ID) → backend filtra por `period`
- **NUEVO**: Variable name select (o input) → backend filtra por `variable_name`
- **NUEVO**: Group filter → backend filtra por `group` (indicator__group_id)

---

### Fase 8: Frontend — Componentes (Cálculos)

#### Tarea 8.1: Reescribir `calc-run-client.tsx`

Formulario correcto:
- `entity` (select, requerido)
- `period` (select, requerido)
- `name` (input, opcional — default autogenerado)
- `description` (textarea, opcional)

Sacar `calc_type`.

Mostrar resultado de la ejecución: status, `porcentaje_r_p`, `real_aa`, `estimado_prox_mes` de los results.

#### Tarea 8.2: Reescribir `calc-results-client.tsx`

Cambiar a listado de `Calculation` (cabeceras):
- Columnas: `id`, `name`, `period_display`, `status` (badge), `executed_by_email`, `started_at`, `finished_at`, `created_at`
- Server-side pagination
- Filtro por periodo
- Acción: "Ver resultados" → navega a detalle (nueva página)
- Acción: "Exportar XLSX" → llama a `calculationsApi.exportXlsx()`

#### Tarea 8.3: Crear página de detalle de cálculo

**Archivos**:
- `app/dashboard/calculations/[calculationId]/page.tsx`
- `app/dashboard/calculations/[calculationId]/results/page.tsx` (opcional, o incluir resultados en misma página)
- `features/calculations/components/calculation-detail-client.tsx`

Contenido:
- Resumen del `Calculation`: name, description, period, status, executed_by, started_at, finished_at
- Tabla de `CalculationResult` paginada:
  - Columnas: `entity_code`, `indicator_code`, `variable_name`, `value`
  - Filtros: entity, indicator, variable_name
  - Botón "Exportar" que llama al endpoint de exportación

---

### Fase 9: Frontend — Sidebar y rutas

#### Tarea 9.1: Actualizar sidebar y dashboard-shell

No requiere cambios — las rutas de indicadores ya están en el sidebar.

Agregar ruta de detalle de cálculo si no existe:
```
'/dashboard/calculations/[id]': 'Detalle de cálculo'
```

---

### Fase 10: Verificación

- Correr tests del backend: `python manage.py test apps.indicators apps.calculations -v 2 --keepdb`
- Build frontend: `pnpm build`

---

## Orden de implementación

```
Fase 1 (Backend):
  1.1  GET /api/calculations/ — CalculationListContractAPIView + urls.py

Fase 2 (Frontend Types):
  2.1  IndicatorGroup
  2.2  IndicatorVariable (renombrar)
  2.3  Indicator
  2.4  IndicatorRecord
  2.5  Calculation + CalculationResult (eliminar CalcType/CalcResult)

Fase 3 (Frontend API):
  3.1  indicators/api.ts — variablesApi.params, sacar bulkCreate
  3.2  calculations/api.ts — endpoints correctos

Fase 4 (Frontend Components — Groups):
  4.1  groups-client.tsx — group_type, order, is_active

Fase 5 (Frontend Components — Indicators):
  5.1  indicators-client.tsx — unit, indicator (code), sin formula
  5.2  indicator-detail-client.tsx + page

Fase 6 (Frontend Components — Variables):
  6.1  variables-client.tsx — indicator FK, label, sin code/type

Fase 7 (Frontend Components — Records):
  7.1  records-client.tsx — columnas reales, filtros

Fase 8 (Frontend Components — Cálculos):
  8.1  calc-run-client.tsx — sin calc_type
  8.2  calc-results-client.tsx — listado de cálculos
  8.3  calculation-detail-client.tsx + page (detalle + results + export)

Fase 9 (Sidebar):
  9.1  dashboard-shell.tsx — ruta de detalle

Fase 10 (Verificación):
  10.1 Tests backend + build frontend
```

---

## Notas adicionales

- El backend NO tiene endpoint para crear IndicatorRecords manualmente. La decisión es deliberada: los records se crean vía Ingestion (importación Excel) o vía Cálculos. Si en el futuro se necesita crear records manuales, se agrega un endpoint POST a `/api/indicators/records/`.
- `recorded_at` no existe en backend — se usa `created_at` en su lugar.
- El backend retorna `indicator` (código) y `name` como campos separados en `Indicator`. El frontend debe usar `indicator` como código único.
- `Calculation` no tiene `calc_type`. Si se necesita clasificar cálculos (full/partial/projection), hay que agregar el campo al modelo. Decisión postergada.
