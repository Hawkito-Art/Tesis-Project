# Spec: Integración completa del módulo Ingestion

## Resumen

Integrar el pipeline completo de ingesta de datos entre frontend y backend:
subida de archivo Excel → procesamiento → visualización de resultados.
Actualmente el módulo está funcionalmente roto: frontend y backend nunca se conectaron.

---

## Gap Analysis

| # | Problema | Archivos afectados | Severidad |
|---|----------|-------------------|-----------|
| 1 | Frontend POSTea a `/ingestion/upload/` pero backend expone en `POST /ingestion/documents/` y payload no coincide | `api.ts`, `upload-client.tsx`, backend views | CRÍTICO |
| 2 | Frontend GETea a `/ingestion/jobs/` pero backend NO tiene listado de ImportJobs | `api.ts`, `jobs-client.tsx`, backend | CRÍTICO |
| 3 | Frontend POSTea a `/ingestion/jobs/<id>/retry/` pero backend NO tiene retry | `api.ts`, `jobs-client.tsx`, backend | CRÍTICO |
| 4 | Frontend nunca llama a `POST /ingestion/import-jobs/<pk>/` para procesar el Excel | Falta flujo completo de procesamiento | CRÍTICO |
| 5 | Frontend nunca llama a `GET /ingestion/import-jobs/<pk>/details/` para ver errores por fila | Falta UI de detalle | ALTO |
| 6 | `ImportJob` type desalineado: frontend espera `filename`, `import_type`; backend retorna `document_name`, `total_rows`, etc. | `types.ts` | ALTO |
| 7 | Upload payload: frontend envía `import_type`/`entity`/`period` que backend ignora, y NO envía `name` que backend requiere | `upload-client.tsx` | ALTO |
| 8 | `Document.status` nunca se actualiza después de creado | `services.py` | BAJO |

---

## Tareas de implementación

### Tarea 1: Backend — Agregar endpoint `GET /api/ingestion/import-jobs/`

**Archivo**: `backend/tesis/apps/ingestion/views.py`

Nueva clase `ImportJobListContractAPIView`:
- `GET` → listado paginado de ImportJobs, ordenado por `-created_at`
- `select_related('document')` para evitar N+1
- Permission: `IsAuthenticated, IngestionPermission`
- Serializer: `ImportJobListSerializer` (sin details anidados para eficiencia)

**Archivo**: `backend/tesis/apps/ingestion/serializers.py`

Nuevo serializer `ImportJobListSerializer`:
- Mismos campos que `ImportJobSerializer` PERO sin `details` (evita N+1 masivo)
- Agregar `document_name` (source=document.name)

**Archivo**: `backend/tesis/apps/ingestion/urls.py`

Agregar ruta:
```python
path('import-jobs/', ImportJobListContractAPIView.as_view(), name='import-job-list'),
```

---

### Tarea 2: Backend — Agregar endpoint `POST /api/ingestion/import-jobs/<pk>/retry/`

**Archivo**: `backend/tesis/apps/ingestion/views.py`

Nueva clase `ImportJobRetryContractAPIView`:
- `POST` → resetea el ImportJob a estado `pendiente`, borra DocumentDetails, borra IndicatorRecords asociados
- Permission: `IsAuthenticated, IngestionPermission`

**Archivo**: `backend/tesis/apps/ingestion/urls.py`

Agregar ruta:
```python
path('import-jobs/<int:pk>/retry/', ImportJobRetryContractAPIView.as_view(), name='import-job-retry'),
```

---

### Tarea 3: Backend — Actualizar `Document.status` durante procesamiento

**Archivo**: `backend/tesis/apps/ingestion/services.py`

En `process_import_job_partial()`:
- Al inicio: `document.status = 'procesado'`
- En el `transaction.atomic()`: actualizar también `document.save(update_fields=['status'])`

---

### Tarea 4: Frontend — Corregir `ImportJob` type

**Archivo**: `lib/types.ts`

```typescript
export type ImportJobStatus = 'pendiente' | 'en_progreso' | 'completado' | 'error'

export interface ImportJob {
  id: number
  document: number
  document_name: string
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
```

---

### Tarea 5: Frontend — Reescribir `api.ts`

**Archivo**: `features/ingestion/api.ts`

```typescript
import apiClient from '@/lib/axios'
import type { ImportJob, ImportJobDetail, PaginatedResponse } from '@/lib/types'

export const ingestionApi = {
  upload: (name: string, file: File) => {
    const form = new FormData()
    form.append('name', name)
    form.append('file', file)
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
```

---

### Tarea 6: Frontend — Reescribir `upload-client.tsx`

**Archivo**: `features/ingestion/components/upload-client.tsx`

Cambios:
- Sacar campos `import_type`, `entity`, `period` del formulario
- El upload solo recibe archivo → el backend genera el `name` desde el filename
- Después del upload exitoso, redirigir a `/dashboard/ingestion/jobs`

Flujo simplificado:
1. Seleccionar archivo Excel
2. Click "Cargar archivo"
3. POST a `/ingestion/documents/` con `name` (del filename) + `file`
4. Redirigir a jobs

---

### Tarea 7: Frontend — Reescribir `jobs-client.tsx`

**Archivo**: `features/ingestion/components/jobs-client.tsx`

Cambios:
- Columnas: `id`, `document_name` (filename), `status` (con badge), `total_rows`, `processed_rows`, `error_rows`, `created_at`
- Status labels: `pendiente`, `en_progreso`, `completado`, `error`
- Acciones:
  - Si status es `pendiente`: botón "Procesar" → abre un dialog para seleccionar entity + period → POST a `/ingestion/import-jobs/<id>/`
  - Si status es `error`: botón "Reintentar" → POST a `/ingestion/import-jobs/<id>/retry/`
  - Si status es `completado` o `en_progreso`: enlace a detalle (o botón "Ver detalles")
- Polling automático cada 10 segundos para jobs en progreso

---

### Tarea 8: Frontend — Crear página de detalle de import job

**Archivos nuevos**:
- `app/dashboard/ingestion/jobs/[jobId]/page.tsx`
- `features/ingestion/components/job-detail-client.tsx`

Página de detalle de un ImportJob:
- Muestra: `document_name`, `status`, `total_rows`, `processed_rows`, `error_rows`, `started_at`, `finished_at`
- Tabla paginada de `DocumentDetail` (vía `GET /ingestion/import-jobs/<pk>/details/`)
- Columnas: `row_number`, `indicator_name` (de raw_data), `is_valid` (badge), `error_message`
- Filtro: solo mostrar errores (is_valid=false) opcionalmente

---

### Tarea 9: Verificación

- Correr tests del backend: `python manage.py test apps.ingestion -v 2 --keepdb`
- Build frontend: `pnpm build`

---

## Orden de implementación

```
1. Backend: ImportJobListContractAPIView (list)
2. Backend: ImportJobRetryContractAPIView (retry)
3. Backend: services.py — actualizar Document.status
4. Backend: urls.py — registrar nuevas rutas
5. Frontend: types.ts — corregir ImportJob
6. Frontend: api.ts — endpoints correctos
7. Frontend: upload-client.tsx — simplificar
8. Frontend: jobs-client.tsx — procesar + reintentar
9. Frontend: job-detail-client.tsx — detalle con errores por fila
10. Frontend: sidebar — agregar ruta a detalle si es necesario
11. Verificación: tests backend + build frontend
```

---

## Notas adicionales

- El upload solo soporta archivos `.xlsx` validados por el backend
- El procesamiento requiere entity + period (seleccionados en UI al hacer clic en "Procesar")
- El retry resetea el job a pendiente y permite volver a procesar
- Los detalles por fila muestran qué indicadores se encontraron y cuáles fallaron
- El status `en_progreso` se usa mientras se procesa el Excel (puede tardar)
- El DocumentDetail contiene `raw_data` con `indicator_name`, `raw_values`, `parsed_values`
