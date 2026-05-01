# Django Admin — Plan de acción e iteración por componentes atómicos (GitHub Issues)

Este documento define la iteración para habilitar un **Django Admin operativo, seguro y mantenible** en todas las apps del backend.

Objetivo principal: permitir gestión de datos desde `/admin/` con buena UX operativa, trazabilidad y bajo riesgo.

---

## Decisiones de implementación

- Implementar en fases **P0 → P1 → P2**.
- Priorizar primero **operatividad y seguridad** (P0), luego ergonomía (P1), luego performance/permisos finos (P2).
- Mantener cambios acotados por app para facilitar revisión y rollback.
- Evitar edición manual en modelos de auditoría (solo lectura donde aplique).

---

## ADM1 — Bootstrap de registro admin por app (P0)

## 🎯 Objetivo
Dejar todos los modelos principales visibles en `/admin/` para gestión mínima.

## 📍 Alcance
- Registrar modelos en:
  - `apps/accounts/admin.py`
  - `apps/catalog/admin.py`
  - `apps/budget/admin.py`
  - `apps/indicators/admin.py`
  - `apps/ingestion/admin.py`
  - `apps/calculations/admin.py`
  - `apps/reports/admin.py`

## ✅ Criterios de aceptación
- Todos los modelos clave aparecen en `/admin/`.
- `python manage.py check` en verde.

---

## ADM2 — Accounts admin seguro y usable (P0)

## 🎯 Objetivo
Administrar usuarios/roles con seguridad y trazabilidad.

## 📍 Alcance
- `CustomUserAdmin` heredando de `UserAdmin`.
- Registrar `Role`, `UserRole`, `BlockedIP`, `LoginAttempt`.
- Configurar por modelo:
  - `list_display`, `search_fields`, `list_filter`, `ordering`, `readonly_fields`.
- `LoginAttempt` en modo solo lectura (sin add/change/delete).

## 📂 Archivos
- `backend/tesis/apps/accounts/admin.py`

## ✅ Criterios de aceptación
- Alta/edición de usuarios y roles desde admin.
- Auditoría de intentos de login solo lectura.

---

## ADM3 — Catálogo y presupuesto administrables (P0/P1)

## 🎯 Objetivo
Gestionar maestros y presupuesto sin fricción.

## 📍 Alcance
- `Entity` y `Period` con filtros, búsqueda y orden.
- `Budget` y `BudgetItem` con filtros y relaciones claras.
- (P1) inline de `BudgetItem` en `Budget` si mejora operación.

## 📂 Archivos
- `backend/tesis/apps/catalog/admin.py`
- `backend/tesis/apps/budget/admin.py`

## ✅ Criterios de aceptación
- Operaciones CRUD de catálogo y budget desde admin.
- Búsqueda por código/nombre funcional.

---

## ADM4 — Indicators admin orientado a volumen (P0/P2)

## 🎯 Objetivo
Hacer utilizable la administración de indicadores y records con datasets crecientes.

## 📍 Alcance
- Registrar `IndicatorGroup`, `Indicator`, `IndicatorVariable`, `IndicatorRecord`.
- Configurar `list_filter` fuertes y `search_fields` por códigos/nombres.
- Agregar `autocomplete_fields` en FKs pesadas.
- (P2) optimizar queryset con `list_select_related`/`get_queryset`.

## 📂 Archivos
- `backend/tesis/apps/indicators/admin.py`

## ✅ Criterios de aceptación
- Navegación fluida en listados frecuentes.
- Filtros de records reducen dataset correctamente.

---

## ADM5 — Ingestion admin para auditoría operativa (P0)

## 🎯 Objetivo
Monitorear importaciones sin permitir alteraciones peligrosas.

## 📍 Alcance
- Registrar `Document`, `ImportJob`, `DocumentDetail`.
- Exponer progreso (`status`, `total_rows`, `processed_rows`, `error_rows`).
- `DocumentDetail` en modo lectura para preservar trazabilidad.

## 📂 Archivos
- `backend/tesis/apps/ingestion/admin.py`

## ✅ Criterios de aceptación
- Se puede auditar un flujo de importación completo desde admin.
- No hay edición manual de evidencias de importación.

---

## ADM6 — Calculations y Reports en modo controlado (P0)

## 🎯 Objetivo
Permitir inspección y gestión de corrida/reportes con foco en consistencia.

## 📍 Alcance
- Registrar `Calculation`, `CalculationResult`, `Report`, `EntityClassification`.
- Marcar campos sensibles/auditables como `readonly_fields`.
- Para JSON grandes (`summary/detail/metadata/criteria_snapshot`), priorizar lectura segura.

## 📂 Archivos
- `backend/tesis/apps/calculations/admin.py`
- `backend/tesis/apps/reports/admin.py`

## ✅ Criterios de aceptación
- Se puede inspeccionar detalle de cálculo/reporte desde admin.
- No se modifica accidentalmente metadata crítica.

---

## ADM7 — Ergonomía de operación (P1)

## 🎯 Objetivo
Reducir clics y tiempo de gestión administrativa.

## 📍 Alcance
- Incorporar `inlines` donde aporte valor:
  - `BudgetItem` en `Budget`
  - `IndicatorVariable` en `Indicator`
  - `UserRole` en `CustomUser` o `Role`
- Usar `fieldsets` para pantallas largas (usuarios/reportes).
- Estandarizar orden y columnas visibles por módulo.

## ✅ Criterios de aceptación
- Flujos comunes se completan con menos navegación.
- Forms de admin legibles y consistentes.

---

## ADM8 — Hardening final: permisos y performance (P2)

## 🎯 Objetivo
Escalar Django Admin para uso real con menor riesgo operativo.

## 📍 Alcance
- Ajustar permisos por grupos/roles administrativos.
- Acciones admin seguras (activar/desactivar, bloqueo controlado).
- Optimizar consultas de listados pesados (N+1, joins frecuentes).
- Revisar límites de edición en modelos de auditoría.

## ✅ Criterios de aceptación
- Admin estable con volumen moderado/alto.
- Acciones de alto impacto restringidas correctamente.

---

## Verificación técnica por iteración

En cada issue/ticket completar:

1. `python manage.py check`
2. `python manage.py makemigrations --check --dry-run`
3. Smoke test manual en `/admin/`:
   - list, search, filters
   - create/edit donde corresponda
   - bloqueo de edición en modelos readonly
4. Tests de apps impactadas (si existen):
   - `python manage.py test <app_name> -v 2`

---

## Orden recomendado de ejecución

`ADM1 → ADM2 → ADM3 → ADM4 → ADM5 → ADM6 → ADM7 → ADM8`

---

## Protocolo de checkpoints contigo

Para evitar desalineación, validamos en checkpoints:

1. **Checkpoint A (ADM1–ADM2):** estructura base + seguridad en accounts.
2. **Checkpoint B (ADM3–ADM5):** operatividad de catálogo/ingesta/indicadores.
3. **Checkpoint C (ADM6–ADM7):** reports/calculations + ergonomía (inlines/fieldsets).
4. **Checkpoint D (ADM8):** permisos finos, performance y cierre técnico.

No pasamos al siguiente checkpoint sin tu OK.
