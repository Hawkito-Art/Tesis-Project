# Spec: Integración completa del módulo Cálculos

## Resumen

Completar la integración frontend-backend del módulo de Cálculos. Actualmente el módulo tiene la estructura base implementada pero con varios gaps funcionales: filtros que no funcionan, columnas faltantes, auto-refresh ausente, y páginas que no existen.

---

## Gap Analysis

### Backend

| # | Endpoint | Problema | Severidad |
|---|----------|----------|-----------|
| B1 | `GET /api/calculations/` | No filtra por `period` — el view `CalculationListContractAPIView` ignora `request.query_params` | ALTO |
| B2 | `GET /api/calculations/` | No soporta filtro por `status` | MEDIO |
| B3 | `GET /api/calculations/` | No soporta `search` (por name) ni `ordering` | BAJO |

### Frontend — API layer (`features/calculations/api.ts`)

Sin gaps — los endpoints son correctos:
- `run()` → `POST /calculations/run/` ✅
- `list()` → `GET /calculations/?page=` ✅
- `get()` → `GET /calculations/{id}/` ✅
- `getResults()` → `GET /calculations/{id}/results/` ✅
- `exportXlsx()` → `POST /exports/xlsx/` ✅

### Frontend — Componentes/UI

| # | Componente | Problema | Severidad |
|---|-----------|----------|-----------|
| F1 | `calc-results-client.tsx` | Filtro `period` no funciona porque backend (B1) lo ignora | ALTO |
| F2 | `calc-results-client.tsx` | Falta columna `finished_at` en la tabla | MEDIO |
| F3 | `calculation-detail-client.tsx` | Tabla de resultados no tiene filtros entity/indicator/variable_name que backend soporta | ALTO |
| F4 | `calculation-detail-client.tsx` | No hay auto-refetch para cálculos en estado `en_progreso` | MEDIO |
| F5 | `calc-run-client.tsx` | Error toast no muestra detalle del backend | BAJO |
| F6 | `calc-run-client.tsx` | Después de ejecutar, no invalida query de listado de cálculos | BAJO |

### Frontend — Rutas/páginas

| # | Ruta | Problema | Severidad |
|---|------|----------|-----------|
| R1 | `/dashboard/calculations` | No existe `page.tsx` — navegar ahí da 404 | MEDIO |

### Frontend — Sidebar

Sin gaps — sidebar tiene "Ejecutar" y "Resultados" correctamente. ✅

---

## Tareas de implementación

### Fase 1: Backend — Soportar filtros en `GET /api/calculations/`

#### Tarea 1.1: Agregar filtro por `period`

**Archivo**: `backend/tesis/apps/calculations/views.py`

En `CalculationListContractAPIView.get()`, extraer `period` de `request.query_params` y filtrar:

```python
def get(self, request):
    queryset = Calculation.objects.select_related('period', 'executed_by').order_by('-created_at')

    period = request.query_params.get('period')
    if period:
        queryset = queryset.filter(period_id=period)

    page = self.paginator.paginate_queryset(queryset, request, view=self)
    ...
```

#### Tarea 1.2: Agregar filtro por `status`

Mismo archivo, mismo método:

```python
status = request.query_params.get('status')
if status:
    queryset = queryset.filter(status=status)
```

#### Tarea 1.3: Agregar search por `name` y ordering

Mismo archivo, mismo método:

```python
search = request.query_params.get('search')
if search:
    queryset = queryset.filter(name__icontains=search)

ordering = request.query_params.get('ordering')
if ordering in ('created_at', '-created_at', 'name', '-name', 'status', '-status', 'started_at', '-started_at'):
    queryset = queryset.order_by(ordering)
```

---

### Fase 2: Frontend — `calc-results-client.tsx` (listado)

#### Tarea 2.1: Agregar columna `finished_at`

Entre `started_at` y `created_at`:

```typescript
{
  accessorKey: 'finished_at',
  header: 'Finalizado',
  cell: ({ row }) => row.original.finished_at ? format(new Date(row.original.finished_at), "dd/MM/yyyy HH:mm", { locale: es }) : '—',
},
```

#### Tarea 2.2: Agregar filtro por `status`

Select con opciones: Todos, Pendiente, Procesando, Completado, Error.

Junto al filtro de período:

```typescript
const [statusFilter, setStatusFilter] = useState('all')
```

Enviar a backend:
```typescript
status: statusFilter === 'all' ? undefined : statusFilter,
```

---

### Fase 3: Frontend — `calculation-detail-client.tsx` (detalle)

#### Tarea 3.1: Agregar filtros a la tabla de resultados

Filtros sobre la tabla de `CalculationResult`:

- **Entity**: select con entidades (fetch via `entitiesApi.list()`)
- **Indicator**: select con indicadores (fetch via `indicatorsApi.list()`)
- **Variable**: select con variables estándar

Estados:
```typescript
const [entityFilter, setEntityFilter] = useState('all')
const [indicatorFilter, setIndicatorFilter] = useState('all')
const [variableFilter, setVariableFilter] = useState('all')
```

Query params:
```typescript
calculationsApi.getResults(Number(calculationId), {
  page: page + 1,
  page_size: 10,
  entity: entityFilter === 'all' ? undefined : entityFilter,
  indicator: indicatorFilter === 'all' ? undefined : indicatorFilter,
  variable_name: variableFilter === 'all' ? undefined : variableFilter,
})
```

Layout: barra de filtros horizontal arriba del DataTable, estilo consistente con `records-client.tsx`.

#### Tarea 3.2: Auto-refresh para cálculos en progreso

Cuando `calc.status === 'en_progreso'`, configurar `refetchInterval: 5000` en la query de detalle para polling automático:

```typescript
const { data: calc, isLoading: calcLoading } = useQuery({
  queryKey: ['calculation', calculationId],
  queryFn: () => calculationsApi.get(Number(calculationId)),
  refetchInterval: (query) => {
    const data = query.state.data
    if (data?.status === 'en_progreso' || data?.status === 'pendiente') return 5000
    return false
  },
})
```

Lo mismo para la query de resultados.

---

### Fase 4: Frontend — `calc-run-client.tsx` (ejecución)

#### Tarea 4.1: Mejorar feedback de error

Mostrar detalle del error del backend:

```typescript
onError: (error) => {
  const detail = (error as { response?: { data?: { error?: { detail?: string } } } })?.response?.data?.error?.detail
  toast.error(detail || 'Error al ejecutar el cálculo')
},
```

#### Tarea 4.2: Invalidar query de listado tras ejecución

Después de ejecutar exitosamente, invalidar la query `['calculations']` para que el listado se refresque:

```typescript
import { useQueryClient } from '@tanstack/react-query'
const qc = useQueryClient()
// en onSuccess:
qc.invalidateQueries({ queryKey: ['calculations'] })
```

---

### Fase 5: Frontend — Ruta `/dashboard/calculations/`

#### Tarea 5.1: Crear `app/dashboard/calculations/page.tsx`

Página índice que redirige a `/dashboard/calculations/results`:

```typescript
import { redirect } from 'next/navigation'

export default function CalculationsPage() {
  redirect('/dashboard/calculations/results')
}
```

---

### Fase 6: Frontend — Agregar `results` al type `Calculation`

#### Tarea 6.1: Actualizar `lib/types.ts`

Agregar `results` opcional al type `Calculation` ya que el backend lo retorna embebido en `GET /api/calculations/{id}/`:

```typescript
export interface Calculation {
  ...
  results?: CalculationResult[]
}
```

---

### Fase 7: Verificación

#### Tarea 7.1: Tests backend

```bash
python manage.py test apps.calculations -v 2 --keepdb
```

Verificar que tests existentes sigan pasando (24 tests).

#### Tarea 7.2: Build frontend

```bash
pnpm build
```

Verificar que compile sin errores.

---

## Orden de implementación

```
Fase 1 (Backend):
  1.1  Filtro period en CalculationListContractAPIView
  1.2  Filtro status
  1.3  Search y ordering

Fase 2 (Frontend — calc-results-client):
  2.1  Columna finished_at
  2.2  Filtro status

Fase 3 (Frontend — calculation-detail-client):
  3.1  Filtros entity/indicator/variable en resultados
  3.2  Auto-refresh para cálculos en progreso

Fase 4 (Frontend — calc-run-client):
  4.1  Error detail en toast
  4.2  Invalidar listado tras ejecución

Fase 5 (Frontend — ruta index):
  5.1  Crear page.tsx con redirect

Fase 6 (Frontend — types):
  6.1  Agregar results opcional a Calculation

Fase 7 (Verificación):
  7.1  Tests backend
  7.2  Build frontend
```

---

## Notas adicionales

- El backend ya soporta filtros `entity`, `indicator`, `variable_name` y `ordering` en `GET /api/calculations/{pk}/results/` via `CalculationResultListQuerySerializer`. Solo falta exponerlos en UI.
- `period` en `GET /api/calculations/` se filtra por `period_id` (PK de Period).
- `status` acepta: `pendiente`, `en_progreso`, `completado`, `error`.
- El auto-refresh cada 5 segundos solo aplica mientras el cálculo está en `en_progreso` o `pendiente`. Una vez que cambia a `completado` o `error`, el polling se detiene automáticamente.
- No se implementa DELETE de cálculos — el backend no expone ese endpoint y no está en alcance.
- No se implementa edición inline de resultados — los resultados son read-only, generados por el motor de cálculo.
