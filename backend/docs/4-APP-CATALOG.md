# 4 - Proceso del Modulo Catalog

## Objetivo

Construir catalogos base de entidades y periodos, base para todos los demas modulos.

## Prerequisitos

- [2A-MODELS](2A-MODELS.md)
- [2C-PERMISSIONS](2C-PERMISSIONS.md)

## Entradas

- Definiciones de `Entity` y `Period` del plan.

## Pasos

- [ ] Implementar modelos `Entity` y `Period` con constraints unicos.
- [ ] Crear serializers con validacion de formato y rango de mes.
- [ ] Exponer CRUD:
  - `GET/POST /api/entities/`
  - `GET/PATCH/DELETE /api/entities/{id}/`
  - `GET/POST /api/periods/`
  - `GET/PATCH /api/periods/{id}/`
- [ ] Aplicar permisos: escritura admin, lectura autenticados autorizados.
- [ ] Agregar filtros por codigo, nombre, ano y mes.
- [ ] Incorporar paginacion y ordenamiento.
- [ ] Crear tests de constraints y permisos.

## Salidas

- Catalogos consistentes para relacionar presupuestos, indicadores e ingesta.

## Criterios de aceptacion

- No se permiten codigos de entidad duplicados.
- No se permite duplicar periodo `(year, month, period_type)`.
- Endpoints listan y filtran correctamente.

## Errores comunes y solucion

- Mes fuera de rango: validar en serializer y modelo.
- Hard delete accidental de entidad: usar `is_active` cuando aplique politica.
