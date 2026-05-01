from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BlockedIP, CustomUser, LoginAttempt, Role, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    autocomplete_fields = ('role',)
    readonly_fields = ('created_at',)
    fields = ('role', 'created_at')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = (
        'email',
        'first_name',
        'last_name',
        'email_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'email_verified', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')
    inlines = (UserRoleInline,)
    actions = ('mark_users_active', 'mark_users_inactive')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email_verified')}),
        (
            'Permisos',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Fechas', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'email_verified',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
    )

    @admin.action(description='Activar usuarios seleccionados')
    def mark_users_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Desactivar usuarios seleccionados')
    def mark_users_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop('mark_users_active', None)
            actions.pop('mark_users_inactive', None)
        return actions


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)
    readonly_fields = ('created_at',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    search_fields = ('user__email', 'role__name')
    list_filter = ('role', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user', 'role')
    list_select_related = ('user', 'role')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'success', 'attempted_at')
    search_fields = ('email', 'ip_address')
    list_filter = ('success', 'attempted_at')
    ordering = ('-attempted_at',)
    readonly_fields = ('email', 'ip_address', 'success', 'attempted_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'is_active', 'blocked_at')
    search_fields = ('ip_address', 'reason')
    list_filter = ('is_active', 'blocked_at')
    ordering = ('-blocked_at',)
    readonly_fields = ('blocked_at',)
    actions = ('mark_ips_active', 'mark_ips_inactive')

    @admin.action(description='Desbloquear IPs seleccionadas')
    def mark_ips_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Bloquear IPs seleccionadas')
    def mark_ips_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop('mark_ips_active', None)
            actions.pop('mark_ips_inactive', None)
        return actions
