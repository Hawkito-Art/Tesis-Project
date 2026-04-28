# Export XLSX — Plan de acción y tickets atómicos (GitHub Issues)

Este documento define la iteración para implementar exportación XLSX **sincrónica/inmediata** en el endpoint `POST /api/exports/xlsx/`, incluyendo datos de **indicator records**.

Decisiones ya cerradas con usuario:
- Estrategia de entrega: **descarga inmediata (síncrona)**.
- Alcance mínimo de datos: incluir **indicator records** en el XLSX.

---

## EX1 — Contrato final del endpoint de exportación

## 🎯 Objetivo
Definir request/response final de `POST /api/exports/xlsx/` para descarga inmediata.

## 📍 Alcance
- Definir payload de filtros opcionales:
  - `entity`
  - `period`
  - (extensible) `indicator`, `group`, `variable_name`
- Definir respuesta exitosa como archivo binario XLSX:
  - `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `Content-Disposition: attachment; filename="export_<timestamp>.xlsx"`
- Definir errores esperados: `400`, `401`, `403`.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md`
- `backend/tesis/apps/calculations/views.py`
- `backend/tesis/apps/calculations/serializers.py`

## ✅ Criterios de aceptación
- Contrato de request/response sin ambigüedades.
- El endpoint deja de responder JSON placeholder y devuelve archivo en éxito.

---

## EX2 — Servicio de construcción de workbook XLSX

## 🎯 Objetivo
Crear servicio reutilizable para construir el archivo XLSX.

## 📍 Alcance
- Implementar servicio (por ejemplo `build_export_workbook(...)`) que:
  - consulte `IndicatorRecord` con filtros,
  - ordene resultados de manera determinista,
  - genere workbook con hoja principal `indicator_records`.
- Columnas mínimas sugeridas:
  - `entity_code`, `entity_name`
  - `period_year`, `period_month`, `period_type`
  - `indicator_code`, `indicator_name`, `indicator_group`
  - `variable_name`, `value`
  - `source`, `import_job_id`, `calculation_id`
  - `created_at`, `updated_at`

## 📂 Archivos
- `backend/tesis/apps/calculations/services.py` (o módulo dedicado de export)

## ✅ Criterios de aceptación
- El servicio devuelve workbook válido con estructura estable.
- Incluye trazabilidad de origen de datos.

---

## EX3 — Integración del servicio con el endpoint

## 🎯 Objetivo
Conectar serializer + servicio + respuesta de descarga.

## 📍 Alcance
- En `POST /api/exports/xlsx/`:
  - validar filtros,
  - construir workbook,
  - serializar en memoria (`BytesIO`),
  - responder `HttpResponse`/`FileResponse` con headers correctos.

## 📂 Archivos
- `backend/tesis/apps/calculations/views.py`
- `backend/tesis/apps/calculations/urls.py`

## ✅ Criterios de aceptación
- Cliente recibe archivo descargable inmediatamente.
- Nombre de archivo y MIME type correctos.

---

## EX4 — Permisos y hardening del endpoint de exportación

## 🎯 Objetivo
Asegurar control de acceso y respuestas homogéneas.

## 📍 Alcance
- Mantener permisos actuales de cálculo/export (`admin` y `analyst`), denegando usuarios sin rol.
- Confirmar respuestas:
  - `401` sin token,
  - `403` sin rol autorizado,
  - `400` filtros inválidos.

## 📂 Archivos
- `backend/tesis/apps/calculations/permissions.py`
- `backend/tesis/apps/calculations/views.py`

## ✅ Criterios de aceptación
- Endpoint sensible no expuesto.
- Matriz de autorización consistente.

---

## EX5 — Tests de exportación XLSX

## 🎯 Objetivo
Cubrir generación de archivo y reglas de acceso.

## 📍 Alcance
Casos mínimos:
- export exitoso devuelve XLSX real y headers correctos,
- contenido incluye filas de `IndicatorRecord`,
- filtros (`entity`, `period`) reducen dataset correctamente,
- `401/403` según permisos,
- `400` en payload inválido.

## 📂 Archivos
- `backend/tesis/apps/calculations/tests/test_export_api.py`
- (si aplica) `backend/tesis/apps/calculations/tests/test_services.py`

## ✅ Criterios de aceptación
- `python manage.py test apps.calculations -v 2` en verde con cobertura de export.

---

## EX6 — Verificación técnica final

## 🎯 Objetivo
Cerrar iteración de exportación con validaciones técnicas.

## 📍 Alcance
Ejecutar:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.calculations -v 2`

## ✅ Criterios de aceptación
- Sin issues, sin migraciones pendientes y tests verdes.

---

## Orden recomendado

`EX1 → EX2 → EX3 → EX4 → EX5 → EX6`

---

## Protocolo de validación contigo (checkpoint por checkpoint)

Para evitar desalineación, vamos a validar contigo en cada paso:

1. **Checkpoint A (EX1)**: contrato final de payload + columnas + nombre de archivo.
2. **Checkpoint B (EX2/EX3)**: estructura final de hoja XLSX y formato de celdas.
3. **Checkpoint C (EX4)**: matriz final de permisos para export.
4. **Checkpoint D (EX5/EX6)**: cobertura de tests y cierre técnico.

No avanzamos al siguiente checkpoint sin tu OK.
