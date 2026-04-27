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
- `GET/PATCH/DELETE /api/budgets/{id}/`
- `GET/POST /api/budget-items/`
- `GET/PATCH/DELETE /api/budget-items/{id}/`

#### Status codes esperados (Budget)

- `200 OK`: lecturas (`list/retrieve`) y `PATCH` exitoso.
- `201 Created`: creacion exitosa de `Budget` o `BudgetItem`.
- `204 No Content`: eliminacion exitosa de `Budget` o `BudgetItem`.
- `400 Bad Request`: payload invalido, duplicados por constraints unicos o regla de negocio sobre presupuesto `closed`.
- `401 Unauthorized`: acceso sin token.
- `403 Forbidden`: usuario autenticado sin privilegios de escritura (solo admin escribe).

#### Filtros, orden y paginacion (Budget)

- `GET /api/budgets/`
  - filtros: `entity`, `period`, `status`, `is_active`
  - orden: `ordering` en `id`, `created_at`, `updated_at`
  - paginacion: `page` (PageNumberPagination global)
- `GET /api/budget-items/`
  - filtros: `budget`, `item_type`, `code`, `is_active`
  - orden: `ordering` en `id`, `code`, `created_at`, `updated_at`
  - paginacion: `page` (PageNumberPagination global)

### Indicators

- `GET/POST /api/indicators/groups/`
- `GET/PATCH/DELETE /api/indicators/groups/{id}/`
- `GET/POST /api/indicators/`
- `GET/PATCH/DELETE /api/indicators/{id}/`
- `GET/POST /api/indicators/variables/`
- `GET/PATCH/DELETE /api/indicators/variables/{id}/`
- `GET /api/indicators/records/`

#### Status codes esperados (Indicators)

- `200 OK`: lecturas (`list/retrieve`) y actualizaciones (`PATCH`) exitosas.
- `201 Created`: creaciones exitosas (groups/indicators/variables).
- `204 No Content`: eliminaciones exitosas.
- `400 Bad Request`: payload invalido, constraints unicos o mismatch variable↔indicador.
- `401 Unauthorized`: acceso sin token.
- `403 Forbidden`: usuario autenticado sin rol permitido.
- `404 Not Found`: recurso no encontrado.
- `501 Not Implemented`: endpoint de contrato disponible pero implementacion funcional pendiente (fase IND1).

#### Filtros, orden y paginacion (Indicators)

- `GET /api/indicators/records/`
  - filtros: `entity`, `indicator`, `group`, `period`, `variable_name`
  - orden: `ordering` (a definir en implementación IND8)
  - paginacion: `page` (PageNumberPagination global)

### Ingestion

- `POST /api/ingestion/documents/`
- `GET /api/ingestion/import-jobs/{id}/`
- `GET /api/ingestion/import-jobs/{id}/details/`

#### Status codes esperados (Ingestion)

- `200 OK`: consulta de estado de job y detalles por fila.
- `201 Created`: carga de documento exitosa (a implementar en I3).
- `400 Bad Request`: payload invalido, archivo no permitido, metadatos incompletos.
- `401 Unauthorized`: acceso sin token.
- `403 Forbidden`: usuario autenticado sin permisos.
- `404 Not Found`: job no encontrado.
- `501 Not Implemented`: endpoint de contrato disponible pero implementacion funcional pendiente (fase I1).

### Calculations y Export

- `POST /api/calculations/run/`
- `POST /api/exports/xlsx/`

#### Status codes esperados (Calculations)

- `200 OK`: ejecucion solicitada y aceptada (a implementar en I9 segun estrategia final).
- `400 Bad Request`: parametros invalidos (`entity/period`).
- `401 Unauthorized`: acceso sin token.
- `403 Forbidden`: usuario autenticado sin permisos.
- `404 Not Found`: entidad o periodo no existe.
- `501 Not Implemented`: endpoint de contrato disponible pero implementacion funcional pendiente (fase I1).

### Reports

- `GET/POST /api/reports/`
- `GET /api/reports/{id}/`
- `GET /api/stats/`
- `POST /api/classifications/calculate/`
- `GET /api/classifications/`
- `GET /api/classifications/{id}/`

#### Status codes esperados (Reports)

- `200 OK`: lecturas (`list/retrieve`) y cálculo/consulta exitosa de estadísticas/clasificaciones.
- `201 Created`: creación de reporte cuando aplique persistencia en `POST /api/reports/`.
- `400 Bad Request`: payload inválido o filtros inconsistentes.
- `401 Unauthorized`: acceso sin token.
- `403 Forbidden`: usuario autenticado sin rol permitido.
- `404 Not Found`: recurso de reporte/clasificación no encontrado.
- `501 Not Implemented`: endpoint de contrato disponible pero implementación funcional pendiente (fase R1).

#### Filtros (Stats)

- `GET /api/stats/`
  - filtros opcionales: `entity`, `period`, `indicator`
  - respuesta: agregados compactos (`totals`, `records_by_source`, `records_by_indicator`, `average_value_by_indicator`, `latest_calculation`)

#### Filtros (Classifications)

- `GET /api/classifications/`
  - filtros opcionales: `entity`, `period`, `category` (valor de clasificación), `classification_type`
  - orden: `ordering` en `id`, `created_at`, `updated_at`
  - paginación: `page`

## Checklist de calidad de contrato

- [ ] Cada endpoint tiene serializer de entrada y salida.
- [ ] Cada endpoint tiene permisos definidos.
- [ ] Cada endpoint documenta codigos HTTP esperados.
- [ ] Endpoints de lista incluyen paginacion y filtros.
