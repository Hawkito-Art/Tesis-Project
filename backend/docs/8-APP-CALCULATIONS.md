# 8 - Proceso del Modulo Calculations

## Objetivo

Implementar motor de calculo para acumulado, correlacion y estimado con manejo de errores.

## Prerequisitos

- [7-APP-INGESTION](7-APP-INGESTION.md)
- [6-APP-INDICATORS](6-APP-INDICATORS.md)

## Entradas

- `IndicatorRecord` validos por entidad y periodo.

## Pasos

### Paso 1: Modelo y estados

- [ ] Implementar `Calculation` y `CalculationResult`.
- [ ] Definir estados: `pending`, `running`, `completed`, `failed`.

### Paso 2: Servicio de calculo

- [ ] Crear `CalculationService.calcular_acumulado(entity, period)`.
- [ ] Crear `CalculationService.calcular_correlacion(entity, period)`.
- [ ] Crear `CalculationService.calcular_estimado(entity, period)`.

### Paso 3: Manejo de errores

- [ ] Detectar division por cero y guardar `is_error=True`.
- [ ] Persistir mensaje tecnico en `error_message`.
- [ ] No abortar toda corrida por un error puntual no critico.

### Paso 4: Endpoints

- [ ] `POST /api/calculations/run/`.
- [ ] `GET /api/calculations/{id}/`.
- [ ] `GET /api/calculations/{id}/results/`.

### Paso 5: Consistencia y concurrencia

- [ ] Evitar ejecutar mismo calculo simultaneo para misma llave.
- [ ] Asegurar consistencia transaccional por corrida.

### Paso 6: Pruebas

- [ ] Unit tests por cada tipo de calculo.
- [ ] Tests de error por division por cero.
- [ ] API tests para ejecucion y consulta de resultados.

## Salidas

- Resultados calculados auditables por corrida.

## Criterios de aceptacion

- Cada corrida deja traza de inicio y fin.
- Resultados y errores quedan persistidos.
- Endpoints responden estado y detalle correcto.

## Errores comunes y solucion

- Formula hardcodeada en vista: mover logica a `services.py`.
- No registrar fallo parcial: usar `is_error` por resultado.
