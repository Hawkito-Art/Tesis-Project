# 6 - Proceso del Modulo Indicators

## Objetivo

Administrar catalogo de indicadores, variables y registros para analisis economico.

## Prerequisitos

- [4-APP-CATALOG](4-APP-CATALOG.md)
- [5-APP-BUDGET](5-APP-BUDGET.md)

## Entradas

- Modelos `Indicator`, `IndicatorVariable`, `IndicatorRecord`.

## Pasos

- [ ] Crear `Indicator` con tipo y metodo de calculo.
- [ ] Crear `IndicatorVariable` y constraint `(indicator, name)`.
- [ ] Crear `IndicatorRecord` con origen (`manual`, `imported`, `calculated`).
- [ ] Implementar CRUD para indicadores y variables.
- [ ] Implementar consulta de records con filtros por entidad, indicador y periodo.
- [ ] Validar que variable corresponda al indicador.
- [ ] Agregar trazabilidad a documento/import job cuando aplique.
- [ ] Escribir pruebas de filtros y unicidad de records.

## Salidas

- Estructura de indicadores lista para ingestas y calculos.

## Criterios de aceptacion

- Indicadores y variables no se duplican segun constraints.
- `GET /api/indicator-records/` filtra correctamente.
- Se preserva origen de los datos para auditoria.

## Errores comunes y solucion

- Guardar record con variable inexistente: validar en serializer.
- Mezclar records manuales con importados sin marca: usar `data_origin` obligatorio.
