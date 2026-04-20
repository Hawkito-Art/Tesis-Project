# Ingestión Excel + Cálculos de Indicadores — Tickets atómicos (GitHub Issues)

Este documento contiene tickets atómicos para implementar la carga de tablas Excel de indicadores y la ejecución de cálculos derivados bajo demanda.

Las reglas de negocio aquí reflejan decisiones cerradas con usuario:
- `estimado_prox_mes = real_acumulado + (real_acumulado * 0.1)`
- división por cero/vacío en derivados => guardar `0`
- duplicados `(entity, period, indicator, variable_name)` => reemplazar (upsert)
- importación parcial => filas válidas entran, filas inválidas se registran
- cálculos derivados => se ejecutan solo cuando el usuario lo solicite
- mapeo de indicador desde Excel => por nombre exacto (`INDICADORES`)

---

## Issue 1 — I1: Cerrar contrato de importación Excel y cálculo bajo demanda

## 🎯 Objetivo
Definir contrato API para subir Excel, consultar estado de importación y disparar cálculo manual.

## 📍 Alcance
- Definir endpoints (propuesta):
  - `POST /api/ingestion/documents/` (subir archivo)
  - `GET /api/ingestion/import-jobs/{id}/` (estado + métricas)
  - `GET /api/ingestion/import-jobs/{id}/details/` (errores por fila)
  - `POST /api/calculations/run/` (ejecución manual por entidad/período)
- Definir payloads, respuestas y códigos HTTP esperados.
- Alinear docs y rutas reales.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md`
- `backend/tesis/apps/ingestion/urls.py`
- `backend/tesis/apps/calculations/urls.py`

## ✅ Criterios de aceptación
- Endpoints y contratos sin contradicciones entre docs y código.
- Códigos HTTP documentados y consistentes.

## 🏁 Definition of Done
- Contrato de ingesta/cálculo explícito y listo para implementar.

---

## Issue 2 — I2: Implementar serializers de ingreso para `Document` e `ImportJob`

## 🎯 Objetivo
Validar carga de archivo Excel y parámetros de ejecución de importación.

## 📍 Alcance
- Serializer para carga de documento (`.xlsx` requerido).
- Validación de campos obligatorios y mensajes claros.
- Serializer para disparar procesamiento (si aplica endpoint separado).

## 📂 Archivos
- `backend/tesis/apps/ingestion/serializers.py`

## ✅ Criterios de aceptación
- Rechaza archivos no válidos con error DRF consistente.
- Acepta carga válida y genera entidad de documento.

## 🏁 Definition of Done
- Capa de validación de entrada de ingesta robusta.

---

## Issue 3 — I3: Implementar endpoint de carga de documento y creación de `ImportJob`

## 🎯 Objetivo
Exponer API para recibir Excel y crear trabajo de importación trazable.

## 📍 Alcance
- Crear vista `POST` para documento.
- Crear `ImportJob` asociado en estado `pendiente`.
- Guardar `uploaded_by`.

## 📂 Archivos
- `backend/tesis/apps/ingestion/views.py`
- `backend/tesis/apps/ingestion/services.py`

## ✅ Criterios de aceptación
- Endpoint devuelve IDs de `Document` e `ImportJob`.
- Estado inicial del job correcto.

## 🏁 Definition of Done
- Flujo de entrada de archivo operativo y auditable.

---

## Issue 4 — I4: Implementar parser Excel con mapeo de columnas canónicas

## 🎯 Objetivo
Convertir la planilla de formato fijo en estructura normalizada para persistencia.

## 📍 Alcance
- Leer hoja con layout de `docs/tablas.md`.
- Mapear columnas canónicas:
  - `plan_anual`, `ano_anterior`, `plan_acumulado`, `real_acumulado`
- Ignorar filas de encabezado/sección que no representen indicador cargable.
- Resolver indicador por nombre exacto (`INDICADORES`).

## 📂 Archivos
- `backend/tesis/apps/ingestion/services.py`

## ✅ Criterios de aceptación
- Parser transforma filas válidas a estructura intermedia consistente.
- Fila con indicador no encontrado queda marcada con error de mapeo.

## 🏁 Definition of Done
- Parser estable para formato Excel esperado.

---

## Issue 5 — I5: Implementar importación parcial con detalle de errores por fila

## 🎯 Objetivo
Procesar filas válidas y registrar las inválidas sin abortar toda la importación.

## 📍 Alcance
- Política parcial obligatoria:
  - filas válidas -> persisten
  - filas inválidas -> `DocumentDetail` con `is_valid=False` y `error_message`
- Mantener métricas del job (`total_rows`, `processed_rows`, `error_rows`).
- `error_log` resumido del job.

## 📂 Archivos
- `backend/tesis/apps/ingestion/services.py`
- `backend/tesis/apps/ingestion/models.py` (si requiere ajuste menor)

## ✅ Criterios de aceptación
- Job finaliza en `completado` aunque existan errores por fila.
- Errores quedan trazables por `row_number`.

## 🏁 Definition of Done
- Importación parcial implementada con auditoría completa.

---

## Issue 6 — I6: Persistir datos base en `IndicatorRecord` con upsert

## 🎯 Objetivo
Guardar variables de entrada por entidad/período/indicador reemplazando duplicados.

## 📍 Alcance
- Persistir variables base por fila en `IndicatorRecord`.
- Upsert por clave única actual:
  - `(entity, indicator, period, variable_name)`
- Reemplazo del valor existente cuando ya exista registro.

## 📂 Archivos
- `backend/tesis/apps/ingestion/services.py`
- `backend/tesis/apps/indicators/models.py` (sin cambio de esquema salvo necesidad puntual)

## ✅ Criterios de aceptación
- Reimportar mismo indicador/variable reemplaza valor anterior.
- No se generan duplicados por constraint único.

## 🏁 Definition of Done
- Persistencia normalizada y consistente con política de reemplazo.

---

## Issue 7 — I7: Exponer consulta de estado y errores de `ImportJob`

## 🎯 Objetivo
Permitir seguimiento operativo del proceso de importación.

## 📍 Alcance
- Endpoint de detalle de job (estado + métricas).
- Endpoint/listado de errores por fila (`DocumentDetail`).
- Paginar detalles si crecen.

## 📂 Archivos
- `backend/tesis/apps/ingestion/views.py`
- `backend/tesis/apps/ingestion/serializers.py`
- `backend/tesis/apps/ingestion/urls.py`

## ✅ Criterios de aceptación
- Usuario puede consultar qué filas fallaron y por qué.
- Respuesta consistente con contrato de I1.

## 🏁 Definition of Done
- Trazabilidad operativa completa del job de importación.

---

## Issue 8 — I8: Implementar motor de fórmulas en `calculations/services.py`

## 🎯 Objetivo
Calcular variables derivadas con reglas de negocio confirmadas.

## 📍 Alcance
- Implementar fórmulas:
  - `porcentaje_r_p = (real_acumulado / plan_acumulado) * 100`
  - `real_aa = (real_acumulado / ano_anterior) * 100`
  - `estimado_prox_mes = real_acumulado + (real_acumulado * 0.1)`
  - correlación = `salario_medio / productividad_del_trabajo`
- Regla de división por cero o denominador vacío => `0`.

## 📂 Archivos
- `backend/tesis/apps/calculations/services.py`

## ✅ Criterios de aceptación
- Fórmulas producen valores esperados en casos normales.
- Casos divisor 0/vacío no fallan y retornan `0`.

## 🏁 Definition of Done
- Motor de cálculo determinista y estable.

---

## Issue 9 — I9: Endpoint de ejecución manual de cálculo

## 🎯 Objetivo
Permitir correr cálculos derivados solo cuando el usuario lo solicite.

## 📍 Alcance
- `POST /api/calculations/run/` con filtros mínimos (`entity`, `period`).
- Crear/actualizar `Calculation` con estado (`pendiente/en_progreso/completado/error`).
- Persistir resultados en `CalculationResult`.

## 📂 Archivos
- `backend/tesis/apps/calculations/views.py`
- `backend/tesis/apps/calculations/serializers.py`
- `backend/tesis/apps/calculations/services.py`
- `backend/tesis/apps/calculations/urls.py`

## ✅ Criterios de aceptación
- El cálculo NO corre automáticamente tras importación.
- Solo se ejecuta cuando se invoca el endpoint manual.

## 🏁 Definition of Done
- Ejecución de cálculo bajo demanda operativa.

---

## Issue 10 — I10: Permisos y validaciones de acceso en ingesta/cálculo

## 🎯 Objetivo
Restringir operaciones sensibles y estandarizar respuestas 401/403.

## 📍 Alcance
- Definir permisos para:
  - carga/procesamiento de Excel
  - ejecución de cálculo manual
  - lectura de jobs y errores
- Alinear con convención actual de proyecto (lectura autenticados, escritura/admin según regla de negocio acordada).

## 📂 Archivos
- `backend/tesis/apps/ingestion/permissions.py`
- `backend/tesis/apps/calculations/permissions.py`
- `backend/tesis/apps/ingestion/views.py`
- `backend/tesis/apps/calculations/views.py`

## ✅ Criterios de aceptación
- Endpoints sensibles no quedan expuestos a usuarios sin privilegios.
- Respuestas de autorización consistentes.

## 🏁 Definition of Done
- Seguridad base de módulo ingestion/calculations implementada.

---

## Issue 11 — I11: Tests de ingesta Excel (parser + importación parcial + upsert)

## 🎯 Objetivo
Cubrir con tests las reglas de importación y persistencia.

## 📍 Alcance
Casos mínimos:
- parseo correcto de estructura esperada
- manejo de filas inválidas con `DocumentDetail`
- upsert en `IndicatorRecord`
- mapeo por nombre exacto de indicador
- normalización numérica (coma/punto) si aplica

## 📂 Archivos
- `backend/tesis/apps/ingestion/tests/test_services.py` (nuevo)
- `backend/tesis/apps/ingestion/tests/test_api.py` (nuevo)

## ✅ Criterios de aceptación
- `python manage.py test apps.ingestion -v 2` en verde.

## 🏁 Definition of Done
- Suite de tests robusta de ingesta y trazabilidad.

---

## Issue 12 — I12: Tests de cálculos derivados y endpoint de ejecución manual

## 🎯 Objetivo
Validar precisión de fórmulas y comportamiento del endpoint de cálculo.

## 📍 Alcance
Casos mínimos:
- `R/P`, `R/AA`, `estimado_prox_mes`, correlación
- divisiones por cero/vacío => `0`
- ejecución solo bajo endpoint manual
- persistencia de `Calculation` y `CalculationResult`

## 📂 Archivos
- `backend/tesis/apps/calculations/tests/test_services.py` (nuevo)
- `backend/tesis/apps/calculations/tests/test_api.py` (nuevo)

## ✅ Criterios de aceptación
- `python manage.py test apps.calculations -v 2` en verde.

## 🏁 Definition of Done
- Cobertura funcional de reglas de cálculo confirmadas.

---

## Issue 13 — I13: Verificación técnica final de iteración Ingestión+Cálculos

## 🎯 Objetivo
Cerrar iteración con checks técnicos y tests en verde.

## 📍 Alcance
- Ejecutar checks de Django y migraciones (si aplica)
- Validar suites de `ingestion` y `calculations`

## ✅ Criterios de aceptación
Comandos en verde:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.ingestion -v 2`
- `python manage.py test apps.calculations -v 2`

## 🏁 Definition of Done
- Iteración de ingesta/cálculos cerrada y lista para reportes.

---

## Orden recomendado de ejecución

`I1 → I2 → I3 → I4 → I5 → I6 → I7 → I8 → I9 → I10 → I11 → I12 → I13`
