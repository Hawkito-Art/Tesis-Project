from rest_framework.permissions import BasePermission, SAFE_METHODS

from tesis.permissions import has_role


class BudgetWriteAdminReadAuthenticated(BasePermission):
    """Permite lectura a autenticados y escritura solo a admin."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return user.is_staff or has_role(user, 'admin')
