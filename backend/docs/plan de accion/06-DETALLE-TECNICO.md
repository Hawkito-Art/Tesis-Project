# Detalle técnico por tarea

## Archivos a cambiar
- `settings.py`: agregar `corsheaders` a `INSTALLED_APPS` y `MIDDLEWARE`, y definir `CORS_ALLOWED_ORIGINS`.
- `apps/ingestion/services.py`: completar funciones de parseo y upsert.
- `apps/indicators/services.py`: implementar validaciones y cálculos.
- `apps/reports/views.py`: completar handlers que hoy devuelven `501`.
- `backend/tesis/urls.py`: montar rutas de Swagger si se agrega la documentación OpenAPI.

## Pruebas recomendadas
- Unitarias: `python manage.py test <app>.tests`.
- Integración: flujos `ingestion -> calculations -> reports` con fixtures.
