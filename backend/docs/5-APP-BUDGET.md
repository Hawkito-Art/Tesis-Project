# 5 - Proceso del Modulo Budget

## Objetivo

Implementar presupuestos y partidas para soportar calculos e indicadores economicos.

## Prerequisitos

- [4-APP-CATALOG](4-APP-CATALOG.md)
- [2A-MODELS](2A-MODELS.md)

## Entradas

- Modelos `Budget` y `BudgetItem`.
- Los indicadores del Excel (Ventas, Ingresos, Gastos, Utilidad) se calculan parcialmente a partir de datos presupuestarios.

## Pasos

- [ ] Crear `Budget` con FK a entidad y periodo.
- [ ] Definir estados de presupuesto: `draft`, `approved`, `closed`.
- [ ] Crear `BudgetItem` con tipo (`ingreso`, `gasto`) y clasificacion.
- [ ] Aplicar constraint unico de partida por presupuesto.
- [ ] Implementar CRUD de presupuestos y partidas.
- [ ] Habilitar filtros por entidad, periodo, tipo y codigo.
- [ ] Validar montos y reglas de negocio minimas.
- [ ] Escribir pruebas de integridad y permisos.

## Salidas

- Presupuestos estructurados y consultables.
- Datos base para formula de indicadores.

## Criterios de aceptacion

- No se crean dos presupuestos para misma entidad/periodo.
- No se duplican partidas por codigo dentro de un mismo presupuesto.
- Listados devuelven totales y campos esperados.

## Errores comunes y solucion

- Campos monetarios con precision insuficiente: usar `DecimalField` coherente.
- Inconsistencia de estado: validar transiciones permitidas.
