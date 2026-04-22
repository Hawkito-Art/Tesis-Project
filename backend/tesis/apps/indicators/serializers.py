from rest_framework import serializers

from .models import Indicator, IndicatorGroup, IndicatorRecord, IndicatorVariable


class IndicatorGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndicatorGroup
        fields = ['id', 'name', 'group_type', 'order', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class IndicatorVariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndicatorVariable
        fields = ['id', 'indicator', 'name', 'label', 'description', 'is_active']
        read_only_fields = []

    def validate(self, attrs):
        indicator = attrs.get('indicator', getattr(self.instance, 'indicator', None))
        name = attrs.get('name', getattr(self.instance, 'name', None))

        if indicator and name:
            queryset = IndicatorVariable.objects.filter(indicator=indicator, name=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {'name': 'Ya existe una variable con ese nombre para este indicador.'}
                )

        return attrs


class IndicatorSerializer(serializers.ModelSerializer):
    variables = IndicatorVariableSerializer(many=True, read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Indicator
        fields = [
            'id', 'indicator', 'name', 'description', 'unit',
            'group', 'group_name', 'variables',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class IndicatorRecordSerializer(serializers.ModelSerializer):
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    indicator_code = serializers.CharField(source='indicator.indicator', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    import_job_id = serializers.IntegerField(source='import_job.id', read_only=True)
    calculation_id = serializers.IntegerField(source='calculation.id', read_only=True)

    class Meta:
        model = IndicatorRecord
        fields = [
            'id', 'entity', 'indicator', 'period',
            'variable_name', 'value',
            'source', 'source_display', 'import_job', 'import_job_id', 'calculation', 'calculation_id',
            'entity_code', 'indicator_code', 'period_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        indicator = attrs.get('indicator', getattr(self.instance, 'indicator', None))
        variable_name = attrs.get('variable_name', getattr(self.instance, 'variable_name', None))

        if indicator and variable_name:
            exists = IndicatorVariable.objects.filter(
                indicator=indicator,
                name=variable_name,
                is_active=True,
            ).exists()
            if not exists:
                raise serializers.ValidationError(
                    {
                        'variable_name': (
                            f'La variable "{variable_name}" no existe '
                            f'para el indicador "{indicator.indicator}".'
                        ),
                    }
                )
        return attrs
