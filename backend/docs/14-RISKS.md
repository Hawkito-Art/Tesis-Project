# 14 - Riesgos y Mitigaciones

## Objetivo

Gestionar riesgos tecnicos y operativos que pueden afectar la construccion del backend.

## Prerequisitos

- Lectura de [PLAN_DE_ACCION](../PLAN_DE_ACCION.md).
- Definicion de iteraciones y responsables.

## Matriz de riesgos

| ID | Riesgo | Impacto | Probabilidad | Mitigacion | Owner |
|---|---|---|---|---|---|
| R1 | Excel muy grande (OOM/timeout) | Alto | Media | Procesamiento por lotes y `bulk_create` | Ingestion |
| R2 | Division por cero en calculos | Alto | Alta | `is_error=True`, mensaje tecnico y pruebas | Calculations |
| R3 | Duplicidad o inconsistencia de catalogos | Alto | Media | Constraints + normalizacion + validacion | Catalog |
| R4 | Secretos expuestos | Alto | Media | Variables de entorno y politicas de git | DevOps |
| R5 | Migraciones rompedoras | Alto | Media | Ensayo en staging + backup previo | Backend Lead |
| R6 | Permisos mal configurados | Alto | Media | Matriz por endpoint y API tests de seguridad | Accounts |
| R7 | Corridas concurrentes de calculo | Medio | Media | Locks y control de idempotencia | Calculations |
| R8 | Falta de trazabilidad de datos | Medio | Baja | `data_origin`, `source_document`, `import_job` | Ingestion |

## Pasos de gestion continua

- [ ] Revisar matriz de riesgos al inicio de cada sprint.
- [ ] Confirmar estado de mitigaciones en retrospectiva.
- [ ] Registrar incidentes y acciones correctivas.
- [ ] Repriorizar riesgos segun avance de iteraciones.

## Criterios de aceptacion

- Cada riesgo critico tiene owner y accion definida.
- Riesgos de seguridad y datos tienen plan preventivo.
- El equipo revisa esta matriz de forma periodica.

## Errores comunes y solucion

- Riesgos sin responsable: asignar owner explicito.
- Riesgos no actualizados: establecer revision fija por sprint.
