from django.contrib import admin

from .models import Indicator, IndicatorGroup, IndicatorRecord, IndicatorVariable


class IndicatorVariableInline(admin.TabularInline):
    model = IndicatorVariable
    extra = 0
    fields = ('name', 'label', 'is_active')
    show_change_link = True


@admin.register(IndicatorGroup)
class IndicatorGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'order', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('group_type', 'is_active', 'created_at')
    ordering = ('order', 'name')
    readonly_fields = ('created_at',)


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'name', 'unit', 'group', 'is_active', 'created_at')
    search_fields = ('indicator', 'name', 'description', 'group__name')
    list_filter = ('group', 'unit', 'is_active', 'created_at')
    ordering = ('indicator',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('group',)
    inlines = (IndicatorVariableInline,)


@admin.register(IndicatorVariable)
class IndicatorVariableAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'name', 'label', 'is_active')
    search_fields = ('name', 'label', 'description', 'indicator__indicator', 'indicator__name')
    list_filter = ('is_active', 'indicator__group')
    ordering = ('indicator', 'name')
    autocomplete_fields = ('indicator',)


@admin.register(IndicatorRecord)
class IndicatorRecordAdmin(admin.ModelAdmin):
    list_display = (
        'entity',
        'indicator',
        'period',
        'variable_name',
        'value',
        'source',
        'created_at',
    )
    search_fields = (
        'entity__code',
        'entity__name',
        'indicator__indicator',
        'indicator__name',
        'variable_name',
    )
    list_filter = (
        'source',
        'period__year',
        'period__month',
        'indicator__group',
        'entity',
        'created_at',
    )
    ordering = ('-period__year', '-period__month', 'entity__code', 'indicator__indicator')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('entity', 'indicator', 'period')
    list_select_related = ('entity', 'indicator', 'period')
