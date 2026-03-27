# 6 - Proceso del Modulo Indicators

## Objetivo

Administrar catalogo de indicadores (con grupos y unidades), variables y registros para analisis economico.

## Prerequisitos

- [4-APP-CATALOG](4-APP-CATALOG.md)
- [5-APP-BUDGET](5-APP-BUDGET.md)

## Entradas

- Modelos `IndicatorGroup`, `Indicator`, `IndicatorVariable`, `IndicatorRecord`.
- Indicadores y grupos derivados del Excel `Indicadores 2025.xls` (ver PLAN_DE_ACCION §4.3).

## Pasos

### Paso 1: Grupos de indicadores

- [ ] Crear `IndicatorGroup` con 3 registros base:
  - `fundamental` — Indicadores Fundamentales (order=1)
  - `limite` — Indicadores Limites (order=2)
  - `otro` — Otros Indicadores (order=3)
- [ ] Exponer CRUD: `GET/POST /api/indicator-groups/`, `GET/PATCH/DELETE /api/indicator-groups/{id}/`

### Paso 2: Indicadores con unidad y grupo

- [ ] Crear `Indicator` con `unit` (MP, U, p, peso, Coef) y FK a `IndicatorGroup`.
- [ ] Seed data con los 13 indicadores del Excel (ver PLAN_DE_ACCION §4.3):
  - Fundamentales: Ventas Totales (MP), Total de Ingresos (MP), Total de Gastos (MP), Utilidad o Perdida (MP)
  - Limites: Gasto de Salario x peso V.A.B (peso)
  - Otros: Gasto Total x peso de Ing.Total (peso), Valor Agregado Bruto (U), Utilidad Antes Imp. x $ de VAB (peso), Fondo de Salario Total (MP), Promedio de Trabajadores (U), Productividad del Trabajo (p), Salario Medio (p), Correlacion Salario Medio/Product. (Coef)
- [ ] Constraint unico por `code`.

### Paso 3: Variables estandar

- [ ] Crear `IndicatorVariable` con `label` y constraint `(indicator, name)`.
- [ ] Cada indicador recibe las 8 variables estandar:
  - `plan_anual` (PLAN ANO)
  - `ano_anterior` (Ano Anter. igual per.)
  - `plan_acumulado` (PLAN acumulado)
  - `real_acumulado` (REAL acumulado)
  - `porcentaje_r_p` (% R/P)
  - `real_aa` (R/AA)
  - `estimado_prox_mes` (Estimado proximo mes)
  - `estimado_cierre_ano` (Estimado cierre/ano)

### Paso 4: Registros de indicadores

- [ ] Crear `IndicatorRecord` con origen (`manual`, `imported`, `calculated`).
- [ ] Constraint unico: `(entity, indicator, period, variable_name)`.
- [ ] Implementar consulta con filtros por entidad, indicador, grupo, periodo y variable_name.
- [ ] Agregar trazabilidad a documento/import job cuando aplique.

### Paso 5: Endpoints y pruebas

- [ ] Implementar CRUD para indicadores y variables.
- [ ] `GET /api/indicator-records/` con filtros compuestos.
- [ ] Validar que variable corresponda al indicador.
- [ ] Escribir pruebas de filtros, unicidad y grupos.

## Salidas

- Estructura de indicadores con grupos y unidades, lista para ingestas y calculos.
- Variables estandar mapeadas a columnas del Excel fuente.

## Criterios de aceptacion

- Los 3 grupos existen y los indicadores referencian su grupo correcto.
- Cada indicador tiene su `unit` correcto (MP, U, p, peso, Coef).
- Las 8 variables estandar existen para cada indicador.
- `GET /api/indicator-records/` filtra por grupo ademas de entidad/indicador/periodo.
- Se preserva origen de los datos para auditoria.

## Errores comunes y solucion

- Guardar record con variable inexistente: validar en serializer.
- Mezclar records manuales con importados sin marca: usar `data_origin` obligatorio.
- Indicador sin grupo asignado: FK obligatoria, migracion con default.
- Unidad incorrecta: validar contra choices en modelo y serializer.
