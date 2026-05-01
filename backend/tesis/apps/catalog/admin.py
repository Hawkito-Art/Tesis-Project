from django.contrib import admin

from .models import Entity, Period


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'is_consolidated', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'description')
    list_filter = ('type', 'is_consolidated', 'is_active', 'created_at')
    ordering = ('code',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'period_type', 'is_active', 'created_at')
    search_fields = ('year', 'month', 'period_type')
    list_filter = ('period_type', 'year', 'is_active', 'created_at')
    ordering = ('-year', '-month', 'period_type')
    readonly_fields = ('created_at',)
