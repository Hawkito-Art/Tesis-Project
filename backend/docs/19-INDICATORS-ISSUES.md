# Indicators — Tickets atómicos (GitHub Issues)

Este documento define la siguiente iteración recomendada para el proyecto: cerrar el módulo `indicators` como base de catálogos, variables estándar y consulta de registros para reportes.

---

## Issue 1 — IND1: Contrato API del módulo Indicators

## 🎯 Objetivo
Definir endpoints y respuestas esperadas para grupos, indicadores, variables y registros.

## 📍 Alcance
- Definir contrato de:
  - `GET/POST /api/indicators/groups/`
  - `GET/PATCH/DELETE /api/indicators/groups/{id}/`
  - `GET/POST /api/indicators/`
  - `GET/PATCH/DELETE /api/indicators/{id}/`
  - `GET/POST /api/indicators/variables/`
  - `GET/PATCH/DELETE /api/indicators/variables/{id}/`
  - `GET /api/indicators/records/` (filtros)
- Documentar status codes y payloads.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md`
- `backend/tesis/apps/indicators/urls.py`

## ✅ Criterios de aceptación
- Contrato alineado entre docs y rutas reales.

---

## Issue 2 — IND2: Seed de grupos base de indicadores

## 🎯 Objetivo
Crear los 3 grupos canónicos del dominio.

## 📍 Alcance
- Crear data migration o management command para:
  - `fundamental` (order=1)
  - `limite` (order=2)
  - `otro` (order=3)

## 📂 Archivos
- `backend/tesis/apps/indicators/migrations/*`
- opcional: `backend/tesis/apps/indicators/management/commands/*`

## ✅ Criterios de aceptación
- Los 3 grupos existen y no se duplican al re-ejecutar.

---

## Issue 3 — IND3: Seed de 13 indicadores con unidad y grupo

## 🎯 Objetivo
Poblar catálogo base de indicadores del Excel de referencia.

## 📍 Alcance
- Crear indicadores con `indicator` (código), `name`, `unit`, `group`.
- Asignar grupo correcto según `docs/6-APP-INDICATORS.md`.

## 📂 Archivos
- `backend/tesis/apps/indicators/migrations/*`

## ✅ Criterios de aceptación
- 13 indicadores activos, sin duplicados de código.

---

## Issue 4 — IND4: Seed de variables estándar por indicador

## 🎯 Objetivo
Asegurar las 8 variables estándar para cada indicador.

## 📍 Alcance
Crear para cada indicador:
- `plan_anual`
- `ano_anterior`
- `plan_acumulado`
- `real_acumulado`
- `porcentaje_r_p`
- `real_aa`
- `estimado_prox_mes`
- `estimado_cierre_ano`

## 📂 Archivos
- `backend/tesis/apps/indicators/migrations/*`

## ✅ Criterios de aceptación
- Cada indicador tiene las 8 variables activas.

---

## Issue 5 — IND5: Endpoints CRUD para IndicatorGroup

## 🎯 Objetivo
Habilitar gestión API de grupos de indicadores.

## 📍 Alcance
- ViewSet/APIView para listar, crear, editar y eliminar grupos.
- Permisos según política del proyecto.

## 📂 Archivos
- `backend/tesis/apps/indicators/views.py`
- `backend/tesis/apps/indicators/urls.py`
- `backend/tesis/apps/indicators/permissions.py`

## ✅ Criterios de aceptación
- CRUD operativo con respuestas DRF consistentes.

---

## Issue 6 — IND6: Endpoints CRUD para Indicator

## 🎯 Objetivo
Habilitar administración del catálogo de indicadores.

## 📍 Alcance
- CRUD de indicadores con validación de `unit`, `group`, `is_active`.
- Búsqueda por `indicator` y `name`.

## 📂 Archivos
- `backend/tesis/apps/indicators/views.py`
- `backend/tesis/apps/indicators/urls.py`

## ✅ Criterios de aceptación
- Alta/edición/baja lógica funcional con validaciones.

---

## Issue 7 — IND7: Endpoints CRUD para IndicatorVariable

## 🎯 Objetivo
Habilitar administración de variables por indicador.

## 📍 Alcance
- CRUD de variables.
- Validar unicidad `(indicator, name)`.

## 📂 Archivos
- `backend/tesis/apps/indicators/views.py`
- `backend/tesis/apps/indicators/urls.py`

## ✅ Criterios de aceptación
- No se permiten variables duplicadas por indicador.

---

## Issue 8 — IND8: Endpoint de consulta `indicator-records` con filtros compuestos

## 🎯 Objetivo
Exponer consulta analítica de registros de indicadores.

## 📍 Alcance
- `GET /api/indicators/records/` con filtros:
  - `entity`
  - `indicator`
  - `group`
  - `period`
  - `variable_name`
- Orden y paginación.

## 📂 Archivos
- `backend/tesis/apps/indicators/views.py`
- `backend/tesis/apps/indicators/urls.py`
- `backend/tesis/apps/indicators/serializers.py`

## ✅ Criterios de aceptación
- Filtros combinables y respuesta paginada consistente.

---

## Issue 9 — IND9: Validación de correspondencia variable ↔ indicador

## 🎯 Objetivo
Evitar registros inválidos cuando `variable_name` no pertenece al indicador.

## 📍 Alcance
- Reforzar validación de serializer/servicio para `IndicatorRecord`.
- Mensajes de error claros.

## 📂 Archivos
- `backend/tesis/apps/indicators/serializers.py`
- `backend/tesis/apps/indicators/services.py` (si aplica)

## ✅ Criterios de aceptación
- Cualquier mismatch variable/indicador devuelve 400 con detalle.

---

## Issue 10 — IND10: Trazabilidad de origen en registros

## 🎯 Objetivo
Preservar origen de datos (`manual/imported/calculated`) y referencia de carga/cálculo.

## 📍 Alcance
- Validar que `IndicatorRecord` mantenga trazabilidad usada por ingestion/calculations.
- Completar serializers de lectura para exponer campos de auditoría relevantes.

## 📂 Archivos
- `backend/tesis/apps/indicators/models.py`
- `backend/tesis/apps/indicators/serializers.py`

## ✅ Criterios de aceptación
- Origen y vínculos de trazabilidad disponibles en consultas.

---

## Issue 11 — IND11: Tests API y servicios del módulo Indicators

## 🎯 Objetivo
Cubrir comportamiento funcional y reglas del módulo.

## 📍 Alcance
Casos mínimos:
- CRUD grupos/indicadores/variables
- unicidad de variables por indicador
- filtros de `indicator-records`
- validación variable↔indicador
- permisos 401/403

## 📂 Archivos
- `backend/tesis/apps/indicators/tests/test_api.py`
- `backend/tesis/apps/indicators/tests/test_serializers.py`
- `backend/tesis/apps/indicators/tests/test_filters.py`

## ✅ Criterios de aceptación
- `python manage.py test apps.indicators -v 2` en verde.

---

## Issue 12 — IND12: Verificación final de iteración Indicators

## 🎯 Objetivo
Cerrar técnicamente la iteración.

## 📍 Alcance
Ejecutar:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.indicators -v 2`

## ✅ Criterios de aceptación
- Sin issues, sin migraciones pendientes y tests en verde.

---

## Orden recomendado

`IND1 → IND2 → IND3 → IND4 → IND5 → IND6 → IND7 → IND8 → IND9 → IND10 → IND11 → IND12`
