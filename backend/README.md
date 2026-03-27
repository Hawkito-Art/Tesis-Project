# Backend CAM Alquizar - Guia de Construccion

Este repositorio contiene la guia paso a paso para construir el backend Django REST del sistema economico municipal.

## Orden de lectura recomendado

1. [Plan general](PLAN_DE_ACCION.md)
2. [Setup del entorno](docs/0-SETUP.md)
3. [Arquitectura y convenciones](docs/1-ARQUITECTURA.md)
4. [Modelos y base de datos](docs/2A-MODELS.md)
5. [Serializacion y contratos](docs/2B-SERIALIZERS.md)
6. [Permisos por endpoint](docs/2C-PERMISSIONS.md)
7. [Modulo Accounts](docs/3-APP-ACCOUNTS.md)
8. [Modulo Catalog](docs/4-APP-CATALOG.md)
9. [Modulo Budget](docs/5-APP-BUDGET.md)
10. [Modulo Indicators](docs/6-APP-INDICATORS.md)
11. [Modulo Ingestion](docs/7-APP-INGESTION.md)
12. [Modulo Calculations](docs/8-APP-CALCULATIONS.md)
13. [Modulo Reports](docs/9-APP-REPORTS.md)
14. [Referencia API](docs/10-API-REFERENCE.md)
15. [Testing](docs/11-TESTING.md)
16. [Errores y observabilidad](docs/12-ERRORS.md)
17. [Deployment](docs/13-DEPLOYMENT.md)
18. [Riesgos](docs/14-RISKS.md)

## Flujo recomendado de ejecucion

1. Completar Iteracion 1 con `accounts` y seguridad basica.
2. Construir dominio de catalogos, presupuestos e indicadores.
3. Implementar pipeline de ingesta y validacion de Excel.
4. Implementar calculos y resultados.
5. Construir reportes, estadisticas y clasificacion.
6. Consolidar pruebas, hardening y despliegue.

## Criterio de cierre documental

Cada documento de `docs/` contiene:
- Objetivo
- Prerequisitos
- Entradas y salidas
- Checklist de pasos
- Criterios de aceptacion
- Errores comunes
