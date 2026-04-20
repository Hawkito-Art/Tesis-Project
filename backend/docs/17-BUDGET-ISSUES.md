# Budget API — Tickets atómicos (GitHub Issues)

Este documento contiene los tickets atómicos para implementar la API del módulo `budget` en la Iteración 3.

---

## Issue 1 — B1: Cerrar contrato de API para `budgets` y `budget-items`

## 🎯 Objetivo
Definir y alinear rutas, payloads y códigos HTTP de `Budget` y `BudgetItem`.

## 📍 Alcance
- Definir endpoints:
  - `GET/POST /api/budgets/`
  - `GET/PATCH/DELETE /api/budgets/{id}/`
  - `GET/POST /api/budget-items/`
  - `GET/PATCH/DELETE /api/budget-items/{id}/`
- Alinear documentación y rutas reales.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md` (si hace falta completar)
- `backend/tesis/apps/budget/urls.py`

## ✅ Criterios de aceptación
- Endpoints definidos y sin contradicciones entre docs y código.
- Status codes documentados y consistentes.

## 🏁 Definition of Done
- Contrato de Budget explícito y listo para implementar.

---

## Issue 2 — B2: Completar modelo `Budget` con estados y reglas mínimas

## 🎯 Objetivo
Incorporar estados de presupuesto y validar consistencia de transición básica.

## 📍 Alcance
- Agregar estado en `Budget`: `draft`, `approved`, `closed`.
- Definir regla mínima: no permitir edición/eliminación inválida en `closed`.
- Mantener constraint único `(entity, period)`.

## 📂 Archivos
- `backend/tesis/apps/budget/models.py`
- `backend/tesis/apps/budget/migrations/*.py`

## ✅ Criterios de aceptación
- Estado disponible en modelo/DB.
- Restricciones mínimas aplicadas en lógica de aplicación.

## 🏁 Definition of Done
- Modelo Budget listo para el flujo de negocio básico.

---

## Issue 3 — B3: Endurecer serializers de `Budget` y `BudgetItem`

## 🎯 Objetivo
Validar montos y relaciones con mensajes claros.

## 📍 Alcance
- Mantener montos no negativos.
- Validar `entity` y `period` activos.
- Validar campos requeridos de `BudgetItem` (`code`, `name`, `item_type`).
- Validar consistencia de estado al actualizar presupuestos.

## 📂 Archivos
- `backend/tesis/apps/budget/serializers.py`

## ✅ Criterios de aceptación
- Serializers rechazan payload inválido con errores consistentes.

## 🏁 Definition of Done
- Capa de validación robusta para contrato de API.

---

## Issue 4 — B4: Implementar vistas CRUD para `Budget`

## 🎯 Objetivo
Exponer list/create/retrieve/partial_update/delete para presupuestos.

## 📍 Alcance
- Implementar vistas DRF para `Budget`.
- Manejar correctamente conflictos por presupuesto duplicado `(entity, period)`.

## 📂 Archivos
- `backend/tesis/apps/budget/views.py`

## ✅ Criterios de aceptación
- Endpoints de `Budget` funcionales.
- Errores DRF estandarizados.

## 🏁 Definition of Done
- CRUD de Budget operativo.

---

## Issue 5 — B5: Implementar vistas CRUD para `BudgetItem`

## 🎯 Objetivo
Exponer list/create/retrieve/partial_update/delete para partidas presupuestarias.

## 📍 Alcance
- Implementar vistas DRF para `BudgetItem`.
- Manejar correctamente duplicados por `(budget, item_type, code)`.

## 📂 Archivos
- `backend/tesis/apps/budget/views.py`

## ✅ Criterios de aceptación
- Endpoints de `BudgetItem` funcionales.
- Duplicados devuelven error consistente.

## 🏁 Definition of Done
- CRUD de BudgetItem operativo.

---

## Issue 6 — B6: Registrar URLs de Budget

## 🎯 Objetivo
Publicar rutas de vistas de `Budget` y `BudgetItem`.

## 📍 Alcance
- Reemplazar `urlpatterns = []` por rutas reales.
- Mantener coherencia con contrato de B1.

## 📂 Archivos
- `backend/tesis/apps/budget/urls.py`

## ✅ Criterios de aceptación
- Todas las rutas del módulo Budget responden correctamente.

## 🏁 Definition of Done
- Módulo Budget enrutable desde `api/budget/`.

---

## Issue 7 — B7: Permisos por endpoint (lectura autenticados, escritura admin)

## 🎯 Objetivo
Aplicar matriz de permisos del módulo Budget.

## 📍 Alcance
- Lectura para autenticados autorizados.
- Escritura para admin.
- Respuestas 401/403 consistentes.

## 📂 Archivos
- `backend/tesis/apps/budget/views.py`
- `backend/tesis/apps/budget/permissions.py` (si hace falta crear)

## ✅ Criterios de aceptación
- No hay endpoints de escritura expuestos a usuarios sin privilegios.

## 🏁 Definition of Done
- Permisos de Budget implementados y testeados.

---

## Issue 8 — B8: Filtros, orden y paginación en listados

## 🎯 Objetivo
Agregar capacidad de consulta escalable en presupuestos y partidas.

## 📍 Alcance
- Filtros `Budget`: `entity`, `period`, `status`, `is_active`.
- Filtros `BudgetItem`: `budget`, `item_type`, `code`, `is_active`.
- Ordenamiento y paginación.

## 📂 Archivos
- `backend/tesis/apps/budget/views.py`
- `backend/tesis/tesis/settings.py` (si requiere ajuste global)

## ✅ Criterios de aceptación
- List endpoints filtran/ordenan/paginan según contrato.

## 🏁 Definition of Done
- Consultas de Budget listas para módulos de cálculos e indicadores.

---

## Issue 9 — B9: Tests de Budget (constraints + permisos + filtros + CRUD)

## 🎯 Objetivo
Cubrir el módulo Budget con tests de API y dominio.

## 📍 Alcance
Casos mínimos:
- CRUD de `Budget` y `BudgetItem`.
- Constraint único de `Budget` por `(entity, period)`.
- Constraint único de `BudgetItem` por `(budget, item_type, code)`.
- Permisos lectura/escritura.
- Filtros y paginación.
- Reglas básicas de estado (`draft/approved/closed`).

## 📂 Archivos
- `backend/tesis/apps/budget/tests/test_api.py` (nuevo)
- `backend/tesis/apps/budget/tests/test_serializers.py` (nuevo/ajuste)
- `backend/tesis/apps/budget/tests/test_models.py` (nuevo/ajuste)

## ✅ Criterios de aceptación
- `python manage.py test apps.budget -v 2` en verde.

## 🏁 Definition of Done
- Suite de tests robusta para evitar regresiones de Budget.

---

## Issue 10 — B10: Verificación técnica final de iteración Budget

## 🎯 Objetivo
Cerrar iteración con checks técnicos en verde.

## 📍 Alcance
- Ejecutar checks de proyecto y migraciones.
- Confirmar estabilidad de tests del módulo.

## ✅ Criterios de aceptación
Comandos en verde:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.budget -v 2`

## 🏁 Definition of Done
- Iteración Budget cerrada y lista para pasar a `ingestion`.

---

## Orden recomendado de ejecución

`B1 → B2 → B3 → B4 → B5 → B6 → B7 → B8 → B9 → B10`
