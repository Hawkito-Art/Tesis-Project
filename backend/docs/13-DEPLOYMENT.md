# 13 - Deployment y Operacion

## Objetivo

Preparar despliegue seguro y operable del backend en ambientes no locales.

## Prerequisitos

- Modulos principales implementados.
- Pruebas criticas en verde.

## Pasos

### Paso 1: Configuracion segura

- [ ] Mover secretos a variables de entorno.
- [ ] Configurar `DEBUG=False` en produccion.
- [ ] Definir `ALLOWED_HOSTS`, CORS y politicas de cookies/tokens.

### Paso 2: Base de datos y migraciones

- [ ] Ejecutar backup previo a despliegue.
- [ ] Ejecutar migraciones con ventana controlada.
- [ ] Validar integridad post-migracion.

### Paso 3: Archivos y almacenamiento

- [ ] Definir estrategia para `documents` (filesystem o cloud).
- [ ] Asegurar permisos de lectura/escritura.

### Paso 4: Observabilidad

- [ ] Configurar logs estructurados.
- [ ] Publicar endpoint de health check (`/api/health/`).
- [ ] Monitorear tiempos de respuesta y errores 5xx.

### Paso 5: Operacion recurrente

- [ ] Definir backup programado.
- [ ] Definir politica de retencion de documentos y logs.
- [ ] Documentar runbook de incidentes.

## Criterios de aceptacion

- Despliegue sin perdida de datos.
- Aplicacion inicia con variables de entorno correctas.
- Health check responde estable.

## Errores comunes y solucion

- Secretos commiteados: rotar claves y limpiar historial.
- Migraciones no probadas: ejecutar ensayo previo en staging.
