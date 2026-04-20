from rest_framework.permissions import BasePermission, SAFE_METHODS

from tesis.permissions import log_access_denied


class CalculationPermission(BasePermission):
    """
    - admin: acceso completo (run, resultados)
    - analyst: lectura y ejecucion de calculos
    - operator: sin acceso
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from tesis.permissions import has_role

        if request.method in SAFE_METHODS:
            allowed = has_role(request.user, 'admin', 'analyst')
            if not allowed:
                log_access_denied(request, 'se requiere rol admin o analyst para lectura de calculos')
            return allowed

        if request.method == 'POST':
            allowed = has_role(request.user, 'admin', 'analyst')
            if not allowed:
                log_access_denied(request, 'se requiere rol admin o analyst para ejecutar calculos')
            return allowed

        if request.method in ('PUT', 'PATCH', 'DELETE'):
            allowed = has_role(request.user, 'admin')
            if not allowed:
                log_access_denied(request, 'se requiere rol admin para mutaciones de calculos')
            return allowed

        return False
