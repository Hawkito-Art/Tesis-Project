# Plan de Implementación y Iteraciones

Fecha: 2026-05-01
Autor: Equipo Tesis (auditado por agente)

## Objetivo
Documentar un plan detallado, por iteraciones, con tareas, criterios de aceptación y comandos para llevar el proyecto Django a estado de producción (o al menos a un 95% funcional).

---

## Resumen ejecutivo
El proyecto está estructurado y funcional en gran parte, pero requiere completar principalmente: 1) configuración CORS, 2) parser XLSX en `ingestion`, 3) implementación de `indicators/services.py` y 4) completar algunos endpoints de `reports`. El plan organiza el trabajo en iteraciones priorizadas.

---

## Iteraciones y tareas
Cada iteración tiene tareas, estimación y criterios de aceptación. Trabajar en orden de prioridad: Bloqueadores críticos → funcionalidades dependientes → calidad / documentación / despliegue.

### Iteración 0 — Preparación (entorno, verificación)
- Tareas:
  - Activar/crear `venv` en `backend/venv`.
  - Instalar dependencias listadas en `docs/0-SETUP.md`.
  - Ejecutar `python manage.py check` y `python manage.py showmigrations`.
  - Ejecutar `python manage.py test -v 2`.
- Estimación: 0.5 - 1 hora
- Criterios de aceptación:
  - Todos los tests existentes pasan o se documentan fallos conocidos.
  - Estado de migraciones conocido.
- Comandos:
```bash
source backend/venv/bin/activate
cd backend/tesis
python manage.py check
python manage.py showmigrations
python manage.py test -v 2
```

---

### Iteración 1 — Bloqueadores críticos (impedir uso por frontend)
- Tareas:
  1. Configurar CORS globalmente.
     - Instalar `django-cors-headers`.
     - Agregar a `INSTALLED_APPS` y `MIDDLEWARE`.
     - Definir `CORS_ALLOWED_ORIGINS` / `CORS_ALLOW_ALL_ORIGINS` según ambiente.
  2. Aplicar migraciones y verificar esquema.
     - `python manage.py migrate`.
     - Revisar constraints e índices.
- Estimación: 1-2 horas
- Criterios de aceptación:
  - Frontend puede hacer llamadas (CORS ok en entorno dev).
  - DB migrada sin errores y tablas esperadas presentes.
- Comandos:
```bash
pip install django-cors-headers
# editar settings.py según pasos
python manage.py migrate
```

---

### Iteración 2 — Ingestión (parser XLSX y upsert)
- Tareas:
  - Revisar `apps.ingestion.services` y localizar el parser incompleto (`parse_document_indicator_rows` u homólogo).
  - Implementar parsing robusto:
    - Validar columnas esperadas (Entity, Period, Indicator, Variable, Value).
    - Manejar filas con errores y acumular reporte de validación.
    - Transformar tipos (dates, numbers) y normalizar códigos de entidad/indicador.
  - Implementar `upsert_indicator_records_from_import_job()` completo:
    - Validar existencia de `Entity` y `Period`.
    - Crear o actualizar `IndicatorRecord` con `source=SOURCE_IMPORTED`.
    - Transaccionalizar el proceso y reportar errores por fila.
  - Añadir pruebas unitarias para parsing y upsert.
- Estimación: 1.5 - 3 horas
- Criterios de aceptación:
  - Un archivo de muestra se importa correctamente y crea/actualiza `IndicatorRecord`.
  - Errores de filas quedan listados y no rompen todo el job.
- Tests a correr:
```bash
python manage.py test ingestion.tests -v 2
```

---

### Iteración 3 — Indicators (lógica de negocio)
- Tareas:
  - Implementar `apps.indicators.services`:
    - Validaciones por variable y unidad.
    - Cálculos derivados si aplica (porcentaje R/P, real año anterior, estimados).
    - API helper para consumir desde `calculations` y `reports`.
  - Añadir pruebas unitarias de cada función crítica.
- Estimación: 2-4 horas
- Criterios de aceptación:
  - Funciones de cálculo devuelven resultados coincidentes con casos de ejemplo.
  - Integración con `calculations.run_formula_engine()` verifica update de `IndicatorRecord`.

---

### Iteración 4 — Reports (endpoints faltantes)
- Tareas:
  - Identificar endpoints que devuelven 501 y completar sus handlers (Contract pattern).
  - Verificar payloads con `build_report_payload()` y `build_stats_payload()`.
  - Añadir pruebas API para los endpoints restaurados.
- Estimación: 1-2 horas
- Criterios de aceptación:
  - Endpoints ya no retornan 501 y devuelven payloads válidos.
  - Tests de integración para reportes pasan.

---

### Iteración 5 — Calidad, documentación y deploy
- Tareas:
  - Agregar `drf-spectacular` o `drf-yasg` para OpenAPI/Swagger.
  - Añadir `django-cors-headers` configuración final para prod/staging.
  - Personalizar `admin.py` para `Entity`, `Indicator`, `Budget`.
  - Crear fixtures mínimos (`fixtures/initial_data.json`) con entidades y periods.
  - Añadir checks de lint (`black`, `isort`, `flake8`) y ajustar estilo.
  - Añadir CI pipeline (GitHub Actions) para tests + flake8 + black check.
- Estimación: 4-8 horas
- Criterios de aceptación:
  - Documentación OpenAPI disponible en `/api/schema/` y Swagger UI.
  - CI verde en PRs.

---

## Detalle técnico por tarea (qué archivos cambiar y cómo probar)
- `settings.py`: agregar `corsheaders` en `INSTALLED_APPS` y `MIDDLEWARE`, añadir `CORS_ALLOWED_ORIGINS`.
- `apps/ingestion/services.py`: completar funciones de parseo y upsert.
- `apps/indicators/services.py`: implementar validaciones y cálculos.
- `apps/reports/views.py`: completar handlers 501.
- `backend/tesis/urls.py`: montar rutas de swagger si se añade.

Pruebas recomendadas:
- Unitarias: `python manage.py test <app>.tests`.
- Integración: flujos `ingestion -> calculations -> reports` con fixtures.

---

## Criterios de finalización (Definition of Done)
- Todos los tests existentes y los nuevos añadidos pasan.
- Endpoints críticos (auth, ingestion, indicators, calculations, reports) funcionan en entorno dev.
- Documentación API accesible y CORS configurado.
- Migraciones aplicadas y fixtures cargables.

---

## Plan de rollback y mitigación
- Ejecutar import jobs en modo `dry-run` antes de aplicar cambios.
- Hacer backups de `db.sqlite3` en dev antes de migraciones riesgosas.
- Registrar transacciones y errores en logs con suficientes datos para reproducir la fila causante.

---

## Anexos
- Ver `backend/docs/0-SETUP.md` para instrucciones de entorno.
- Ver `backend/docs/11-TESTING.md` para estrategia de pruebas.

---

Archivo generado automáticamente por auditoría de 2026-05-01.
