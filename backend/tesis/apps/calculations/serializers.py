from rest_framework import serializers

from apps.catalog.models import Entity, Period

from .models import Calculation, CalculationResult


class CalculationResultSerializer(serializers.ModelSerializer):
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    indicator_code = serializers.CharField(source='indicator.indicator', read_only=True)

    class Meta:
        model = CalculationResult
        fields = [
            'id', 'calculation', 'entity', 'indicator',
            'variable_name', 'value',
            'entity_code', 'indicator_code',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_value(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('El valor no puede ser negativo.')
        return value


class CalculationSerializer(serializers.ModelSerializer):
    results = CalculationResultSerializer(many=True, read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)
    executed_by_email = serializers.EmailField(source='executed_by.email', read_only=True)

    class Meta:
        model = Calculation
        fields = [
            'id', 'name', 'description', 'period', 'period_display',
            'status', 'executed_by', 'executed_by_email',
            'results',
            'started_at', 'finished_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'status', 'executed_by', 'started_at', 'finished_at',
            'created_at', 'updated_at',
        ]


class CalculationRunSerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.filter(is_active=True))
    period = serializers.PrimaryKeyRelatedField(queryset=Period.objects.filter(is_active=True))
    name = serializers.CharField(max_length=255, required=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_blank=True)


class CalculationExportXlsxSerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(is_active=True),
        required=False,
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.filter(is_active=True),
        required=False,
    )


class CalculationListSerializer(serializers.ModelSerializer):
    period_display = serializers.CharField(source='period.__str__', read_only=True)
    executed_by_email = serializers.EmailField(source='executed_by.email', read_only=True)

    class Meta:
        model = Calculation
        fields = [
            'id', 'name', 'description', 'period', 'period_display',
            'status', 'executed_by', 'executed_by_email',
            'started_at', 'finished_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class CalculationResultListQuerySerializer(serializers.Serializer):
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(is_active=True),
        required=False,
    )
    indicator = serializers.IntegerField(required=False, min_value=1)
    variable_name = serializers.CharField(required=False, allow_blank=False, max_length=100)
    ordering = serializers.ChoiceField(
        choices=[
            'id',
            '-id',
            'created_at',
            '-created_at',
            'value',
            '-value',
            'variable_name',
            '-variable_name',
        ],
        required=False,
        default='-id',
    )
