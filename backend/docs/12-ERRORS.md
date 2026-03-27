# 12 - Estandar de Errores y Observabilidad

## Objetivo

Definir formato unico de errores para facilitar integracion y soporte.

## Prerequisitos

- DRF configurado.
- Politica de permisos definida.

## Formato de error recomendado

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos enviados no son validos",
    "details": {
      "field": ["Este campo es obligatorio"]
    },
    "trace_id": "optional-correlation-id"
  }
}
```

## Mapa de codigos HTTP

- `400`: error de validacion o regla de negocio.
- `401`: token ausente o invalido.
- `403`: rol/permisos insuficientes.
- `404`: recurso no encontrado.
- `409`: conflicto de unicidad.
- `422`: dato semantico invalido en procesos complejos.
- `500`: error interno no controlado.

## Pasos de implementacion

- [ ] Definir custom exception handler DRF.
- [ ] Estandarizar `code` por tipo de fallo.
- [ ] Incluir `trace_id` para correlacion de logs.
- [ ] Mapear errores de base de datos a respuestas legibles.
- [ ] Loggear errores con contexto de endpoint y usuario.

## Criterios de aceptacion

- Toda respuesta de error sigue un formato unico.
- El frontend puede manejar errores por `code` sin parseo fragil.

## Errores comunes y solucion

- Exponer stacktrace en produccion: desactivar y loggear internamente.
- Mensajes inconsistentes entre endpoints: usar codigos centralizados.
