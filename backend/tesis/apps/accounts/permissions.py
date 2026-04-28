from rest_framework.permissions import BasePermission, SAFE_METHODS

from tesis.permissions import IsAdmin, has_role, log_access_denied


class IsAdminUser(IsAdmin):
    """Solo administradores (por rol o is_staff)."""
    pass


class IsOwnerOrAdmin(BasePermission):
    """El propio usuario o un admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or obj == request.user:
            return True
        from tesis.permissions import has_role
        if has_role(request.user, 'admin'):
            return True
        log_access_denied(request, 'se requiere ser propietario o admin')
        return False


class AccountsDirectoryPermission(BasePermission):
    """Lectura para autenticados; escritura solo admin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        allowed = has_role(request.user, 'admin')
        if not allowed:
            log_access_denied(request, 'accounts directory: se requiere rol admin para escritura')
        return allowed
