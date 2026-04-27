# Reports API — Tickets atómicos (GitHub Issues)

Este documento define la siguiente iteración recomendada: cerrar el módulo `reports` para generación de informes, estadísticas y clasificación de entidades, reutilizando datos trazables desde `indicators` y `calculations`.

---

## Issue 1 — R1: Contrato API del módulo Reports

## 🎯 Objetivo
Definir endpoints, payloads y status codes para reportes, estadísticas y clasificaciones.

## 📍 Alcance
- Definir contrato de:
  - `POST /api/reports/`
  - `GET /api/reports/`
  - `GET /api/reports/{id}/`
  - `GET /api/stats/`
  - `POST /api/classifications/calculate/`
  - `GET /api/classifications/`
  - `GET /api/classifications/{id}/`
- Alinear documentación y rutas reales.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md`
- `backend/tesis/apps/reports/urls.py`

## ✅ Criterios de aceptación
- Sin contradicciones entre docs y rutas reales.
- Contratos y códigos HTTP explícitos.

---

## Issue 2 — R2: Modelado mínimo para Report y clasificación

## 🎯 Objetivo
Completar/ajustar entidades persistentes para soportar generación y trazabilidad de reportes.

## 📍 Alcance
- Verificar/ajustar modelo `Report` con campos mínimos de consulta.
- Implementar/ajustar modelo `EntityClassification` para almacenar resultado por entidad/período.
- Definir constraints e índices básicos para consultas frecuentes.

## 📂 Archivos
- `backend/tesis/apps/reports/models.py`
- `backend/tesis/apps/reports/migrations/*.py`

## ✅ Criterios de aceptación
- Estructura de datos lista para reportes y clasificaciones sin duplicados inválidos.

---

## Issue 3 — R3: Serializers de entrada/salida para Report

## 🎯 Objetivo
Validar requests y estandarizar respuesta de reportes.

## 📍 Alcance
- Serializer de entrada para generación (`entity`, `period`, filtros opcionales).
- Serializer de salida con:
  - resumen
  - detalle
  - metadatos de trazabilidad
- Validaciones con mensajes claros.

## 📂 Archivos
- `backend/tesis/apps/reports/serializers.py`

## ✅ Criterios de aceptación
- Payload inválido devuelve errores consistentes.
- Payload válido genera estructura de salida documentada.

---

## Issue 4 — R4: Endpoint `POST /api/reports/` (generación bajo demanda)

## 🎯 Objetivo
Exponer generación de informe consolidado para entidad/período.

## 📍 Alcance
- Implementar vista para generar reporte.
- Recolectar datos desde `IndicatorRecord` y/o `CalculationResult`.
- Persistir resultado en `Report` (si aplica estrategia persistida).

## 📂 Archivos
- `backend/tesis/apps/reports/views.py`
- `backend/tesis/apps/reports/services.py` (si aplica)

## ✅ Criterios de aceptación
- Endpoint retorna informe consistente y trazable a datos fuente.

---

## Issue 5 — R5: Endpoints `GET /api/reports/` y `GET /api/reports/{id}/`

## 🎯 Objetivo
Permitir consulta de reportes generados.

## 📍 Alcance
- Listado con filtros mínimos (`entity`, `period`, rango de fechas si aplica).
- Detalle por ID con payload completo.
- Paginación y orden en listado.

## 📂 Archivos
- `backend/tesis/apps/reports/views.py`
- `backend/tesis/apps/reports/urls.py`

## ✅ Criterios de aceptación
- List y detail operativos, con formato DRF consistente.

---

## Issue 6 — R6: Servicio y endpoint de estadísticas `GET /api/stats/`

## 🎯 Objetivo
Exponer agregados listos para visualización (tendencias y comparativas).

## 📍 Alcance
- Implementar servicio de tendencias por entidad/período/indicador.
- Endpoint `GET /api/stats/` con agregaciones para frontend.
- Definir filtros clave y respuesta compacta.

## 📂 Archivos
- `backend/tesis/apps/reports/services.py`
- `backend/tesis/apps/reports/views.py`
- `backend/tesis/apps/reports/serializers.py`

## ✅ Criterios de aceptación
- Endpoint responde agregados coherentes y trazables.

---

## Issue 7 — R7: Cálculo y persistencia de clasificación de entidades

## 🎯 Objetivo
Implementar regla de clasificación y guardar resultado por período.

## 📍 Alcance
- Implementar lógica de clasificación (reglas iniciales versionadas).
- Persistir en `EntityClassification` evitando duplicados inválidos.
- Mantener auditabilidad de criterio aplicado.

## 📂 Archivos
- `backend/tesis/apps/reports/services.py`
- `backend/tesis/apps/reports/models.py`

## ✅ Criterios de aceptación
- Clasificación determinista y repetible para mismos insumos.

---

## Issue 8 — R8: Endpoints de clasificación

## 🎯 Objetivo
Exponer cálculo manual y consulta de clasificaciones.

## 📍 Alcance
- `POST /api/classifications/calculate/`
- `GET /api/classifications/`
- `GET /api/classifications/{id}/`
- Filtros por período/entidad/categoría en list.

## 📂 Archivos
- `backend/tesis/apps/reports/views.py`
- `backend/tesis/apps/reports/urls.py`
- `backend/tesis/apps/reports/serializers.py`

## ✅ Criterios de aceptación
- Flujo de cálculo y consulta funcional con respuestas consistentes.

---

## Issue 9 — R9: Permisos y hardening del módulo Reports

## 🎯 Objetivo
Asegurar política de acceso y respuestas 401/403 homogéneas.

## 📍 Alcance
- Lectura: autenticados con rol permitido (según política vigente).
- Escritura/cálculo: restringido a roles autorizados.
- Ajustes de permisos por endpoint (`reports`, `stats`, `classifications`).

## 📂 Archivos
- `backend/tesis/apps/reports/permissions.py`
- `backend/tesis/apps/reports/views.py`

## ✅ Criterios de aceptación
- No quedan endpoints sensibles abiertos.

---

## Issue 10 — R10: Tests API del módulo Reports

## 🎯 Objetivo
Cubrir flujos críticos de reportes, estadísticas y clasificación.

## 📍 Alcance
Casos mínimos:
- `POST /api/reports/` exitoso y validaciones
- `GET /api/reports/` + `GET /api/reports/{id}/`
- `GET /api/stats/` con filtros
- `POST /api/classifications/calculate/` + list/detail
- matriz de permisos 401/403

## 📂 Archivos
- `backend/tesis/apps/reports/tests/test_api.py`

## ✅ Criterios de aceptación
- `python manage.py test apps.reports.tests.test_api -v 2` en verde.

---

## Issue 11 — R11: Tests de servicios y consistencia estadística

## 🎯 Objetivo
Validar reglas de negocio del motor de reportes y clasificación.

## 📍 Alcance
Casos mínimos:
- consistencia de agregados vs datos de entrada
- reproducibilidad de clasificación
- edge cases con datos faltantes o divisor cero

## 📂 Archivos
- `backend/tesis/apps/reports/tests/test_services.py`

## ✅ Criterios de aceptación
- `python manage.py test apps.reports.tests.test_services -v 2` en verde.

---

## Issue 12 — R12: Verificación técnica final de iteración Reports

## 🎯 Objetivo
Cerrar iteración con checks técnicos y tests en verde.

## 📍 Alcance
Ejecutar:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.reports -v 2`

## ✅ Criterios de aceptación
- Sin issues, sin migraciones pendientes y tests en verde.

---

## Orden recomendado

`R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 → R9 → R10 → R11 → R12`
