# Iteración 2 — Ingestión

## Objetivo
Completar el parser XLSX y el proceso de upsert para la importación de indicadores.

## Tareas
- Revisar `apps.ingestion.services` y localizar el parser incompleto.
- Implementar parsing robusto.
  - Validar columnas esperadas: `Entity`, `Period`, `Indicator`, `Variable`, `Value`.
  - Manejar filas con errores y acumular un reporte de validación.
  - Transformar tipos y normalizar códigos de entidad e indicador.
- Implementar `upsert_indicator_records_from_import_job()` completo.
  - Validar existencia de `Entity` y `Period`.
  - Crear o actualizar `IndicatorRecord` con `source=SOURCE_IMPORTED`.
  - Ejecutar el proceso de forma transaccional y reportar errores por fila.
- Añadir pruebas unitarias para parseo y upsert.

## Estimación
1.5 a 3 horas.

## Criterios de aceptación
- Un archivo de muestra se importa correctamente y crea o actualiza `IndicatorRecord`.
- Los errores por fila quedan listados sin romper todo el job.

## Tests recomendados
```bash
python manage.py test ingestion.tests -v 2
```
