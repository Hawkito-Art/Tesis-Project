from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.email


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'rol'
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='user_roles',
    )
    role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.CASCADE,
        related_name='role_users',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'usuario-rol'
        verbose_name_plural = 'usuario-roles'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='unique_user_role',
            ),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.role.name}'


class LoginAttempt(models.Model):
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'intento de login'
        verbose_name_plural = 'intentos de login'
        indexes = [
            models.Index(fields=['email', '-attempted_at'], name='idx_login_email_date'),
            models.Index(fields=['ip_address', '-attempted_at'], name='idx_login_ip_date'),
        ]

    def __str__(self):
        return f'{self.email} - {self.attempted_at}'


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField(blank=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'IP bloqueada'
        verbose_name_plural = 'IPs bloqueadas'

    def __str__(self):
        return self.ip_address
