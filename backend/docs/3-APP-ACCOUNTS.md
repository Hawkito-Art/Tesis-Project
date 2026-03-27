# 3 - Proceso del Modulo Accounts

## Objetivo

Implementar autenticacion JWT segura, gestion de usuarios y control anti fuerza bruta.

## Prerequisitos

- [0-SETUP](0-SETUP.md)
- [2A-MODELS](2A-MODELS.md)
- [2C-PERMISSIONS](2C-PERMISSIONS.md)

## Entradas

- Requisitos HU1-HU5 y RNF1-RNF2.

## Pasos

### Paso 1: Modelos y admin

- [ ] Definir `CustomUser` con email como identificador.
- [ ] Implementar `Role`, `UserRole`, `LoginAttempt`, `BlockedIP`.
- [ ] Registrar modelos en admin para gestion interna.

### Paso 2: JWT y configuracion

- [ ] Configurar `djangorestframework-simplejwt`.
- [ ] Definir expiracion de access y refresh.
- [ ] Configurar blacklist para logout seguro.

### Paso 3: Endpoints de auth

- [ ] `POST /api/auth/login/` con registro de intentos.
- [ ] `POST /api/auth/refresh/`.
- [ ] `POST /api/auth/logout/` con invalidacion de token.
- [ ] `GET /api/auth/me/`.

### Paso 4: Gestion de usuarios

- [ ] `GET /api/users/` paginado.
- [ ] `POST /api/users/` (admin crea usuario).
- [ ] `PATCH /api/users/{id}/`.
- [ ] `DELETE /api/users/{id}/` con soft delete.

### Paso 5: Seguridad de acceso

- [ ] Bloquear IP tras 5 intentos fallidos en 15 min.
- [ ] Verificar `email_verified` en login.
- [ ] Registrar intentos exitosos y fallidos.

### Paso 6: Pruebas

- [ ] Unit tests para bloqueo y desbloqueo por IP.
- [ ] API tests para login, refresh, logout y `me`.
- [ ] Tests de permisos para CRUD de usuarios/roles.

## Salidas

- Sistema de autenticacion operativo.
- Endpoints de usuarios listos para Iteracion 1.

## Criterios de aceptacion

- Login correcto entrega access y refresh.
- Usuario sin verificar no puede autenticarse.
- Bloqueo por IP funciona en condiciones definidas.

## Errores comunes y solucion

- Rotacion incorrecta de refresh token: revisar configuracion de simplejwt.
- Soft delete no aplicado en listados: filtrar por `is_active=True`.
