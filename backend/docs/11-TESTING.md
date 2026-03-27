# 11 - Estrategia de Testing

## Objetivo

Asegurar calidad funcional y regresion minima durante todas las iteraciones.

## Prerequisitos

- Estructura de apps lista.
- Endpoints base implementados.

## Tipos de prueba

- Unit tests: modelos, serializers, servicios.
- API tests: permisos, contratos, estados HTTP.
- Integration tests: flujos cross-app (ingesta -> calculo -> reporte).

## Plan por iteracion

### Iteracion 1

- [ ] Login exitoso y fallido.
- [ ] Bloqueo de IP por fuerza bruta.
- [ ] Soft delete de usuario.
- [ ] Permisos de admin en gestion de usuarios.

### Iteracion 2

- [ ] CRUD de catalogos, presupuestos e indicadores.
- [ ] Flujo completo de importacion.
- [ ] Calculo acumulado, correlacion y estimado.
- [ ] Exportacion a Excel.

### Iteracion 3

- [ ] Generacion de reportes.
- [ ] Estadisticas agregadas.
- [ ] Clasificacion por cumplimiento presupuestario.

## Comandos de ejecucion

```bash
python manage.py test
python manage.py test accounts
python manage.py test accounts.tests.LoginAttemptTestCase
python manage.py test accounts.tests.LoginAttemptTestCase.test_ip_blocked_after_failures
python manage.py test -v 2
python manage.py test --keepdb
```

## Cobertura minima sugerida

- 80% unit tests en servicios criticos.
- 100% de endpoints protegidos con pruebas de permiso.
- 1 prueba de integracion por flujo principal.

## Criterios de aceptacion

- No hay fallos en pruebas criticas de seguridad e ingesta.
- Los contratos API no rompen entre iteraciones.

## Errores comunes y solucion

- Tests acoplados a orden de ejecucion: aislar fixtures.
- Fixtures inestables: usar fabricas y datos minimos.
