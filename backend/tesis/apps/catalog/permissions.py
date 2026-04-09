from rest_framework.permissions import BasePermission, SAFE_METHODS

from tesis.permissions import has_role


class CatalogPermission(BasePermission):
    """
    - admin: lectura + escritura
    - analyst, operator: solo lectura
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff or has_role(request.user, 'admin')
