# 7 - Proceso del Modulo Ingestion

## Objetivo

Implementar pipeline completo de importacion de Excel (.xls/.xlsx): carga, parseo, validacion y migracion.

## Prerequisitos

- [4-APP-CATALOG](4-APP-CATALOG.md)
- [5-APP-BUDGET](5-APP-BUDGET.md)
- [6-APP-INDICATORS](6-APP-INDICATORS.md)

## Entradas

- Archivos `.xls` (xlrd) o `.xlsx` (openpyxl).
- Archivo principal: `Indicadores 2025.xls` — 6 hojas, una por entidad economica.
- Catalogos de entidades, periodos e indicadores ya cargados (incluyendo grupos y variables estandar).

## Pasos

### Paso 1: Upload de documento

- [ ] Implementar `Document` y endpoint `POST /api/documents/upload/`.
- [ ] Validar extension (.xls o .xlsx), tamano y usuario autenticado.
- [ ] Registrar metadata: nombre, tipo (xls/xlsx), tamano, ruta, `uploaded_by`.
- [ ] Seleccionar libreria segun extension: `xlrd` para .xls, `openpyxl` para .xlsx.

### Paso 2: Crear trabajo de importacion

- [ ] Crear `ImportJob` asociado a documento.
- [ ] Inicializar estado `uploaded`.
- [ ] Detectar entidades y periodos del archivo si es posible (metadata del nombre o contenido).

### Paso 3: Parseo a staging

El Excel `Indicadores 2025.xls` tiene estructura por hojas:

- **Cada hoja = una entidad** (ver PLAN_DE_ACCION §4.1 para mapeo hoja→Entity).
- **Filas 0-6**: cabeceras (titulo, unidad de medida, codigo interno `45992.0`, encabezados de columna).
- **Filas de indicadores**: datos por indicador, columnas = variables.
- **Filas separadoras**: "Indicadores Limites", "Otros Indicadores" (no son datos).
- **Filas de pie**: "Aprobado:", nombre de directora (no son datos).

Parser por hoja:

1. Abrir hoja con `xlrd` (`.xls`) u `openpyxl` (`.xlsx`).
2. Saltar filas de cabecera hasta encontrar la fila con encabezados de columna (contiene "PLAN" y "AÑO").
3. Leer encabezados para mapear columnas a `variable_name`:
   | Col indice | variable_name |
   |------------|---------------|
   | 2 (o 1 si no hay U:M separada) | plan_anual |
   | 3 | ano_anterior |
   | 4 | plan_acumulado |
   | 5 | real_acumulado |
   | 6 | porcentaje_r_p |
   | 7 | real_aa |
   | 8 | estimado_prox_mes |
   | 9 | estimado_cierre_ano |
4. Para cada fila siguiente:
   - Si la celda col 0 es vacia o contiene texto de separador/firma → skip.
   - Si la celda col 0 tiene un nombre de indicador conocido → procesar.
   - Para cada columna de variable (cols 2-9), insertar un `DocumentDetail`:
     - `entity_code`: codigo de la entidad (derivado del nombre de la hoja)
     - `indicator_code`: codigo del indicador (derivado del nombre de la fila)
     - `variable_name`: segun mapeo de columna
     - `raw_value`: valor crudo de la celda
     - `parsed_value`: conversion a Decimal (null si no es numerico)
     - `is_valid`: True si parsed_value no es null y el indicador existe
5. Actualizar contadores en `ImportJob`: `rows_total`, `rows_processed`.

[ ] Implementar servicio `ExcelParser.parse(document, import_job)`.
[ ] Insertar filas en `DocumentDetail` con `raw_value` y `parsed_value`.
[ ] Actualizar contadores de filas en `ImportJob`.

### Paso 4: Estandarizacion

- [ ] Normalizar codigos de entidad: mapear nombre de hoja a `Entity.code` (configuracion externa).
  - Ejemplo: "Emp.Agropecuaria" → entity.code = "AGRO"
- [ ] Normalizar indicadores: mapear nombre de fila a `Indicator.code`.
  - Ejemplo: "Ventas Totales" → indicator.code = "VENTAS_TOT"
- [ ] Normalizar variable_name: mapear indice de columna a nombre estandar.
- [ ] Marcar discrepancias: indicador no encontrado, entidad no encontrada, valor no numerico.
- [ ] Servicio `Standardizer.standardize(import_job)` actualiza `is_valid` y `validation_error`.

### Paso 5: Validacion

- [ ] Endpoint `POST /api/import-jobs/{id}/validate/`.
- [ ] Verificar que `entity_code` existe en catalogo de entidades.
- [ ] Verificar que `indicator_code` existe en catalogo de indicadores.
- [ ] Verificar que `variable_name` es una variable valida del indicador.
- [ ] Verificar que `parsed_value` es numerico y razonable.
- [ ] Marcar `is_valid` y `validation_error` por fila.
- [ ] Actualizar totales `rows_valid`/`rows_invalid` en `ImportJob`.

### Paso 6: Migracion a records

- [ ] Endpoint `POST /api/import-jobs/{id}/migrate/`.
- [ ] Migrar solo filas con `is_valid=True` a `IndicatorRecord` dentro de transaccion.
- [ ] Cada `DocumentDetail` valido genera un `IndicatorRecord` con:
  - `entity`: FK a la entidad mapeada
  - `indicator`: FK al indicador mapeado
  - `period`: FK al periodo (del ImportJob o inferido)
  - `variable_name`: variable_name de la fila
  - `value`: parsed_value
  - `data_origin`: "imported"
  - `source_document`: FK al Document
  - `import_job`: FK al ImportJob
- [ ] Guardar trazabilidad con `source_document` e `import_job`.
- [ ] Actualizar estado de `ImportJob` a `completed` o `failed`.

### Paso 7: Errores y reintentos

- [ ] Exponer `GET /api/import-jobs/{id}/errors/`.
- [ ] Permitir correccion manual de `DocumentDetail` y reintento de validacion/migracion.
- [ ] Log de errores en `ImportJob.errors_log` (JSONField).

### Paso 8: Pruebas integradas

- [ ] Probar flujo completo upload → parse → standardize → validate → migrate.
- [ ] Probar con archivo `Indicadores 2025.xls` real (6 hojas).
- [ ] Probar archivos con errores de formato: hojas vacias, columnas faltantes, valores no numericos.
- [ ] Probar con archivo .xlsx para verificar compatibilidad dual.

## Salidas

- Datos importados y trazables en `IndicatorRecord`.
- Registro de errores por fila para correccion.
- ImportJob con estado final `completed` o `failed` y contadores precisos.

## Criterios de aceptacion

- Todo `ImportJob` termina en `completed` o `failed`.
- Nunca migra una fila invalida.
- La migracion es atomica en caso de fallo.
- Las 6 hojas del Excel se parsean correctamente (aprox 120-150 filas de datos totales).
- Cada indicador genera 8 `IndicatorRecord` (uno por variable) por entidad/periodo.

## Errores comunes y solucion

- OOM con archivos grandes: procesar por lotes y `bulk_create`.
- Periodos o entidades no reconocidos: reforzar capa de normalizacion con configuracion externa.
- Hoja con ncols diferentes (Consolidado Municipal tiene 11 cols vs 10): detectar ncols por hoja dinamicamente.
- Valor `45992.0` confundido con dato: el parser debe identificar filas de cabecera por posicion, no por contenido.
- Nombre de indicador con variaciones ortograficas ("Utilidad " vs "Utilidad o Perdida"): mapeo case-insensitive con normalizacion de espacios.
