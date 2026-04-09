# Auth API — Tickets atómicos (GitHub Issues)

Este documento contiene los tickets atómicos para implementar la autenticación de `accounts` en la Iteración 1.

---

## Issue 1 — A1: Definir contrato final de endpoints Auth

## 🎯 Objetivo
Consolidar el contrato de API para `login`, `refresh`, `logout`, `me` (payloads, responses y status codes) y alinearlo con rutas reales.

## 📍 Alcance
- Confirmar paths finales:
  - `POST /api/auth/login/`
  - `POST /api/auth/refresh/`
  - `POST /api/auth/logout/`
  - `GET /api/auth/me/`
- Alinear `accounts/urls.py` con docs.

## 📂 Archivos
- `backend/docs/10-API-REFERENCE.md` (si hace falta ajuste)
- `backend/tesis/apps/accounts/urls.py`

## ✅ Criterios de aceptación
- No hay contradicción entre docs y rutas.
- Status codes documentados (200/400/401/403/429 según caso).
- Endpoints quedan definidos y cerrados para implementación.

## 🏁 Definition of Done
- Contrato Auth explícito, único y versionado en repo.

---

## Issue 2 — A2: Crear serializer de login (entrada)

## 🎯 Objetivo
Implementar serializer para validar request de login.

## 📍 Alcance
- Validar campos obligatorios y formato.
- Mensajes de error claros.
- Sin lógica de negocio pesada en serializer.

## 📂 Archivos
- `backend/tesis/apps/accounts/serializers.py`

## ✅ Criterios de aceptación
- Serializer rechaza payload inválido con errores consistentes.
- Serializer acepta payload válido.
- Código limpio y testeable.

## 🏁 Definition of Done
- Serializer de login integrado y pasando tests.

---

## Issue 3 — A3: Implementar servicio de autenticación (login flow)

## 🎯 Objetivo
Implementar lógica central del login en servicio desacoplado.

## 📍 Alcance
- Validar credenciales.
- Incrementar intentos en fallo.
- Bloquear usuario al superar umbral.
- Verificar `email_verified` (si aplica).
- Emitir tokens en éxito.
- Resetear intentos en éxito.

## 📂 Archivos
- `backend/tesis/apps/accounts/services.py` (crear si no existe)

## ✅ Criterios de aceptación
- Flujo exitoso y de error cubiertos.
- Reglas de bloqueo y verificación aplicadas correctamente.
- Lógica reutilizable desde view.

## 🏁 Definition of Done
- Servicio estable y cubierto por tests.

---

## Issue 4 — A4: Implementar endpoint `POST /api/auth/login/`

## 🎯 Objetivo
Exponer endpoint de login usando serializer + servicio.

## 📍 Alcance
- Crear view de login.
- Registrar ruta en `accounts/urls.py`.
- Respuestas consistentes según contrato.

## 📂 Archivos
- `backend/tesis/apps/accounts/views.py`
- `backend/tesis/apps/accounts/urls.py`

## ✅ Criterios de aceptación
- `POST /api/auth/login/` devuelve `access` + `refresh` en éxito.
- Devuelve error correcto en credenciales inválidas / bloqueado / no verificado.
- Respeta contrato de status codes.

## 🏁 Definition of Done
- Endpoint funcional en entorno local y pasando tests.

---

## Issue 5 — A5: Implementar endpoint `GET /api/auth/me/`

## 🎯 Objetivo
Permitir que el usuario autenticado consulte su perfil actual.

## 📍 Alcance
- Serializer de salida con campos mínimos.
- View autenticada para `me`.
- Ruta en `accounts/urls.py`.

## 📂 Archivos
- `backend/tesis/apps/accounts/serializers.py`
- `backend/tesis/apps/accounts/views.py`
- `backend/tesis/apps/accounts/urls.py`

## ✅ Criterios de aceptación
- Usuario autenticado recibe 200 con payload esperado.
- Usuario no autenticado recibe 401.
- No se exponen datos sensibles.

## 🏁 Definition of Done
- Endpoint `me` estable, seguro y documentado.

---

## Issue 6 — A6: Implementar endpoint `POST /api/auth/logout/` con revocación

## 🎯 Objetivo
Implementar logout invalidando refresh token (blacklist).

## 📍 Alcance
- Endpoint de logout.
- Parseo y validación de refresh token.
- Revocación efectiva del token.
- Manejo de token inválido/expirado.

## 📂 Archivos
- `backend/tesis/apps/accounts/serializers.py`
- `backend/tesis/apps/accounts/views.py`
- `backend/tesis/apps/accounts/urls.py`
- `backend/tesis/tesis/settings.py` (si falta config de blacklist)

## ✅ Criterios de aceptación
- Logout válido revoca token.
- Token revocado no sirve para refresh.
- Errores devuelven status consistente.

## 🏁 Definition of Done
- Logout implementado con revocación comprobada.

---

## Issue 7 — A7: Ajustar permisos y hardening básico en Auth

## 🎯 Objetivo
Asegurar permisos correctos y hardening mínimo en endpoints de auth.

## 📍 Alcance
- `AllowAny` solo para login/refresh.
- `IsAuthenticated` para me/logout.
- Revisar consistencia de errores de auth/permisos.
- Ajustes mínimos de seguridad en settings si aplica.

## 📂 Archivos
- `backend/tesis/apps/accounts/views.py`
- `backend/tesis/apps/accounts/permissions.py`
- `backend/tesis/tesis/settings.py` (si aplica)

## ✅ Criterios de aceptación
- Matriz de permisos correcta por endpoint.
- Respuestas de error homogéneas.
- No quedan endpoints sensibles abiertos.

## 🏁 Definition of Done
- Seguridad base de Auth cerrada.

---

## Issue 8 — A8: Suite de tests API para Auth completa

## 🎯 Objetivo
Cubrir con tests de integración API los flujos críticos de auth.

## 📍 Alcance
Casos mínimos:
- login exitoso
- login inválido
- bloqueo por intentos
- denegación por email no verificado (si aplica)
- me autenticado/no autenticado
- logout válido/inválido
- refresh con token revocado falla

## 📂 Archivos
- `backend/tesis/apps/accounts/tests/test_auth_api.py` (nuevo)
- Ajustes opcionales en tests existentes

## ✅ Criterios de aceptación
- Cobertura funcional de flujos felices + edge cases críticos.
- `python manage.py test apps.accounts -v 2` en verde.

## 🏁 Definition of Done
- Test suite confiable para prevenir regresiones de auth.

---

## Issue 9 — A9: Verificación técnica final y cierre de iteración Auth

## 🎯 Objetivo
Validar consistencia técnica final antes de dar por cerrada la iteración.

## 📍 Alcance
- Ejecutar checks finales.
- Verificar ausencia de migraciones pendientes.
- Confirmar estabilidad de tests auth.

## ✅ Criterios de aceptación
Comandos en verde:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test apps.accounts -v 2`

## 🏁 Definition of Done
- Iteración Auth lista para continuar con módulo siguiente.

---

## Orden recomendado de ejecución

`A1 → A2 → A3 → A4 → A5 → A6 → A7 → A8 → A9`
