from rest_framework.permissions import BasePermission

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

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return has_role(request.user, 'admin', 'analyst')

        if request.method == 'POST':
            return has_role(request.user, 'admin', 'analyst')

        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return has_role(request.user, 'admin')

        return False
