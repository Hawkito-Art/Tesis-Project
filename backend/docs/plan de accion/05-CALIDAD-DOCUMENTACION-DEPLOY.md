# Iteración 5 — Calidad, documentación y deploy

## Objetivo
Cerrar el proyecto con documentación, validaciones y soporte de despliegue.

## Tareas
- Agregar `drf-spectacular` o `drf-yasg` para OpenAPI/Swagger.
- Ajustar la configuración final de CORS para prod y staging.
- Personalizar `admin.py` para `Entity`, `Indicator` y `Budget`.
- Crear fixtures mínimos en `fixtures/initial_data.json` con entidades y periods.
- Añadir checks de lint (`black`, `isort`, `flake8`) y ajustar estilo.
- Añadir CI con GitHub Actions para tests y lint.

## Estimación
4 a 8 horas.

## Criterios de aceptación
- La documentación OpenAPI está disponible en `/api/schema/` y Swagger UI.
- La CI queda verde en PRs.
