from django.contrib import admin

from .models import EntityClassification, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'entity',
        'period',
        'report_type',
        'status',
        'generated_by',
        'generated_at',
        'created_at',
    )
    search_fields = ('entity__code', 'entity__name', 'generated_by__email')
    list_filter = ('report_type', 'status', 'period__year', 'generated_at', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('summary', 'detail', 'metadata', 'generated_at', 'created_at', 'updated_at')
    autocomplete_fields = ('entity', 'period', 'generated_by')
    list_select_related = ('entity', 'period', 'generated_by')
    fieldsets = (
        (None, {'fields': ('entity', 'period', 'report_type', 'status', 'generated_by')}),
        ('Contenido', {'fields': ('summary', 'detail', 'metadata')}),
        ('Trazabilidad', {'fields': ('generated_at', 'created_at', 'updated_at')}),
    )


@admin.register(EntityClassification)
class EntityClassificationAdmin(admin.ModelAdmin):
    list_display = (
        'entity',
        'period',
        'classification_type',
        'value',
        'rule_version',
        'created_at',
    )
    search_fields = ('entity__code', 'entity__name', 'classification_type', 'value')
    list_filter = ('classification_type', 'rule_version', 'period__year', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('criteria_snapshot', 'created_at', 'updated_at')
    autocomplete_fields = ('entity', 'period')
    list_select_related = ('entity', 'period')
