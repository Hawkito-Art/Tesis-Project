# 2C - Permisos y Seguridad por Endpoint

## Objetivo

Definir autorizacion por roles para evitar accesos indebidos a datos sensibles.

## Prerequisitos

- [1-ARQUITECTURA](1-ARQUITECTURA.md)
- [2B-SERIALIZERS](2B-SERIALIZERS.md)

## Roles base

- `admin`: gestion completa.
- `analyst`: lectura amplia y ejecucion de procesos permitidos.
- `operator`: carga de datos y operaciones limitadas.

## Matriz resumida de acceso

- Auth (`/api/auth/*`): autenticado segun endpoint.
- Users/Roles: solo `admin` para crear, editar y desactivar.
- Catalog (`entities`, `periods`): `admin` escritura, `analyst/operator` lectura.
- Budget/Indicators: `admin` escritura, `analyst` lectura y edicion controlada segun politica.
- Ingestion (`upload`, `validate`, `migrate`): `admin` y `operator`.
- Calculations (`run`, `results`): `admin` y `analyst`.
- Reports/Stats/Classifications: lectura para `admin` y `analyst`.

## Pasos

- [ ] Implementar clases de permisos DRF por modulo.
- [ ] Aplicar permisos por accion (`list`, `create`, `update`, `destroy`).
- [ ] Proteger endpoints de administracion con rol `admin`.
- [ ] Restringir datos por contexto cuando aplique.
- [ ] Registrar eventos de acceso denegado para auditoria.
- [ ] Agregar pruebas por rol para `401` y `403`.

## Salidas

- Endpoints con politica de acceso explicita.
- Menor riesgo de exposicion de datos.

## Criterios de aceptacion

- Ningun endpoint sensible queda publico.
- Casos sin token retornan `401`.
- Casos con rol insuficiente retornan `403`.

## Errores comunes y solucion

- Validar solo en frontend: mover control al backend con DRF permissions.
- Usar un permiso global demasiado amplio: definir permisos por vista/accion.
