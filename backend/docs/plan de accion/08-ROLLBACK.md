# Plan de rollback y mitigación

## Medidas
- Ejecutar jobs de importación en modo `dry-run` antes de aplicar cambios.
- Hacer backups de `db.sqlite3` en desarrollo antes de migraciones riesgosas.
- Registrar transacciones y errores con suficiente contexto para reproducir la fila causante.
