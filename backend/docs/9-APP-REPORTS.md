# 9 - Proceso del Modulo Reports

## Objetivo

Construir reportes, estadisticas y clasificaciones de cumplimiento presupuestario.

## Prerequisitos

- [8-APP-CALCULATIONS](8-APP-CALCULATIONS.md)
- [6-APP-INDICATORS](6-APP-INDICATORS.md)

## Entradas

- Resultados de calculo y registros de indicadores.

## Pasos

### Paso 1: Reportes

- [ ] Implementar endpoint `POST /api/reports/` para generar informe.
- [ ] Implementar `GET /api/reports/` y `GET /api/reports/{id}/`.
- [ ] Definir formato de salida (resumen, detalle, metadatos).

### Paso 2: Estadisticas

- [ ] Implementar servicio de tendencias por entidad/periodo/indicador.
- [ ] Exponer `GET /api/stats/` con datos agregados para graficos.

### Paso 3: Clasificacion

- [ ] Implementar `EntityClassification`.
- [ ] Exponer `POST /api/classifications/calculate/`.
- [ ] Exponer `GET /api/classifications/` y detalle.

### Paso 4: Pruebas

- [ ] Validar coherencia estadistica con datos de entrada.
- [ ] Probar filtros de reportes y clasificaciones.
- [ ] Verificar tiempos de respuesta aceptables.

## Salidas

- Reportes generados bajo demanda.
- Estadisticas listas para consumo frontend.
- Clasificaciones persistidas por periodo.

## Criterios de aceptacion

- Reportes contienen datos trazables a calculos.
- Clasificacion respeta reglas de categoria definidas.
- Endpoints soportan filtros principales sin error.

## Errores comunes y solucion

- Regla de clasificacion ambigua: versionar criterios y documentar cambios.
- Reportes sin contexto temporal: exigir periodo en filtros.
