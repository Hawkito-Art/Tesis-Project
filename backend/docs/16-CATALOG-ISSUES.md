# Catalog API — Tickets atómicos (GitHub Issues)

Este documento contiene los tickets atómicos para implementar la API del módulo `catalog` en la Iteración 2.

---

## Issue 1 — C1: Cerrar contrato de API para `entities` y `periods`

## 🎯 Objetivo
Definir y alinear rutas, payloads y códigos HTTP de `Entity` y `Period`.

## 📍 Alcance
- Definir endpoints:
  - `GET/POST /api/entities/`
  - `GET/PATCH/DELETE /api/entities/{id}/`
  - `GET/POST /api/periods/`
  - `GET/PATCH /api/periods/{id}/`
- Alinear documentación y rutas reales.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md` (si hace falta completar)
- `backend/tesis/apps/catalog/urls.py`

## ✅ Criterios de aceptación
- Endpoints definidos y sin contradicciones entre docs y código.
- Status codes documentados y consistentes.

## 🏁 Definition of Done
- Contrato de Catalog explícito y listo para implementar.

---

## Issue 2 — C2: Completar validaciones de serializers de Catalog

## 🎯 Objetivo
Endurecer validaciones de `Entity` y `Period`.

## 📍 Alcance
- Mantener validación de mes (1..12) y año (rango válido).
- Validar `code` y `name` en `Entity` (requeridos/formato).
- Mensajes de error claros.

## 📂 Archivos
- `backend/tesis/apps/catalog/serializers.py`

## ✅ Criterios de aceptación
- Serializers rechazan payload inválido con errores consistentes.
- Payloads válidos pasan sin romper contrato.

## 🏁 Definition of Done
- Serializers de Catalog listos y cubiertos por tests unitarios.

---

## Issue 3 — C3: Implementar vistas CRUD para `Entity`

## 🎯 Objetivo
Exponer list/create/retrieve/partial_update/delete para entidades.

## 📍 Alcance
- Implementar vistas DRF para `Entity`.
- Definir comportamiento de delete según política (soft delete si aplica).

## 📂 Archivos
- `backend/tesis/apps/catalog/views.py`

## ✅ Criterios de aceptación
- Endpoints de `Entity` funcionales.
- Respuestas y errores en formato estándar DRF.

## 🏁 Definition of Done
- CRUD de `Entity` operativo y validado.

---

## Issue 4 — C4: Implementar vistas CRUD para `Period`

## 🎯 Objetivo
Exponer list/create/retrieve/partial_update para períodos.

## 📍 Alcance
- Implementar vistas DRF para `Period`.
- Manejar constraint único `(year, month, period_type)` con error legible.

## 📂 Archivos
- `backend/tesis/apps/catalog/views.py`

## ✅ Criterios de aceptación
- Endpoints de `Period` funcionales.
- Duplicados de período devuelven error consistente.

## 🏁 Definition of Done
- CRUD parcial de `Period` operativo y validado.

---

## Issue 5 — C5: Registrar URLs de Catalog

## 🎯 Objetivo
Publicar rutas de vistas de `Entity` y `Period`.

## 📍 Alcance
- Reemplazar `urlpatterns = []` por rutas reales.
- Mantener coherencia con contrato de C1.

## 📂 Archivos
- `backend/tesis/apps/catalog/urls.py`

## ✅ Criterios de aceptación
- Todas las rutas de Catalog responden correctamente.

## 🏁 Definition of Done
- Módulo Catalog enrutable desde `api/catalog/`.

---

## Issue 6 — C6: Permisos por endpoint (lectura autenticados, escritura admin)

## 🎯 Objetivo
Aplicar matriz de permisos del módulo Catalog.

## 📍 Alcance
- Lectura para autenticados autorizados.
- Escritura para admin.
- Respuestas 401/403 consistentes.

## 📂 Archivos
- `backend/tesis/apps/catalog/views.py`
- `backend/tesis/apps/catalog/permissions.py` (si hace falta crear)

## ✅ Criterios de aceptación
- No hay endpoints de escritura expuestos a usuarios sin privilegios.

## 🏁 Definition of Done
- Permisos de Catalog implementados y testeados.

---

## Issue 7 — C7: Filtros, búsqueda, orden y paginación

## 🎯 Objetivo
Agregar capacidad de consulta escalable para listados.

## 📍 Alcance
- Filtros `Entity`: `code`, `name`, `type` (si existe), `is_consolidated`.
- Filtros `Period`: `year`, `month`.
- Ordenamiento y paginación.

## 📂 Archivos
- `backend/tesis/apps/catalog/views.py`
- `backend/tesis/tesis/settings.py` (si requiere ajuste global)

## ✅ Criterios de aceptación
- List endpoints filtran/ordenan/paginan según contrato.

## 🏁 Definition of Done
- Consultas de Catalog listas para consumo de módulos siguientes.

---

## Issue 8 — C8: Seed data inicial (6 entidades del Excel)

## 🎯 Objetivo
Cargar dataset base de entidades para desbloquear presupuesto/ingesta/cálculos.

## 📍 Alcance
- Crear comando de seed idempotente.
- Insertar las 6 entidades base definidas en plan.

## 📂 Archivos sugeridos
- `backend/tesis/apps/catalog/management/commands/seed_catalog.py`

## ✅ Criterios de aceptación
- Seed crea/actualiza sin duplicar datos.
- Correr seed múltiples veces no rompe consistencia.

## 🏁 Definition of Done
- Dataset base disponible para pruebas funcionales.

---

## Issue 9 — C9: Tests de catálogo (constraints + permisos + filtros + CRUD)

## 🎯 Objetivo
Cubrir el módulo Catalog con tests de API y capa de dominio.

## 📍 Alcance
Casos mínimos:
- CRUD de `Entity` y `Period`.
- Constraint único de `Period`.
- Duplicado de `code` en `Entity` rechazado.
- Permisos lectura/escritura.
- Filtros y paginación.

## 📂 Archivos
- `backend/tesis/apps/catalog/tests/test_api.py` (nuevo)
- `backend/tesis/apps/catalog/tests/test_serializers.py` (nuevo/ajuste)
- `backend/tesis/apps/catalog/tests/test_models.py` (nuevo/ajuste)

## ✅ Criterios de aceptación
- `python manage.py test apps.catalog -v 2` en verde.

## 🏁 Definition of Done
- Suite de tests robusta para evitar regresiones de Catalog.

---

## Issue 10 — C10: Verificación técnica final de iteración Catalog

## 🎯 Objetivo
Cerrar iteración con checks técnicos en verde.

## 📍 Alcance
- Ejecutar checks de proyecto y migraciones.
- Confirmar estabilidad de tests del módulo.

## ✅ Criterios de aceptación
Comandos en verde:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.catalog -v 2`

## 🏁 Definition of Done
- Iteración Catalog cerrada y lista para pasar a `budget`.

---

## Orden recomendado de ejecución

`C1 → C2 → C3 → C4 → C5 → C6 → C7 → C8 → C9 → C10`
