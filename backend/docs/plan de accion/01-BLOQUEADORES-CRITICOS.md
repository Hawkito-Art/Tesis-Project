# Iteración 1 — Bloqueadores críticos

## Objetivo
Habilitar la comunicación con el frontend y dejar el esquema de base de datos aplicado.

## Tareas
1. Configurar CORS globalmente.
   - Instalar `django-cors-headers`.
   - Agregarlo a `INSTALLED_APPS` y `MIDDLEWARE`.
   - Definir `CORS_ALLOWED_ORIGINS` o `CORS_ALLOW_ALL_ORIGINS` según ambiente.
2. Aplicar migraciones y verificar esquema.
   - Ejecutar `python manage.py migrate`.
   - Revisar constraints e índices.

## Estimación
1 a 2 horas.

## Criterios de aceptación
- El frontend puede hacer llamadas en entorno de desarrollo.
- La base de datos migra sin errores y las tablas esperadas están presentes.

## Comandos
```bash
pip install django-cors-headers
python manage.py migrate
```
