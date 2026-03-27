# 1 - Arquitectura del Backend

## Objetivo

Definir estructura tecnica, fronteras por app y convenciones para un desarrollo consistente.

## Prerequisitos

- Haber completado [0-SETUP](0-SETUP.md).
- Conocer [PLAN_DE_ACCION](../PLAN_DE_ACCION.md).

## Alcance arquitectonico

Apps objetivo:
- `accounts`
- `catalog`
- `budget`
- `indicators`
- `ingestion`
- `calculations`
- `reports`

Estructura sugerida por app:
- `models.py`
- `serializers.py`
- `views.py`
- `urls.py`
- `permissions.py`
- `services.py`
- `tests/`

## Flujo funcional macro

1. Autenticacion y autorizacion.
2. Carga y gestion de catalogos base.
3. Registro de presupuestos y partidas.
4. Ingesta de Excel hacia staging.
5. Validacion y migracion a registros definitivos.
6. Calculos economicos por entidad y periodo.
7. Reportes, estadisticas y clasificacion.

## Convenciones

- Nombres de endpoints en plural: `/api/entities/`.
- Soft delete cuando aplique (`is_active=False`).
- Campos de auditoria: `created_at`, `updated_at`.
- Errores API con formato estandar (ver [12-ERRORS](12-ERRORS.md)).
- Permisos declarados por vista y testeados.

## Pasos

- [ ] Crear carpeta `apps/` dentro del proyecto Django.
- [ ] Crear las 7 apps con `startapp`.
- [ ] Registrar apps en `INSTALLED_APPS`.
- [ ] Definir prefijos de rutas por modulo.
- [ ] Configurar DRF, JWT, paginacion y filtros globales.
- [ ] Definir estrategia de logs y trazabilidad.

## Salidas

- Mapa de apps claro.
- Convenciones compartidas por todo el equipo.
- Ruta para implementar por iteraciones sin conflictos.

## Criterios de aceptacion

- Cada app tiene responsabilidades no solapadas.
- Todas las rutas API estan agrupadas por dominio.
- Las reglas de permisos y errores estan centralizadas.

## Errores comunes y solucion

- Mezclar logica de negocio en vistas: mover a `services.py`.
- Duplicar validaciones entre serializer y modelo: definir unica fuente por regla.
