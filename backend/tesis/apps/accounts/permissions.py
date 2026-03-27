from rest_framework.permissions import BasePermission

from tesis.permissions import IsAdmin, log_access_denied


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
