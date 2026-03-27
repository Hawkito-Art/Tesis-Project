# 7 - Proceso del Modulo Ingestion

## Objetivo

Implementar pipeline completo de importacion de Excel: carga, parseo, validacion y migracion.

## Prerequisitos

- [4-APP-CATALOG](4-APP-CATALOG.md)
- [5-APP-BUDGET](5-APP-BUDGET.md)
- [6-APP-INDICATORS](6-APP-INDICATORS.md)

## Entradas

- Archivos `.xlsx` o `.xls`.
- Catalogos de entidades, periodos e indicadores ya cargados.

## Pasos

### Paso 1: Upload de documento

- [ ] Implementar `Document` y endpoint `POST /api/documents/upload/`.
- [ ] Validar extension, tamano y usuario autenticado.
- [ ] Registrar metadata: nombre, tipo, tamano, ruta.

### Paso 2: Crear trabajo de importacion

- [ ] Crear `ImportJob` asociado a documento.
- [ ] Inicializar estado `uploaded`.

### Paso 3: Parseo a staging

- [ ] Leer Excel con `openpyxl` o `pandas`.
- [ ] Insertar filas en `DocumentDetail` con `raw_value` y `parsed_value`.
- [ ] Actualizar contadores de filas en `ImportJob`.

### Paso 4: Estandarizacion

- [ ] Normalizar codigos/nombres de entidad.
- [ ] Normalizar indicador y periodo.
- [ ] Marcar discrepancias para validacion.

### Paso 5: Validacion

- [ ] Endpoint `POST /api/import-jobs/{id}/validate/`.
- [ ] Marcar `is_valid` y `validation_error` por fila.
- [ ] Actualizar totales validos/invalidos en `ImportJob`.

### Paso 6: Migracion a records

- [ ] Endpoint `POST /api/import-jobs/{id}/migrate/`.
- [ ] Migrar solo filas validas a `IndicatorRecord` dentro de transaccion.
- [ ] Guardar trazabilidad con `source_document` e `import_job`.

### Paso 7: Errores y reintentos

- [ ] Exponer `GET /api/import-jobs/{id}/errors/`.
- [ ] Permitir correccion y reintento de validacion/migracion.

### Paso 8: Pruebas integradas

- [ ] Probar flujo completo upload -> validate -> migrate.
- [ ] Probar archivos con errores de formato y datos.

## Salidas

- Datos importados y trazables en `IndicatorRecord`.
- Registro de errores por fila para correccion.

## Criterios de aceptacion

- Todo `ImportJob` termina en `completed` o `failed`.
- Nunca migra una fila invalida.
- La migracion es atomica en caso de fallo.

## Errores comunes y solucion

- OOM con archivos grandes: procesar por lotes y `bulk_create`.
- Periodos o entidades no reconocidos: reforzar capa de normalizacion.
