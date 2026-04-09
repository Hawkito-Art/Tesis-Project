# 10 - API Reference

## Objetivo

Consolidar endpoints del backend y su uso esperado por frontend e integraciones.

## Prerequisitos

- Modulos de [3](3-APP-ACCOUNTS.md) a [9](9-APP-REPORTS.md) implementados.

## Convenciones

- Base path: `/api/`
- Autenticacion: `Authorization: Bearer <token>`
- Formato de error: ver [12-ERRORS](12-ERRORS.md)

## Endpoints principales

### Auth

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

#### Status codes esperados (Auth)

- `200 OK`: login/refresh/logout/me exitoso.
- `400 Bad Request`: payload inválido (campos requeridos, token refresh inválido).
- `401 Unauthorized`: credenciales inválidas o acceso sin token en endpoints protegidos.
- `403 Forbidden`: usuario autenticado pero con email no verificado.
- `429 Too Many Requests`: usuario/IP bloqueado por exceso de intentos fallidos.

### Users y Roles

- `GET/POST /api/users/`
- `GET/PATCH/DELETE /api/users/{id}/`
- `GET/POST /api/roles/`
- `GET/PATCH/DELETE /api/roles/{id}/`

### Catalog

- `GET/POST /api/entities/`
- `GET/PATCH/DELETE /api/entities/{id}/`
- `GET/POST /api/periods/`
- `GET/PATCH /api/periods/{id}/`

#### Status codes esperados (Catalog)

- `200 OK`: lecturas (`list/retrieve`) y `PATCH` exitoso.
- `201 Created`: creacion exitosa de `Entity` o `Period`.
- `204 No Content`: eliminacion exitosa de `Entity`.
- `400 Bad Request`: payload invalido o violacion de constraints de negocio.
- `401 Unauthorized`: acceso sin token.
- `403 Forbidden`: usuario autenticado sin privilegios de escritura (solo admin escribe).

#### Filtros, orden y paginacion (Catalog)

- `GET /api/entities/`
  - filtros: `code`, `name`, `type`, `is_consolidated`, `is_active`
  - busqueda: `search` sobre `code` y `name`
  - orden: `ordering` en `id`, `code`, `name`, `type`, `created_at`, `updated_at`
  - paginacion: `page` (PageNumberPagination global)
- `GET /api/periods/`
  - filtros: `year`, `month`, `period_type`, `is_active`
  - orden: `ordering` en `id`, `year`, `month`, `period_type`, `created_at`
  - paginacion: `page` (PageNumberPagination global)

### Budget

- `GET/POST /api/budgets/`
- `GET/PATCH /api/budgets/{id}/`
- `GET/POST /api/budget-items/`
- `GET/PATCH/DELETE /api/budget-items/{id}/`

### Indicators

- `GET/POST /api/indicators/`
- `GET/PATCH/DELETE /api/indicators/{id}/`
- `GET/POST /api/indicator-variables/`
- `GET/PATCH/DELETE /api/indicator-variables/{id}/`
- `GET/POST /api/indicator-records/`
- `GET/PATCH/DELETE /api/indicator-records/{id}/`

### Ingestion

- `GET /api/documents/`
- `POST /api/documents/upload/`
- `GET/DELETE /api/documents/{id}/`
- `GET /api/import-jobs/`
- `GET /api/import-jobs/{id}/`
- `POST /api/import-jobs/{id}/validate/`
- `POST /api/import-jobs/{id}/migrate/`
- `GET /api/import-jobs/{id}/errors/`

### Calculations y Export

- `GET /api/calculations/`
- `POST /api/calculations/run/`
- `GET /api/calculations/{id}/`
- `GET /api/calculations/{id}/results/`
- `POST /api/exports/xlsx/`

### Reports

- `GET/POST /api/reports/`
- `GET /api/reports/{id}/`
- `GET /api/stats/`
- `GET /api/classifications/`
- `POST /api/classifications/calculate/`
- `GET /api/classifications/{id}/`

## Checklist de calidad de contrato

- [ ] Cada endpoint tiene serializer de entrada y salida.
- [ ] Cada endpoint tiene permisos definidos.
- [ ] Cada endpoint documenta codigos HTTP esperados.
- [ ] Endpoints de lista incluyen paginacion y filtros.
