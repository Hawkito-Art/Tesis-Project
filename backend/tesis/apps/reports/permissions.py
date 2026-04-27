from rest_framework.permissions import BasePermission

from tesis.permissions import log_access_denied
from tesis.permissions import has_role


class ReportPermission(BasePermission):
    """
    - admin: lectura + escritura
    - analyst: lectura
    - operator: sin acceso
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            allowed = has_role(request.user, 'admin', 'analyst')
            if not allowed:
                log_access_denied(request, 'reports: se requiere rol admin o analyst para lectura')
            return allowed

        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            allowed = has_role(request.user, 'admin')
            if not allowed:
                log_access_denied(request, 'reports: se requiere rol admin para escritura/calculo')
            return allowed

        log_access_denied(request, f'reports: metodo no permitido por permisos ({request.method})')
        return False
