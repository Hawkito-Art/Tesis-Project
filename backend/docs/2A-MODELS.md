# 2A - Modelos y Base de Datos

## Objetivo

Implementar los modelos de dominio y restricciones de integridad definidos en el plan.

## Prerequisitos

- [1-ARQUITECTURA](1-ARQUITECTURA.md) definido.
- Apps creadas y registradas en Django.

## Entradas

- Tablas y campos definidos en [PLAN_DE_ACCION](../PLAN_DE_ACCION.md).

## Pasos

### Fase 1: Seguridad y acceso

- [ ] Crear `CustomUser` (email unico, `email_verified`, `is_active`).
- [ ] Crear `Role` y `UserRole` con constraint unico `(user, role)`.
- [ ] Crear `LoginAttempt` y `BlockedIP` con indices por email/IP.

### Fase 2: Dominio base

- [ ] Crear `Entity` con `code` unico e `is_consolidated` para la entidad agregada.
- [ ] Crear `Period` con constraint `(year, month, period_type)`.

### Fase 3: Presupuestos e indicadores

- [ ] Crear `Budget` con constraint `(entity, period)`.
- [ ] Crear `BudgetItem` con constraint compuesto por presupuesto, tipo y codigo.
- [ ] Crear `IndicatorGroup` (fundamental, limite, otro) con campo `order`.
- [ ] Crear `Indicator` con `unit` (MP, U, p, peso, Coef), FK a `IndicatorGroup` y constraint `(indicator, name)`.
- [ ] Crear `IndicatorVariable` con `label` y constraint `(indicator, name)`. Variables estandar: plan_anual, ano_anterior, plan_acumulado, real_acumulado, porcentaje_r_p, real_aa, estimado_prox_mes, estimado_cierre_ano.
- [ ] Crear `IndicatorRecord` con constraint `(entity, indicator, period, variable_name)`.

### Fase 4: Ingesta y calculos

- [ ] Crear `Document`, `ImportJob`, `DocumentDetail` (staging).
- [ ] Crear `Calculation` y `CalculationResult` con constraint unico por variable.

### Fase 5: Reportes y clasificacion

- [ ] Crear `EntityClassification` con constraint `(entity, period, classification_type)`.

### Fase 6: Migraciones

- [ ] Generar migraciones por app.
- [ ] Ejecutar `python manage.py migrate`.
- [ ] Verificar constraints e indices en DB.

## Salidas

- Esquema de datos completo y consistente.
- Integridad garantizada por constraints e indices.

## Criterios de aceptacion

- Todas las tablas del plan existen.
- Los constraints compuestos se aplican correctamente.
- Las FK invalidas se rechazan con error controlado.

## Errores comunes y solucion

- Constraint faltante: agregar en `Meta.constraints` y nueva migracion.
- FK circular mal definida: usar string reference temporal y ordenar migraciones.
