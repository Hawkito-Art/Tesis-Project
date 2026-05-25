"""Ejemplo de patrón Decorador para vistas y funciones (backend).

Incluye un decorador sencillo `require_permission` y un `log_action`.
Usar estos decoradores para añadir comportamiento transversal sin tocar
la lógica principal.
"""
from functools import wraps
from typing import Callable


def require_permission(perm: str):
    """Decorator que verifica `request.user.has_perm(perm)`.

    Uso:
        @require_permission('indicators.change_indicator')
        def my_view(request):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "user", None)
            if user is None or not getattr(user, "has_perm", lambda p: False)(perm):
                # en DRF usar `PermissionDenied`, aquí simplificamos
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied(f"Missing permission: {perm}")
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def log_action(func: Callable):
    """Decorator para logging simple de entrada/salida de funciones."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Entering {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] Exiting {func.__name__}")
        return result

    return wrapper


if __name__ == "__main__":
    @log_action
    def say_hi(name: str):
        print(f"Hello {name}")

    say_hi("mundo")
