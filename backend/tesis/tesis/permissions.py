import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger('apps')


def get_user_roles(user):
    """Retorna el conjunto de nombres de roles activos del usuario."""
    if not user or not user.is_authenticated:
        return set()
    return set(
        user.user_roles.filter(role__is_active=True)
        .values_list('role__name', flat=True)
    )


def has_role(user, *role_names):
    """Verifica si el usuario tiene alguno de los roles indicados."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff and 'admin' in role_names:
        return True
    roles = get_user_roles(user)
    return bool(roles & set(role_names))


def log_access_denied(request, reason):
    """Registra evento de acceso denegado para auditoria."""
    user = request.user if request.user.is_authenticated else None
    logger.warning(
        'Acceso denegado | usuario=%s | ip=%s | path=%s | motivo=%s',
        user.email if user else 'anonimo',
        request.META.get('REMOTE_ADDR', ''),
        request.path,
        reason,
    )


class IsAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol admin o is_staff."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed = has_role(request.user, 'admin')
        if not allowed:
            log_access_denied(request, 'se requiere rol admin')
        return allowed


class IsAnalyst(BasePermission):
    """Permite acceso a usuarios con rol analyst."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed = has_role(request.user, 'analyst')
        if not allowed:
            log_access_denied(request, 'se requiere rol analyst')
        return allowed


class IsOperator(BasePermission):
    """Permite acceso a usuarios con rol operator."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed = has_role(request.user, 'operator')
        if not allowed:
            log_access_denied(request, 'se requiere rol operator')
        return allowed


class IsAdminOrAnalyst(BasePermission):
    """Permite acceso a usuarios con rol admin o analyst."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed = has_role(request.user, 'admin', 'analyst')
        if not allowed:
            log_access_denied(request, 'se requiere rol admin o analyst')
        return allowed


class IsAdminOrOperator(BasePermission):
    """Permite acceso a usuarios con rol admin u operator."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        allowed = has_role(request.user, 'admin', 'operator')
        if not allowed:
            log_access_denied(request, 'se requiere rol admin u operator')
        return allowed


class ReadOnly(BasePermission):
    """Permite solo metodos de lectura (GET, HEAD, OPTIONS)."""

    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
