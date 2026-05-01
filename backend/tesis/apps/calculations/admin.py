from django.contrib import admin

from .models import Calculation, CalculationResult


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'period',
        'status',
        'executed_by',
        'started_at',
        'finished_at',
        'created_at',
    )
    search_fields = ('name', 'description', 'executed_by__email')
    list_filter = ('status', 'period__year', 'created_at', 'started_at', 'finished_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('period', 'executed_by')
    list_select_related = ('period', 'executed_by')


@admin.register(CalculationResult)
class CalculationResultAdmin(admin.ModelAdmin):
    list_display = ('calculation', 'entity', 'indicator', 'variable_name', 'value', 'created_at')
    search_fields = (
        'calculation__name',
        'entity__code',
        'entity__name',
        'indicator__indicator',
        'indicator__name',
        'variable_name',
    )
    list_filter = ('created_at', 'calculation__status', 'calculation__period__year', 'entity')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('calculation', 'entity', 'indicator')
    list_select_related = ('calculation', 'entity', 'indicator')
