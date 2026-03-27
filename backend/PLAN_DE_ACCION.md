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
| type | CharField(50) | unidad presupuestada, empresa, mipyme, etc. |
| is_consolidated | BooleanField | True para la entidad agregada (Consolidado Municipal) |
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

### 3.10 indicator_groups
| Campo | Tipo |
|-------|------|
| id | AutoField |
| code | CharField(30), único | fundamental, limite, otro |
| name | CharField(100) | Indicadores Fundamentales, Indicadores Límites, Otros Indicadores |
| order | PositiveIntegerField | orden de presentación |
| created_at | DateTimeField |

### 3.11 indicators
| Campo | Tipo |
|-------|------|
| id | AutoField |
| code | CharField(20), único | generado a partir del nombre (slug) |
| name | CharField(200) | nombre exacto del Excel (ej: "Ventas Totales") |
| group | FK → indicator_groups | fundamental, limite u otro |
| indicator_type | CharField(30) | ingreso, gasto, productividad, salario, ratio |
| unit | CharField(10) | MP=miles de pesos, U=unidades, p=pesos, Coef=coeficiente, peso=ratio |
| description | TextField | opcional |
| calculation_method | CharField(50) | acumulado, correlacion, estimado, ninguno |
| is_active | BooleanField |
| created_at | DateTimeField |

### 3.12 indicator_variables
| Campo | Tipo | Notas |
|-------|------|-------|
| id | AutoField | |
| indicator | FK → indicators | |
| name | CharField(100) | nombre técnico de la variable |
| label | CharField(150) | etiqueta legible (ej: "Plan Año") |
| data_type | CharField(20) | decimal, integer, percentage, coefficient |
| source_field | CharField(100) | nombre del campo en budget_item (si aplica) |
| is_required | BooleanField | |

Único compuesto: (indicator, name)

**Variables estándar por indicador** (derivadas de las columnas del Excel):

| name | label | descripción |
|------|-------|-------------|
| `plan_anual` | PLAN AÑO | plan anual del indicador |
| `ano_anterior` | Año Anter. igual per. | valor del año anterior mismo período |
| `plan_acumulado` | PLAN acumulado | plan acumulado a la fecha |
| `real_acumulado` | REAL acumulado | valor real acumulado |
| `porcentaje_r_p` | % R/P | cumplimiento real/plan (real ÷ plan × 100) |
| `real_aa` | R/AA | real respecto al año anterior (real ÷ año_ant × 100) |
| `estimado_prox_mes` | Estimado próximo mes | proyección para el siguiente mes |
| `estimado_cierre_ano` | Estimado cierre/año | proyección de cierre anual |

### 3.13 indicator_records
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

### 3.14 calculations
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

### 3.15 calculation_results
| Campo | Tipo |
|-------|------|
| id | AutoField |
| calculation | FK → calculations |
| indicator | FK → indicators |
| variable_name | CharField(100) |
| value | DecimalField(18,6) | puede ser null |
| is_error | BooleanField | indica división por cero u otro error |

Único compuesto: (calculation, indicator, variable_name)

### 3.16 documents
| Campo | Tipo |
|-------|------|
| id | AutoField |
| filename | CharField(255) |
| file_path | CharField(500) | ruta interna de storage |
| file_type | CharField(20) | xlsx, xls |
| file_size | PositiveIntegerField | bytes |
| uploaded_by | FK → users |
| uploaded_at | DateTimeField |

### 3.17 import_jobs
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

### 3.18 document_details (staging — pre-migración)
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

### 3.19 entity_classifications
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

## 4. Estructura del Excel fuente (Indicadores 2025.xls)

El archivo fuente principal es `Indicadores 2025.xls` (formato Excel 97-2003, requiere `xlrd`).

### 4.1 Organización por hojas

Cada hoja representa una entidad económica del municipio:

| Hoja | Entidad | Tipo |
|------|---------|------|
| Consolidado Municipal | Alquízar (agregado) | consolidado |
| Emp.Agropecuaria | Empresa Agropecuaria | empresa |
| Empresa Alquitex | Empresa Alquitex | empresa |
| Empresa de Comercio | Empresa de Comercio | empresa |
| MIPYME ESTATAL | MIPYME Estatal | mipyme |
| IaGROP | IaGROP | mipyme |

### 4.2 Columnas por hoja

| Col índice | Encabezado | Campo destino |
|------------|------------|---------------|
| 0 | INDICADORES | `indicator.name` |
| 1 | U:M | `indicator.unit` |
| 2 | AÑO | `variable_name = plan_anual` |
| 3 | Año Anter. igual per. | `variable_name = ano_anterior` |
| 4 | PLAN | `variable_name = plan_acumulado` |
| 5 | REAL | `variable_name = real_acumulado` |
| 6 | % (R/P) | `variable_name = porcentaje_r_p` |
| 7 | R/AA | `variable_name = real_aa` |
| 8 | Estimado próximo mes | `variable_name = estimado_prox_mes` |
| 9 | Estimado cierre/año | `variable_name = estimado_cierre_ano` |

> Nota: La hoja "Consolidado Municipal" tiene una columna adicional (col 10) con un segundo estimado de cierre.

### 4.3 Indicadores por grupo

**Fundamentales** (filas de datos 1-4):
- Ventas Totales
- Total de Ingresos
- Total de Gastos
- Utilidad o Pérdida

**Límites** (fila siguiente a "Indicadores Limites"):
- Gasto de Salario x peso V.A.B

**Otros** (después de "Otros Indicadores"):
- Gasto Total x peso de Ing.Total
- Valor Agregado Bruto
- Utilidad Antes del Imp. x $ de VAB
- Fondo de Salario Total
- Promedio de Trabajadores
- Productividad del Trabajo
- Salario Medio
- Correlación Salario Medio/Product.

### 4.4 Reglas del parser

1. Las primeras 5-7 filas de cada hoja son cabeceras/metadata y deben ignorarse.
2. Filas con texto de sección ("Indicadores Limites", "Otros Indicadores") son separadores, no datos.
3. Filas vacías o con solo la celda de firma ("Aprobado:", nombre de directora) son pie de página.
4. El valor numérico `45992.0` en las filas superiores es un código interno del Excel, no un dato de indicador.
5. Cada fila de indicador válido genera hasta 8 `document_details` (uno por variable/columna con valor no vacío).
6. Los valores vacíos o texto no numérico en columnas de datos deben marcarse como `is_valid=False` en staging.

### 4.5 Mapeo de unidades

| Código Excel | Significado | Ejemplo |
|-------------|-------------|---------|
| MP | Miles de pesos | Ventas Totales, Ingresos, Gastos |
| U | Unidades | Promedio Trabajadores, VAB |
| p | Pesos | Productividad, Salario Medio |
| peso | Ratio/pesos por peso | Gasto x peso de ingreso |
| Coef | Coeficiente de correlación | Correlación Salario/Productividad |

## 5. Plan por Iteraciones

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

- [ ] **catalog**: `Entity` (con `is_consolidated`), `Period`
- [ ] **budget**: `Budget`, `BudgetItem`
- [ ] **indicators**: `IndicatorGroup`, `Indicator` (con `unit` y `group` FK), `IndicatorVariable`, `IndicatorRecord`
- [ ] `Document`, `ImportJob`, `DocumentDetail`
- [ ] Endpoint `POST /api/documents/upload` — guarda archivo xlsx/xls
- [ ] Servicio de parsing: lee xlsx con openpyxl o xls con xlrd; cada hoja = una entidad; filas de cabecera se saltan (5-7 primeras); cada fila de indicador genera N `document_details` (uno por variable/columna: plan_anual, ano_anterior, real_acumulado, etc.)
- [ ] Servicio de estandarización: normaliza nombres de entidades (mapeo hoja→Entity.code), periodos, indicadores (nombre→Indicator.code)
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

## 6. API REST — Endpoints

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

### Indicator Groups
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/indicator-groups/` | Lista de grupos (fundamental, limite, otro) |
| POST | `/api/indicator-groups/` | Crear |
| GET/PATCH/DELETE | `/api/indicator-groups/{id}/` | CRUD |

### Indicators
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/indicators/` | Lista (filtrable por group) |
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

## 7. Dependencias

```bash
pip install Django==6.0.3 djangorestframework==3.17.0
pip install djangorestframework-simplejwt  # JWT
pip install openpyxl                      # Leer/escribir xlsx
pip install xlrd                          # Leer xls (formato legacy de Indicadores 2025.xls)
pip install pandas                         # Preprocesamiento de datos (opcional en venv)
pip install black isort flake8 pytest-django  # Lint/test
```

## 8. Estrategia de Pruebas

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

## 9. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Duplicidad "Presupuesto" en diagrama | Pérdida de granularidad en cálculos | Resolver con `Budget` + `BudgetItem` separados |
| Archivos Excel muy grandes | OOM, timeouts | Procesar por lotes (chunking), `bulk_create` |
| División por cero en cálculos | Cálculos fallidos silenciosamente | Servicios con manejo explícito, marcar `is_error=True`, notificar usuario |
| Pérdida de trazabilidad de datos | Auditoría difícil | Campo `data_origin` + FK a `document`/`import_job` en todos los records |
| Crecimiento de datos (RNF4) | Degradación de rendimiento | Índices en FK + campos de filtro, paginación desde inicio |
| Credenciales hardcodeadas | Seguridad | Nunca commitear secrets; usar variables de entorno |
| Estructura irregular del Excel | Parser falla o importa datos basura | Validar cabeceras por hoja antes de parsear; skip de filas de separador y firma; pruebas con archivo real |
| Hojas con columnas variables | Columnas faltantes o extra | Consolidado Municipal tiene 11 cols vs 10 del resto; parser debe detectar ncols por hoja |
| Nombres de entidad no normalizados | Entidad no encontrada en catálogo | Mapeo explícito nombre_hoja → Entity.code; configuración mantenible |
