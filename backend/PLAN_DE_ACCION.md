# Plan de Desarrollo Backend — CAM Alquízar

## 1. Resumen del Plan

Desarrollar el backend Django REST API para gestionar los procesos económicos del Consejo de Administración Municipal de Alquízar, priorizando la iteración 1 (autenticación y usuarios) antes de tocar datos sensibles.

## 2. Apps Django

```
backend/tesis/
├── manage.py
├── tesis/                          # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── apps/
    ├── __init__.py
    ├── accounts/                   # Autenticación, usuarios, roles (HU1-HU5)
    ├── catalog/                    # Entidades y períodos (dominio base)
    ├── budget/                     # Presupuestos y partidas (HU14)
    ├── indicators/                 # Indicadores y variables (HU10, HU14)
    ├── ingestion/                  # Importación/estandarización/exportación (HU6-HU9, HU15)
    ├── calculations/               # Motor de cálculos (HU11-HU13)
    └── reports/                    # Reportes, estadísticas, clasificación (HU16-HU18)
```

## 3. Modelo de Base de Datos

### 3.1 users
| Campo | Tipo | Notas |
|-------|------|-------|
| id | AutoField | PK |
| email | EmailField | Único, indexed |
| password | CharField | Hash Django |
| first_name | CharField | |
| last_name | CharField | |
| is_active | BooleanField | Soft delete (HU5) |
| email_verified | BooleanField | HU1 |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

### 3.2 roles
| Campo | Tipo |
|-------|------|
| id | AutoField |
| name | CharField(50), único |
| permissions | JSONField | opcional |

### 3.3 user_roles
| Campo | Tipo |
|-------|------|
| id | AutoField |
| user | FK → users |
| role | FK → roles |
| assigned_at | DateTimeField |

Único compuesto: (user, role)

### 3.4 login_attempts
| Campo | Tipo |
|-------|------|
| id | AutoField |
| email | EmailField, indexed |
| ip_address | GenericIPAddressField |
| attempted_at | DateTimeField |
| successful | BooleanField |

### 3.5 blocked_ips
| Campo | Tipo |
|-------|------|
| id | AutoField |
| ip_address | GenericIPAddressField, único |
| blocked_until | DateTimeField |
| reason | TextField | opcional |

### 3.6 entities
| Campo | Tipo |
|-------|------|
| id | AutoField |
| code | CharField(20), único |
| name | CharField(200) |
| type | CharField(50) | unidad presupuestada, etc. |
| is_active | BooleanField |
| created_at | DateTimeField |
| updated_at | DateTimeField |

### 3.7 periods
| Campo | Tipo |
|-------|------|
| id | AutoField |
| year | PositiveIntegerField |
| month | PositiveIntegerField (1-12) |
| period_type | CharField(20) | mensual, cierre_anual |
| is_closed | BooleanField |

Único compuesto: (year, month, period_type)

### 3.8 budgets
| Campo | Tipo |
|-------|------|
| id | AutoField |
| entity | FK → entities |
| period | FK → periods |
| plan_year | PositiveIntegerField | año del plan |
| status | CharField(20) | draft, approved, closed |
| created_at | DateTimeField |
| updated_at | DateTimeField |

Único compuesto: (entity, period)

### 3.9 budget_items
| Campo | Tipo |
|-------|------|
| id | AutoField |
| budget | FK → budgets |
| item_type | CharField(20) | ingreso, gasto |
| economic_classification | CharField(100) | naturaleza económica |
| code | CharField(20) | código de partida |
| description | TextField | |
| planned_amount | DecimalField(18,2) | |
| created_at | DateTimeField |
| updated_at | DateTimeField |

Único compuesto: (budget, item_type, economic_classification, code)

### 3.10 indicators
| Campo | Tipo |
|-------|------|
| id | AutoField |
| code | CharField(20), único |
| name | CharField(200) |
| indicator_type | CharField(30) | ingreso, gasto, productividad, salario |
| description | TextField | opcional |
| calculation_method | CharField(50) | acumulado, correlacion, estimado, ninguno |
| is_active | BooleanField |
| created_at | DateTimeField |

### 3.11 indicator_variables
| Campo | Tipo |
|-------|------|
| id | AutoField |
| indicator | FK → indicators |
| name | CharField(100) |
| data_type | CharField(20) | decimal, integer, percentage |
| source_field | CharField(100) | nombre del campo en budget_item |
| is_required | BooleanField |

Único compuesto: (indicator, name)

### 3.12 indicator_records
| Campo | Tipo |
|-------|------|
| id | AutoField |
| entity | FK → entities |
| indicator | FK → indicators |
| period | FK → periods |
| variable_name | CharField(100) | nombre de la variable |
| value | DecimalField(18,6) | |
| data_origin | CharField(20) | manual, imported, calculated |
| source_document | FK → documents | nullable |
| import_job | FK → import_jobs | nullable |
| created_at | DateTimeField |
| updated_at | DateTimeField |

Único compuesto: (entity, indicator, period, variable_name)

### 3.13 calculations
| Campo | Tipo |
|-------|------|
| id | AutoField |
| calculation_type | CharField(30) | acumulado, correlacion, estimado |
| entity | FK → entities | nullable (null = todas) |
| period | FK → periods |
| status | CharField(20) | pending, running, completed, failed |
| error_message | TextField | nullable |
| triggered_by | FK → users |
| started_at | DateTimeField | nullable |
| completed_at | DateTimeField | nullable |
| created_at | DateTimeField |

### 3.14 calculation_results
| Campo | Tipo |
|-------|------|
| id | AutoField |
| calculation | FK → calculations |
| indicator | FK → indicators |
| variable_name | CharField(100) |
| value | DecimalField(18,6) | puede ser null |
| is_error | BooleanField | indica división por cero u otro error |

Único compuesto: (calculation, indicator, variable_name)

### 3.15 documents
| Campo | Tipo |
|-------|------|
| id | AutoField |
| filename | CharField(255) |
| file_path | CharField(500) | ruta interna de storage |
| file_type | CharField(20) | xlsx, xls |
| file_size | PositiveIntegerField | bytes |
| uploaded_by | FK → users |
| uploaded_at | DateTimeField |

### 3.16 import_jobs
| Campo | Tipo |
|-------|------|
| id | AutoField |
| document | FK → documents |
| entity | FK → entities | nullable |
| period | FK → periods | nullable |
| status | CharField(20) | uploaded, parsing, validating, migrating, completed, failed |
| rows_total | PositiveIntegerField | nullable |
| rows_processed | PositiveIntegerField | nullable |
| rows_valid | PositiveIntegerField | nullable |
| rows_invalid | PositiveIntegerField | nullable |
| errors_log | JSONField | lista de errores |
| started_at | DateTimeField | nullable |
| completed_at | DateTimeField | nullable |
| created_at | DateTimeField |

### 3.17 document_details (staging — pre-migración)
| Campo | Tipo |
|-------|------|
| id | AutoField |
| import_job | FK → import_jobs |
| row_number | PositiveIntegerField |
| entity_code | CharField(100) | raw del Excel |
| period_year | PositiveIntegerField | raw |
| period_month | PositiveIntegerField | raw |
| indicator_code | CharField(100) | raw |
| variable_name | CharField(100) | raw |
| raw_value | CharField(200) | valor sin procesar |
| parsed_value | DecimalField(18,6) | nullable |
| is_valid | BooleanField |
| validation_error | TextField | nullable |

### 3.18 entity_classifications
| Campo | Tipo |
|-------|------|
| id | AutoField |
| entity | FK → entities |
| period | FK → periods |
| classification_type | CharField(50) | cumplimiento_presupuestario |
| category | CharField(50) | cumplimiento, subejecucion, sobrecumplimiento |
| score | DecimalField(18,6) | nullable |
| details | JSONField | nullable |
| calculated_at | DateTimeField |

Único compuesto: (entity, period, classification_type)

## 4. Plan por Iteraciones

### Iteración 1 — 2 semanas (HU1–HU5, RNF1–RNF2)

**Objetivo**: Autenticación JWT segura y gestión básica de usuarios.

- [ ] **accounts**: `CustomUser`, `Role`, `UserRole`
- [ ] `LoginAttempt`, `BlockedIP` para control de fuerza bruta
- [ ] Endpoint `POST /api/auth/login` — validación de email verificado, registra intento
- [ ] Endpoint `POST /api/auth/refresh` — rotación de access token
- [ ] Endpoint `POST /api/auth/logout` — blacklist del token
- [ ] Endpoint `GET /api/auth/me`
- [ ] Endpoint `POST /api/auth/register` (admin crea usuarios)
- [ ] Endpoint `DELETE /api/users/{id}` — soft delete
- [ ] Middleware de expiración de sesión (JWT exp claim)
- [ ] Rate limiting por IP: bloquea tras 5 intentos fallidos / 15 min (RNF2)
- [ ] Tests unitarios y de API

### Iteración 2 — 5 semanas (HU6–HU15)

**Objetivo**: Pipeline de importación, cálculo de indicadores y exportación.

- [ ] **catalog**: `Entity`, `Period`
- [ ] **budget**: `Budget`, `BudgetItem`
- [ ] **indicators**: `Indicator`, `IndicatorVariable`, `IndicatorRecord`
- [ ] `Document`, `ImportJob`, `DocumentDetail`
- [ ] Endpoint `POST /api/documents/upload` — guarda archivo xlsx
- [ ] Servicio de parsing: lee xlsx con openpyxl/pandas, inserta en `document_details`
- [ ] Servicio de estandarización: normaliza nombres de entidades, periodos, indicadores
- [ ] Endpoint `POST /api/import-jobs/{id}/validate` — corre validación, marca filas válidas/inválidas
- [ ] Endpoint `POST /api/import-jobs/{id}/migrate` — migra filas válidas a `indicator_records` en transacción
- [ ] Endpoint `GET /api/indicator-records` con filtros por entity, indicator, period
- [ ] **calculations**: `Calculation`, `CalculationResult`
- [ ] Servicio `CalculationService.calcular_acumulado(entity, period)` — HU11
- [ ] Servicio `CalculationService.calcular_correlacion(entity, period)` — HU12 (productividad vs salario medio)
- [ ] Servicio `CalculationService.calcular_estimado(entity, period)` — HU13
- [ ] Manejo de división por cero → marca `is_error=True`, registra mensaje
- [ ] Endpoint `POST /api/calculations/run` — lanza cálculo async/sync
- [ ] Endpoint `GET /api/calculations/{id}/results`
- [ ] Endpoint `POST /api/exports/xlsx` — exporta a Excel reutilizando budget_items y records
- [ ] Tests de integración: upload → validate → migrate → calculate → export

### Iteración 3 — 3 semanas (HU16–HU18)

**Objetivo**: Reportes, estadísticas y clasificación.

- [ ] `EntityClassification`
- [ ] Endpoint `POST /api/reports` — genera informe automático o personalizado
- [ ] Servicio de estadísticas: tendencias por entidad, periodo, indicador
- [ ] Endpoint `GET /api/stats` — devuelve datos agregados para gráficos
- [ ] Servicio de clasificación: categoriza entidades por cumplimiento presupuestario
- [ ] Endpoint `POST /api/classifications/calculate`
- [ ] Endpoint `GET /api/classifications` — lista con filtros
- [ ] Tests de reportes y clasificación

## 5. API REST — Endpoints

### Auth
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login (email, password) |
| POST | `/api/auth/refresh/` | Refresh token |
| POST | `/api/auth/logout/` | Logout / blacklist |
| GET | `/api/auth/me/` | Usuario actual |

### Users
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/` | Lista paginada |
| POST | `/api/users/` | Crear usuario |
| GET | `/api/users/{id}/` | Detalle |
| PATCH | `/api/users/{id}/` | Actualizar |
| DELETE | `/api/users/{id}/` | Soft delete |

### Roles
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/roles/` | Lista |
| POST | `/api/roles/` | Crear |
| GET/PATCH/DELETE | `/api/roles/{id}/` | CRUD |

### Entities
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/entities/` | Lista paginada |
| POST | `/api/entities/` | Crear |
| GET/PATCH/DELETE | `/api/entities/{id}/` | CRUD |

### Periods
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/periods/` | Lista |
| POST | `/api/periods/` | Crear |
| GET/PATCH | `/api/periods/{id}/` | CRUD |

### Budgets
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/budgets/` | Lista con filtros |
| POST | `/api/budgets/` | Crear |
| GET/PATCH | `/api/budgets/{id}/` | CRUD |

### Budget Items
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/budget-items/` | Lista con filtros |
| POST | `/api/budget-items/` | Crear |
| GET/PATCH/DELETE | `/api/budget-items/{id}/` | CRUD |

### Indicators
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/indicators/` | Lista |
| POST | `/api/indicators/` | Crear |
| GET/PATCH/DELETE | `/api/indicators/{id}/` | CRUD |

### Indicator Variables
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/indicator-variables/` | Lista |
| POST | `/api/indicator-variables/` | Crear |
| GET/PATCH/DELETE | `/api/indicator-variables/{id}/` | CRUD |

### Indicator Records
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/indicator-records/` | Lista con filtros |
| POST | `/api/indicator-records/` | Crear manual |
| GET/PATCH/DELETE | `/api/indicator-records/{id}/` | CRUD |

### Documents
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/documents/` | Lista |
| POST | `/api/documents/upload/` | Subir archivo |
| GET/DELETE | `/api/documents/{id}/` | Detalle/Eliminar |

### Import Jobs
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/import-jobs/` | Lista |
| GET | `/api/import-jobs/{id}/` | Detalle + estado |
| POST | `/api/import-jobs/{id}/validate/` | Validar |
| POST | `/api/import-jobs/{id}/migrate/` | Migrar a BD |
| GET | `/api/import-jobs/{id}/errors/` | Errores de validación |

### Calculations
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/calculations/` | Lista |
| POST | `/api/calculations/run/` | Ejecutar cálculo |
| GET | `/api/calculations/{id}/` | Detalle |
| GET | `/api/calculations/{id}/results/` | Resultados |

### Exports
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/exports/xlsx/` | Exportar a Excel |

### Reports
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/reports/` | Lista de reportes |
| POST | `/api/reports/` | Generar reporte |
| GET | `/api/reports/{id}/` | Detalle + descarga |

### Statistics
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/stats/` | Datos para gráficos y tendencias |

### Classifications
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/classifications/` | Lista con filtros |
| POST | `/api/classifications/calculate/` | Recalcular |
| GET | `/api/classifications/{id}/` | Detalle |

## 6. Dependencias

```bash
pip install Django==6.0.3 djangorestframework==3.17.0
pip install djangorestframework-simplejwt  # JWT
pip install openpyxl                      # Leer/escribir xlsx
pip install pandas                         # Preprocesamiento de datos (opcional en venv)
pip install black isort flake8 pytest-django  # Lint/test
```

## 7. Estrategia de Pruebas

### Unit tests
- `accounts`: validación de login, bloqueo de IP, creación de usuario
- `calculations`: acumulado, correlación, estimado, división por cero
- `ingestion`: parser de xlsx, normalización, validación

### API tests (DRF `APITestCase`)
- Permisos por rol (admin vs usuario)
- Contratos de endpoints: respuestas 200, 400, 401, 403, 404
- Flujo de importación completo

### Integration tests
```
upload xlsx → parse → validate → migrate →
calculate(acumulado) → calculate(correlacion) →
calculate(estimado) → export xlsx
```

### Ejecución de tests
```bash
# Todos
python manage.py test

# App específica
python manage.py test accounts

# Clase específica
python manage.py test accounts.tests.LoginAttemptTestCase

# Un solo test
python manage.py test accounts.tests.LoginAttemptTestCase.test_ip_blocked_after_failures

# Verbose
python manage.py test -v 2

# Rápido (reuse DB)
python manage.py test --keepdb
```

## 8. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Duplicidad "Presupuesto" en diagrama | Pérdida de granularidad en cálculos | Resolver con `Budget` + `BudgetItem` separados |
| Archivos Excel muy grandes | OOM, timeouts | Procesar por lotes (chunking), `bulk_create` |
| División por cero en cálculos | Cálculos fallidos silenciosamente | Servicios con manejo explícito, marcar `is_error=True`, notificar usuario |
| Pérdida de trazabilidad de datos | Auditoría difícil | Campo `data_origin` + FK a `document`/`import_job` en todos los records |
| Crecimiento de datos (RNF4) | Degradación de rendimiento | Índices en FK + campos de filtro, paginación desde inicio |
| Credenciales hardcodeadas | Seguridad | Nunca commitear secrets; usar variables de entorno |
