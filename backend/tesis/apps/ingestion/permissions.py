from rest_framework.permissions import BasePermission, SAFE_METHODS

from tesis.permissions import log_access_denied


class IngestionPermission(BasePermission):
    """
    - admin: acceso completo (upload, validate, migrate)
    - operator: upload y validate
    - analyst: sin acceso
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from tesis.permissions import has_role

        if request.method in SAFE_METHODS:
            allowed = has_role(request.user, 'admin', 'operator')
            if not allowed:
                log_access_denied(request, 'se requiere rol admin u operator para lectura de ingestion')
            return allowed

        if request.method == 'POST':
            allowed = has_role(request.user, 'admin', 'operator')
            if not allowed:
                log_access_denied(request, 'se requiere rol admin u operator para escritura de ingestion')
            return allowed

        if request.method in ('PUT', 'PATCH', 'DELETE'):
            allowed = has_role(request.user, 'admin')
            if not allowed:
                log_access_denied(request, 'se requiere rol admin para mutaciones de ingestion')
            return allowed

        return False
