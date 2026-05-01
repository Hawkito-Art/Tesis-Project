# Iteración 0 — Preparación

## Objetivo
Dejar el entorno listo y verificar el estado base del proyecto antes de comenzar cambios funcionales.

## Tareas
- Activar o crear `venv` en `backend/venv`.
- Instalar dependencias listadas en `docs/0-SETUP.md`.
- Ejecutar `python manage.py check`.
- Ejecutar `python manage.py showmigrations`.
- Ejecutar `python manage.py test -v 2`.

## Estimación
0.5 a 1 hora.

## Criterios de aceptación
- Todos los tests existentes pasan o quedan documentados los fallos conocidos.
- El estado de migraciones queda identificado.

## Comandos
```bash
source backend/venv/bin/activate
cd backend/tesis
python manage.py check
python manage.py showmigrations
python manage.py test -v 2
```
