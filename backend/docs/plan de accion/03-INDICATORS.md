# Iteración 3 — Indicators

## Objetivo
Implementar la lógica de negocio de indicadores.

## Tareas
- Implementar `apps.indicators.services`.
  - Validaciones por variable y unidad.
  - Cálculos derivados si aplican: porcentaje R/P, real año anterior, estimados.
  - Helper de API para consumo desde `calculations` y `reports`.
- Añadir pruebas unitarias de cada función crítica.

## Estimación
2 a 4 horas.

## Criterios de aceptación
- Las funciones de cálculo devuelven resultados consistentes con casos de ejemplo.
- La integración con `calculations.run_formula_engine()` actualiza `IndicatorRecord` correctamente.
