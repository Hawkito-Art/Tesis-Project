from django.contrib import admin

from .models import Budget, BudgetItem


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 0
    fields = ('item_type', 'code', 'name', 'planned_amount', 'actual_amount', 'is_active')
    show_change_link = True


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('entity', 'period', 'status', 'is_active', 'created_by', 'created_at')
    search_fields = (
        'entity__code',
        'entity__name',
        'period__year',
        'description',
        'created_by__email',
    )
    list_filter = ('status', 'is_active', 'period__year', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('entity', 'period', 'created_by')
    inlines = (BudgetItemInline,)
    list_select_related = ('entity', 'period', 'created_by')


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = (
        'budget',
        'item_type',
        'code',
        'name',
        'planned_amount',
        'actual_amount',
        'is_active',
        'created_at',
    )
    search_fields = ('code', 'name', 'budget__entity__code', 'budget__entity__name')
    list_filter = ('item_type', 'is_active', 'created_at', 'budget__period__year')
    ordering = ('budget', 'item_type', 'code')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('budget',)
    list_select_related = ('budget',)
