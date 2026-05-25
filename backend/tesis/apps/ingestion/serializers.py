from rest_framework import serializers

from apps.catalog.models import Entity, Period

from .models import Document, DocumentDetail, ImportJob


class DocumentUploadSerializer(serializers.Serializer):
    IMPORT_TYPE_CHOICES = [
        ('presupuesto', 'Presupuesto'),
        ('indicadores', 'Indicadores'),
        ('registros', 'Registros de indicadores'),
    ]

    name = serializers.CharField(max_length=255)
    file = serializers.FileField()
    import_type = serializers.ChoiceField(choices=IMPORT_TYPE_CHOICES)
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )

    def validate_file(self, value):
        filename = (value.name or '').lower()
        if not filename.endswith('.xlsx'):
            raise serializers.ValidationError(
                'Solo se permiten archivos con extension .xlsx.'
            )
        return value


class ImportJobExecutionSerializer(serializers.Serializer):
    document = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())


class ImportJobProcessSerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(is_active=True)
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.filter(is_active=True)
    )


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    import_type_display = serializers.CharField(source='get_import_type_display', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'name', 'file', 'import_type', 'import_type_display', 'status',
            'uploaded_by', 'uploaded_by_email',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'uploaded_by', 'created_at', 'updated_at']


class EntityBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'code', 'name']


class PeriodBasicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Period
        fields = ['id', 'name', 'year', 'month']

    def get_name(self, obj):
        month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
        }
        month_name = month_names.get(obj.month, str(obj.month).zfill(2))
        return f'{month_name} {obj.year} ({obj.period_type})'


class DocumentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentDetail
        fields = [
            'id', 'import_job', 'row_number',
            'raw_data', 'is_valid', 'error_message',
            'created_at',
        ]
        read_only_fields = ['created_at']


class ImportJobSerializer(serializers.ModelSerializer):
    details = DocumentDetailSerializer(many=True, read_only=True)
    document_name = serializers.CharField(source='document.name', read_only=True)
    document_import_type = serializers.CharField(source='document.import_type', read_only=True)
    entity_detail = EntityBasicSerializer(source='entity', read_only=True)
    period_detail = PeriodBasicSerializer(source='period', read_only=True)

    class Meta:
        model = ImportJob
        fields = [
            'id', 'document', 'document_name', 'document_import_type',
            'entity', 'entity_detail', 'period', 'period_detail',
            'status',
            'total_rows', 'processed_rows', 'error_rows',
            'error_log', 'details',
            'started_at', 'finished_at', 'created_at',
        ]
        read_only_fields = [
            'entity', 'period', 'status',
            'total_rows', 'processed_rows', 'error_rows',
            'error_log', 'started_at', 'finished_at', 'created_at',
        ]


class ImportJobListSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document.name', read_only=True)
    document_import_type = serializers.CharField(source='document.import_type', read_only=True)
    entity_detail = EntityBasicSerializer(source='entity', read_only=True)
    period_detail = PeriodBasicSerializer(source='period', read_only=True)

    class Meta:
        model = ImportJob
        fields = [
            'id', 'document', 'document_name', 'document_import_type',
            'entity', 'entity_detail', 'period', 'period_detail',
            'status',
            'total_rows', 'processed_rows', 'error_rows',
            'error_log',
            'started_at', 'finished_at', 'created_at',
        ]
        read_only_fields = fields
