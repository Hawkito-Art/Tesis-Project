# Budget API — Tickets atómicos 

Este documento contiene los tickets atómicos para implementar la API del módulo `budget` en la Iteración 3.

---

## Issue 1 — B1: Cerrar contrato de API para `budgets` y `budget-items`

## 🎯 Objetivo
Dejar completamente especificado el contrato de la API del módulo `budget` para que el comportamiento de rutas, payloads, permisos, filtros y errores quede alineado entre documentación y código.

## 📍 Alcance funcional
- Publicar y documentar estos endpoints:
  - `GET /api/budgets/`
  - `POST /api/budgets/`
  - `GET /api/budgets/{id}/`
  - `PATCH /api/budgets/{id}/`
  - `DELETE /api/budgets/{id}/`
  - `GET /api/budget-items/`
  - `POST /api/budget-items/`
  - `GET /api/budget-items/{id}/`
  - `PATCH /api/budget-items/{id}/`
  - `DELETE /api/budget-items/{id}/`
- Alinear el contrato con los modelos y serializers reales.
- Dejar explícitos los casos felices, fallos esperados y restricciones de negocio.

## 📌 Contrato mínimo esperado

### `Budget`
- Campos de entrada permitidos:
  - `entity` (FK obligatoria a `Entity` activa)
  - `period` (FK obligatoria a `Period` activo)
  - `description` (opcional)
  - `status` (`draft`, `approved`, `closed`)
  - `is_active` (booleano)
- Campos gestionados por el servidor:
  - `created_by`
  - `created_at`
  - `updated_at`
- Campos de solo lectura en respuesta:
  - `id`
  - `entity_code`
  - `period_display`
  - `items`

### `BudgetItem`
- Campos de entrada permitidos:
  - `budget` (FK obligatoria a `Budget`)
  - `item_type` (`ingreso`, `gasto`)
  - `code` (obligatorio, trimmed)
  - `name` (obligatorio, trimmed)
  - `planned_amount` (decimal no negativo)
  - `actual_amount` (decimal no negativo)
  - `is_active` (booleano)
- Campos de solo lectura en respuesta:
  - `id`
  - `created_at`
  - `updated_at`

## 🔁 Reglas de negocio
- Solo usuarios autenticados pueden leer los recursos.
- Solo usuarios con privilegios de escritura pueden crear, actualizar o eliminar.
- `Budget` debe ser único por combinación `(entity, period)`.
- `BudgetItem` debe ser único por combinación `(budget, item_type, code)`.
- No se permiten modificaciones sobre un `Budget` con `status = closed`.
- No se permiten modificaciones ni eliminaciones sobre `BudgetItem` pertenecientes a un `Budget` cerrado.
- `entity` y `period` deben existir y estar activos al crear o actualizar un `Budget`.
- Los montos `planned_amount` y `actual_amount` no pueden ser negativos.
- `code` y `name` no pueden quedar vacíos después de aplicar `trim`.

## ✅ Happy path

### HP1 - Listar presupuestos
**Dado** un usuario autenticado con permiso de lectura
**Cuando** ejecuta `GET /api/budgets/`
**Entonces** recibe `200 OK` con un listado paginado de presupuestos.
**Y** cada elemento incluye `entity_code`, `period_display` e `items`.

### HP2 - Crear presupuesto
**Dado** un usuario autenticado con permiso de escritura y una `entity` activa más un `period` activo
**Cuando** ejecuta `POST /api/budgets/` con `entity`, `period`, `description`, `status` opcional e `is_active`
**Entonces** recibe `201 Created`.
**Y** el presupuesto queda persistido con `created_by` asignado automáticamente.
**Y** la combinación `(entity, period)` queda registrada sin duplicados.

### HP3 - Consultar y actualizar presupuesto
**Dado** un presupuesto existente con estado distinto de `closed`
**Cuando** ejecuta `GET /api/budgets/{id}/`
**Entonces** recibe `200 OK` con el detalle completo.
**Cuando** ejecuta `PATCH /api/budgets/{id}/`
**Entonces** recibe `200 OK` y los campos editables quedan actualizados.

### HP4 - Eliminar presupuesto
**Dado** un presupuesto existente con estado distinto de `closed`
**Cuando** ejecuta `DELETE /api/budgets/{id}/`
**Entonces** recibe `204 No Content`.

### HP5 - Crear partida presupuestaria
**Dado** un usuario autenticado con permiso de escritura y un `Budget` no cerrado
**Cuando** ejecuta `POST /api/budget-items/` con `budget`, `item_type`, `code`, `name`, `planned_amount`, `actual_amount` e `is_active`
**Entonces** recibe `201 Created`.
**Y** la partida queda asociada al presupuesto indicado.

### HP6 - Editar y eliminar partida presupuestaria
**Dado** una partida existente asociada a un `Budget` no cerrado
**Cuando** ejecuta `PATCH /api/budget-items/{id}/`
**Entonces** recibe `200 OK` con los cambios persistidos.
**Cuando** ejecuta `DELETE /api/budget-items/{id}/`
**Entonces** recibe `204 No Content`.

## ❌ Bad path

### BP1 - Acceso sin autenticación
**Dado** un request sin token
**Cuando** intenta acceder a cualquier endpoint de `budget`
**Entonces** recibe `401 Unauthorized`.

### BP2 - Escritura sin privilegios
**Dado** un usuario autenticado sin rol admin ni privilegios equivalentes
**Cuando** intenta hacer `POST`, `PATCH` o `DELETE`
**Entonces** recibe `403 Forbidden`.

### BP3 - Presupuesto duplicado
**Dado** que ya existe un `Budget` para la misma combinación `(entity, period)`
**Cuando** se intenta crear otro con los mismos valores
**Entonces** recibe `400 Bad Request` con un mensaje de conflicto de unicidad legible.

### BP4 - Partida duplicada
**Dado** que ya existe una `BudgetItem` para la misma combinación `(budget, item_type, code)`
**Cuando** se intenta crear o actualizar una partida con esos valores
**Entonces** recibe `400 Bad Request` con un mensaje de conflicto de unicidad legible.

### BP5 - Entidad o periodo inactivo/inexistente
**Dado** un `entity` o `period` inexistente o inactivo
**Cuando** se intenta crear o actualizar un `Budget`
**Entonces** recibe `400 Bad Request` con error de validación sobre el campo correspondiente.

### BP6 - Presupuesto cerrado
**Dado** un `Budget` con `status = closed`
**Cuando** se intenta hacer `PATCH` o `DELETE` sobre ese presupuesto
**Entonces** recibe `400 Bad Request` con un error de regla de negocio.

### BP7 - Partida dentro de presupuesto cerrado
**Dado** una `BudgetItem` cuyo presupuesto padre está cerrado
**Cuando** se intenta hacer `PATCH` o `DELETE`
**Entonces** recibe `400 Bad Request` con un error de regla de negocio.

### BP8 - Montos negativos
**Dado** un `planned_amount` o `actual_amount` menor que cero
**Cuando** se intenta crear o actualizar una partida
**Entonces** recibe `400 Bad Request` con error específico del campo.

### BP9 - Campos inválidos o vacíos
**Dado** un `code` o `name` vacío después de `trim`, o un `item_type` inválido, o un `status` inválido
**Cuando** se envía el payload
**Entonces** recibe `400 Bad Request` con errores por campo.

### BP10 - Recurso inexistente
**Dado** un `id` inexistente
**Cuando** se consulta, actualiza o elimina
**Entonces** recibe `404 Not Found`.

## 🌐 Paginación, filtros y orden
- `GET /api/budgets/` debe soportar filtros por `entity`, `period`, `status` e `is_active`.
- `GET /api/budget-items/` debe soportar filtros por `budget`, `item_type`, `code` e `is_active`.
- Ambos listados deben respetar el `PageNumberPagination` global del proyecto.
- El ordenamiento permitido debe quedar documentado en `backend/docs/10-API-REFERENCE.md` y coincidir con la vista.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md`
- `backend/tesis/apps/budget/models.py`
- `backend/tesis/apps/budget/serializers.py`
- `backend/tesis/apps/budget/views.py`
- `backend/tesis/apps/budget/permissions.py`
- `backend/tesis/apps/budget/services.py`
- `backend/tesis/apps/budget/urls.py`

## ✅ Criterios de aceptación
- El contrato documenta rutas, payloads, campos de solo lectura y reglas de negocio sin ambigüedades.
- Los casos felices están descritos para lectura, creación, actualización y eliminación de ambos recursos.
- Los casos malos cubren autenticación, permisos, unicidad, validación de campos, estados cerrados y recursos inexistentes.
- Los códigos HTTP esperados quedan alineados con el estándar del proyecto.
- No existen contradicciones entre la spec y el contrato reflejado en código.

## 🏁 Definition of Done
- El contrato de Budget queda especificado de punta a punta y listo para implementación o ajuste fino en API Reference.

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
