from rest_framework.permissions import BasePermission

from tesis.permissions import IsAdmin, IsAdminOrAnalyst, ReadOnly


class CatalogPermission(BasePermission):
    """
    - admin: lectura + escritura
    - analyst, operator: solo lectura
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from tesis.permissions import has_role

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return has_role(request.user, 'admin', 'analyst', 'operator')
        return has_role(request.user, 'admin')
