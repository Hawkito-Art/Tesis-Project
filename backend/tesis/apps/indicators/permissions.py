from rest_framework.permissions import BasePermission, SAFE_METHODS

from tesis.permissions import log_access_denied


class IndicatorPermission(BasePermission):
    """
    - admin: lectura + escritura
    - analyst: lectura + edicion de records
    - operator: sin acceso
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from tesis.permissions import has_role

        if request.method in SAFE_METHODS:
            return has_role(request.user, 'admin', 'analyst')

        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return has_role(request.user, 'admin')

        return False


class IndicatorRecordPermission(BasePermission):
    """
    - admin: lectura + escritura completa
    - analyst: lectura + edicion de valores
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from tesis.permissions import has_role

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return has_role(request.user, 'admin', 'analyst')

        if request.method in ('PUT', 'PATCH'):
            return has_role(request.user, 'admin', 'analyst')

        if request.method in ('POST', 'DELETE'):
            return has_role(request.user, 'admin')

        return False
