from rest_framework import serializers

from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator

from .models import EntityClassification, Report


class ReportGenerateRequestSerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.all())
    report_type = serializers.ChoiceField(
        choices=Report.REPORT_TYPE_CHOICES,
        default=Report.REPORT_TYPE_OPERATIONAL,
    )
    include_stats = serializers.BooleanField(default=True)
    include_classifications = serializers.BooleanField(default=True)
    filters = serializers.DictField(required=False, default=dict)

    def validate_entity(self, value):
        if not value.is_active:
            raise serializers.ValidationError('La entidad seleccionada no esta activa.')
        return value

    def validate_period(self, value):
        if not value.is_active:
            raise serializers.ValidationError('El periodo seleccionado no esta activo.')
        return value


class ReportListQuerySerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.all(), required=False)
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=Report.STATUS_CHOICES, required=False)
    ordering = serializers.ChoiceField(
        choices=['id', 'created_at', 'updated_at', '-id', '-created_at', '-updated_at'],
        required=False,
        default='-created_at',
    )
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
    created_from = serializers.DateField(required=False)
    created_to = serializers.DateField(required=False)

    def validate(self, attrs):
        created_from = attrs.get('created_from')
        created_to = attrs.get('created_to')
        if created_from and created_to and created_from > created_to:
            raise serializers.ValidationError(
                {'created_to': 'created_to debe ser mayor o igual que created_from.'}
            )
        return attrs


class ReportSerializer(serializers.ModelSerializer):
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id',
            'entity',
            'period',
            'report_type',
            'status',
            'summary',
            'detail',
            'metadata',
            'generated_by',
            'generated_by_email',
            'generated_at',
            'entity_code',
            'period_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['generated_at', 'created_at', 'updated_at']


class ReportOutputSerializer(serializers.Serializer):
    summary = serializers.DictField()
    detail = serializers.DictField()
    metadata = serializers.DictField()


class EntityClassificationSerializer(serializers.ModelSerializer):
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)

    class Meta:
        model = EntityClassification
        fields = [
            'id', 'entity', 'period', 'classification_type', 'value',
            'description',
            'rule_version', 'criteria_snapshot',
            'entity_code', 'period_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class EntityClassificationCalculateRequestSerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.all())
    classification_type = serializers.CharField(required=False, default='overall_performance', max_length=100)

    def validate_entity(self, value):
        if not value.is_active:
            raise serializers.ValidationError('La entidad seleccionada no esta activa.')
        return value

    def validate_period(self, value):
        if not value.is_active:
            raise serializers.ValidationError('El periodo seleccionado no esta activo.')
        return value


class EntityClassificationListQuerySerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.all(), required=False)
    category = serializers.CharField(required=False, source='value')
    classification_type = serializers.CharField(required=False)
    ordering = serializers.ChoiceField(
        choices=['id', 'created_at', 'updated_at', '-id', '-created_at', '-updated_at'],
        required=False,
        default='-created_at',
    )
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)


class ReportStatsQuerySerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.all(), required=False)
    indicator = serializers.PrimaryKeyRelatedField(queryset=Indicator.objects.all(), required=False)


class ReportStatsOutputSerializer(serializers.Serializer):
    filters_applied = serializers.DictField()
    totals = serializers.DictField()
    records_by_source = serializers.DictField()
    records_by_indicator = serializers.DictField()
    average_value_by_indicator = serializers.DictField()
    latest_calculation = serializers.DictField()
