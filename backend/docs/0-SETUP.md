# 0 - Setup del Entorno

## Objetivo

Preparar un entorno local reproducible para iniciar el desarrollo del backend Django REST.

## Prerequisitos

- Linux con Python 3.11+.
- Acceso al repositorio.
- `pip` y `venv` disponibles.

## Entradas

- Codigo fuente del repositorio.
- Variables de entorno de desarrollo.

## Pasos

- [ ] Verificar version de Python:

```bash
python --version
```

- [ ] Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate
```

- [ ] Instalar dependencias base:

```bash
pip install Django==6.0.3 djangorestframework==3.17.0
pip install djangorestframework-simplejwt openpyxl pandas
pip install black isort flake8 pytest pytest-django
```

- [ ] Crear archivo de variables de entorno `.env` con al menos:

```env
DEBUG=True
SECRET_KEY=replace-me
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7
```

- [ ] Ejecutar migraciones iniciales:

```bash
cd tesis
python manage.py migrate
```

- [ ] Crear superusuario de desarrollo:

```bash
python manage.py createsuperuser
```

- [ ] Arrancar servidor local:

```bash
python manage.py runserver
```

- [ ] Verificar que responde `/admin/` y futura ruta `/api/health/`.

## Salidas

- Entorno virtual activo.
- Dependencias instaladas.
- Base de datos inicializada.
- Proyecto corriendo en local.

## Criterios de aceptacion

- El servidor inicia sin errores.
- Se puede acceder al admin con el superusuario.
- `python manage.py check` no reporta problemas criticos.

## Errores comunes y solucion

- Error `command not found: python`: instalar Python o usar `python3`.
- Error de migraciones: borrar `db.sqlite3` solo en desarrollo y reintentar.
- Error de paquete faltante: reinstalar en el `venv` activo.
