# 2B - Serializers y Contratos API

## Objetivo

Definir contratos request/response y validaciones de entrada/salida para cada modulo.

## Prerequisitos

- [2A-MODELS](2A-MODELS.md) implementado.
- Convenciones de errores en [12-ERRORS](12-ERRORS.md).

## Entradas

- Modelos de las apps.
- Endpoints definidos en [10-API-REFERENCE](10-API-REFERENCE.md).

## Pasos

- [ ] Crear serializers por app con separacion de lectura/escritura cuando sea necesario.
- [ ] Validar campos clave:
  - email unico en usuarios.
  - mes en rango 1-12 para periodos.
  - montos no negativos cuando aplique.
- [ ] Implementar validaciones cruzadas:
  - entidad y periodo existentes antes de crear presupuesto.
  - variable permitida para indicador antes de crear record.
- [ ] Estandarizar formato decimal en respuestas economicas.
- [ ] Evitar sobreexponer campos internos (`file_path`, trazas sensibles).
- [ ] Agregar pruebas de serializer para errores de contrato.

## Contratos minimos por dominio

- Auth: login/refresh/logout/me.
- Catalog: entidades y periodos.
- Budget: presupuestos y partidas.
- Indicators: indicadores, variables, records.
- Ingestion: upload, validate, migrate.
- Calculations: run y resultados.
- Reports: reportes, stats y clasificaciones.

## Salidas

- Contratos API consistentes y validables.
- Mensajes de error uniformes.

## Criterios de aceptacion

- Cada endpoint tiene serializer definido.
- Los casos invalidos retornan `400` con detalle claro.
- Los tipos de datos de salida son estables.

## Errores comunes y solucion

- Validacion duplicada en vista y serializer: mover la regla al serializer.
- Campos readonly sobreescritos: separar `CreateSerializer` y `DetailSerializer`.
