from django.contrib import admin

from .models import Document, DocumentDetail, ImportJob


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'import_type', 'status', 'uploaded_by', 'created_at', 'updated_at')
    search_fields = ('name', 'uploaded_by__email')
    list_filter = ('import_type', 'status', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('uploaded_by',)


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'document',
        'entity',
        'period',
        'status',
        'total_rows',
        'processed_rows',
        'error_rows',
        'started_at',
        'finished_at',
        'created_at',
    )
    search_fields = ('id', 'document__name', 'entity__name', 'period__name')
    list_filter = ('status', 'entity', 'period', 'created_at', 'started_at', 'finished_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('document', 'entity', 'period')


@admin.register(DocumentDetail)
class DocumentDetailAdmin(admin.ModelAdmin):
    list_display = ('import_job', 'row_number', 'is_valid', 'created_at')
    search_fields = ('import_job__id', 'error_message')
    list_filter = ('is_valid', 'created_at', 'import_job__status')
    ordering = ('-created_at',)
    readonly_fields = (
        'import_job',
        'row_number',
        'raw_data',
        'is_valid',
        'error_message',
        'created_at',
    )
    autocomplete_fields = ('import_job',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
