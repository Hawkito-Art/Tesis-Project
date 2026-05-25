from dataclasses import dataclass

from django.contrib.auth import authenticate, get_user_model
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, Throttled, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import BlockedIP, LoginAttempt

User = get_user_model()


MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPTS_WINDOW_MINUTES = 30


@dataclass(frozen=True)
class AuthTokens:
    access: str
    refresh: str
def _failed_attempts_queryset(email: str, ip_address: str) -> QuerySet[LoginAttempt]:
    since = timezone.now() - timezone.timedelta(minutes=LOGIN_ATTEMPTS_WINDOW_MINUTES)
    return LoginAttempt.objects.filter(
        email=email,
        ip_address=ip_address,
        success=False,
        attempted_at__gte=since,
    )


def _assert_not_blocked(email: str, ip_address: str) -> None:
    if BlockedIP.objects.filter(ip_address=ip_address, is_active=True).exists():
        raise Throttled(detail='IP bloqueada temporalmente.')

    if _failed_attempts_queryset(email=email, ip_address=ip_address).count() >= MAX_LOGIN_ATTEMPTS:
        raise Throttled(detail='Demasiados intentos fallidos. Intenta nuevamente más tarde.')


def _register_attempt(email: str, ip_address: str, success: bool) -> None:
    LoginAttempt.objects.create(email=email, ip_address=ip_address, success=success)


def authenticate_user(*, email: str, password: str, ip_address: str) -> AuthTokens:
    normalized_email = email.strip().lower()
    _assert_not_blocked(email=normalized_email, ip_address=ip_address)

    user = authenticate(username=normalized_email, password=password)
    if user is None:
        _register_attempt(email=normalized_email, ip_address=ip_address, success=False)
        raise AuthenticationFailed(detail='Credenciales inválidas.')

    if not user.email_verified:
        _register_attempt(email=normalized_email, ip_address=ip_address, success=False)
        raise PermissionDenied(detail='Debes verificar tu email antes de iniciar sesión.')

    _register_attempt(email=normalized_email, ip_address=ip_address, success=True)
    _failed_attempts_queryset(email=normalized_email, ip_address=ip_address).delete()

    refresh = RefreshToken.for_user(user)
    return AuthTokens(access=str(refresh.access_token), refresh=str(refresh))


def revoke_refresh_token(*, refresh_token: str) -> None:
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as exc:
        raise ValidationError({'refresh': ['Token de refresh inválido o expirado.']}) from exc
