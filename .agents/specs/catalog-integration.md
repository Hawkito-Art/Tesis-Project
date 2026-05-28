# Spec: Integración completa del módulo Catálogo

## Resumen

Integrar full CRUD del backend de Catálogo (Entity, Period) y Directorio (Role, User)
con el frontend, alineando types, forms, API paths, y agregando funcionalidad faltante.

---

## Gap Analysis

| # | Problema | Archivos afectados | Severidad |
|---|----------|-------------------|-----------|
| 1 | `Period` type completamente desalineado (tiene `name`, `start_date`, `end_date` que no existen) | `types.ts`, `periods-client.tsx`, `periods/page.tsx`, backend serializer | CRÍTICO |
| 2 | `rolesApi` llama a `/catalog/roles/` pero backend expone en `/api/roles/` | `api.ts` | CRÍTICO |
| 3 | `usersApi` llama a `/catalog/users/` pero backend expone en `/api/users/` | `api.ts` | CRÍTICO |
| 4 | `Entity` type incompleto (falta `type`, `is_consolidated`, `is_active`) | `types.ts`, `entities-client.tsx` | ALTO |
| 5 | Entity form no permite seleccionar `type`, marcar `is_consolidated` ni `is_active` | `entities-client.tsx` | ALTO |
| 6 | Period form no puede crear períodos (fields incorrectos) + DELETE no soportado | `periods-client.tsx`, backend `PeriodViewSet` | ALTO |
| 7 | `usersApi` envía `role`/`entity` que backend no acepta en create/update | `users-client.tsx`, backend serializers | ALTO |
| 8 | User form no maneja password + `UserDetailSerializer` no devuelve `role`/`entity` | `users-client.tsx`, backend serializers | ALTO |
| 9 | `Role` type tiene `permissions` que no existe en backend | `types.ts` | MEDIO |
| 10 | Roles form no permite editar `description` ni `is_active` | `roles-client.tsx` | MEDIO |

---

## Tareas de implementación

### Tarea 1: Backend — Agregar `name` calculado a `PeriodSerializer`

**Archivo**: `backend/tesis/apps/catalog/serializers.py`

Agregar `name` como `SerializerMethodField` que devuelva `f"{year}-{month:02d} ({period_type})"`.

Esto permite que el frontend siga usando `period.name` sin romper todas las referencias existentes en Budget, Ingestion, Indicators, etc.

```python
class PeriodSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Period
        fields = ['id', 'name', 'year', 'month', 'period_type', 'is_active', 'created_at']

    def get_name(self, obj):
        month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
        }
        month_name = month_names.get(obj.month, str(obj.month).zfill(2))
        return f'{month_name} {obj.year} ({obj.period_type})'
```

---

### Tarea 2: Backend — Agregar DELETE a `PeriodViewSet`

**Archivo**: `backend/tesis/apps/catalog/views.py`

Agregar `mixins.DestroyModelMixin`:

```python
class PeriodViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
```

---

### Tarea 3: Backend — Agregar `role` a `UserSerializer` y `entity` a read

**Archivos**: `backend/tesis/apps/accounts/serializers.py`, `backend/tesis/apps/accounts/views.py`

`UserDetailSerializer` necesita devolver `role` (string, primer rol). Agregar como `SerializerMethodField`.

`UserCreateSerializer` y `UserUpdateSerializer` necesitan aceptar `role_id` opcional para asignar rol en create/update.

---

### Tarea 4: Frontend — Corregir `types.ts`

**Archivo**: `lib/types.ts`

```typescript
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
```

---

### Tarea 5: Frontend — Corregir `api.ts` (paths de roles y users)

**Archivo**: `features/catalog/api.ts`

```typescript
// Roles
export const rolesApi = {
  list: () => apiClient.get<PaginatedResponse<Role>>('/roles/').then((r) => r.data),
  create: (data: Partial<Role>) => apiClient.post<Role>('/roles/', data).then((r) => r.data),
  update: (id: number, data: Partial<Role>) => apiClient.patch<Role>(`/roles/${id}/`, data).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/roles/${id}/`).then((r) => r.data),
}

// Users
export const usersApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<User>>('/users/', { params }).then((r) => r.data),
  get: (id: number) => apiClient.get<User>(`/users/${id}/`).then((r) => r.data),
  create: (data: UserPayload) => apiClient.post<User>('/users/', data).then((r) => r.data),
  update: (id: number, data: UserPayload) => apiClient.patch<User>(`/users/${id}/`, data).then((r) => r.data),
  remove: (id: number) => apiClient.delete(`/users/${id}/`).then((r) => r.data),
}
```

NOTA: `entitiesApi` y `periodsApi` pueden seguir apuntando a `/catalog/entities/` y `/catalog/periods/` (están duplicadas en backend y funcionan ambos paths).

---

### Tarea 6: Frontend — Rehacer `periods-client.tsx` con fields correctos

**Archivo**: `features/catalog/components/periods-client.tsx`

Reemplazar schema de form:
- Sacar `name`, `start_date`, `end_date`
- Agregar `year` (number input), `month` (Select 1-12 con nombres), `period_type` (Select: mensual/acumulado/anual), `is_active` (switch/checkbox)

Reemplazar columnas de la tabla:
- `name` → se mantiene (viene calculado del backend ahora)
- `start_date`, `end_date` → sacar, reemplazar con `year`, `month`, `period_type`

El DELETE ya funciona (Tarea 2).

---

### Tarea 7: Frontend — Completar `entities-client.tsx` con type, is_consolidated, is_active

**Archivo**: `features/catalog/components/entities-client.tsx`

Schema de form actualizado:
```typescript
const entitySchema = z.object({
  code: z.string().min(1, 'El código es requerido'),
  name: z.string().min(1, 'El nombre es requerido'),
  type: z.string().min(1, 'El tipo es requerido'),
  description: z.string().optional(),
  is_consolidated: z.boolean().default(false),
  is_active: z.boolean().default(true),
})
```

Form:
- Agregar `<Select>` para `type` (consolidado/empresa/mipyme/unidad_presupuestada)
- Agregar checkbox para `is_consolidated` (solo habilitado si type === 'consolidado')
- Agregar checkbox o switch para `is_active`

Tabla:
- Agregar columnas `type` (con badge), `is_active` (con badge Activo/Inactivo)

---

### Tarea 8: Frontend — Completar `roles-client.tsx` con description e is_active

**Archivo**: `features/catalog/components/roles-client.tsx`

Schema actualizado:
```typescript
const roleSchema = z.object({
  name: z.string().min(1, 'El nombre es requerido'),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
})
```

Form: agregar campo `description` (textarea) y switch para `is_active`.

Tabla: agregar columna `description`, cambiar badge de estado.

---

### Tarea 9: Frontend — Ajustar `users-client.tsx` al backend real

**Archivo**: `features/catalog/components/users-client.tsx`

El backend `UserCreateSerializer` acepta: `email`, `password`, `first_name`, `last_name`, `email_verified`, `is_active`, `is_staff`.

El backend `UserDetailSerializer` devuelve: `id`, `email`, `first_name`, `last_name`, `email_verified`, `is_active`, `is_staff`, `created_at`, `updated_at`.

NO tiene `role` ni `entity` como campos directos (son via `UserRole` y no existen respectivamente).

**Cambios**:
- Sacar selects de `role` y `entity` del form
- Agregar campo `password` (solo en create)
- Agregar checkbox para `is_active`
- Columnas de tabla: `email`, `name` (first + last), `is_active`, `is_staff`
- `role` columna: mostrar como `—` hasta que se implemente UserRole management

---

### Tarea 10: Frontend — Actualizar `User` type y `UserPayload`

**Archivo**: `lib/types.ts`

```typescript
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
```

---

### Tarea 11: Verificación

- Correr tests del backend: `python manage.py test apps.catalog apps.accounts -v 2 --keepdb`
- Build frontend: `pnpm build`
- Probar manualmente CRUD de Entities, Periods, Roles, Users

---

## Orden de implementación

```
1. Backend: PeriodSerializer (name calculado)        → sin dependencias
2. Backend: PeriodViewSet (agregar DELETE)            → sin dependencias
3. Backend: UserDetailSerializer (role field)         → sin dependencias
4. Frontend: types.ts (Period, Entity, Role, User)    → depende de 1
5. Frontend: api.ts (paths roles/users)               → sin dependencias
6. Frontend: periods-client.tsx (rehacer form/tabla)  → depende de 1, 2, 4
7. Frontend: entities-client.tsx (completar form)     → depende de 4
8. Frontend: roles-client.tsx (description, is_active) → depende de 4
9. Frontend: users-client.tsx (ajustar al backend)    → depende de 3, 4, 5
10. Verificación: tests backend + build frontend       → depende de todo lo anterior
```

---

## Notas adicionales

- Los types `Entity` y `Period` se usan como nested objects en otras interfaces (`Budget`, `ImportJob`, `IndicatorRecord`, `CalcResult`, `Classification`). Como son objetos anidados del API, los cambios son aditivos (nuevos campos opcionales) y no deberían romper nada.
- La duplicación de rutas `/api/entities/` y `/api/catalog/entities/` en backend NO se toca por ahora. Ambas funcionan. Si en el futuro se limpia, se decide un único namespace.
