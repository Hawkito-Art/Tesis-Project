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

    class Meta:
        model = IndicatorRecord
        fields = [
            'id', 'entity', 'indicator', 'period',
            'variable_name', 'value',
            'entity_code', 'indicator_code', 'period_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        indicator = attrs.get('indicator')
        variable_name = attrs.get('variable_name')

        if indicator and variable_name:
            exists = IndicatorVariable.objects.filter(
                indicator=indicator,
                name=variable_name,
                is_active=True,
            ).exists()
            if not exists:
                raise serializers.ValidationError({
                    'variable_name': (
                        f'La variable "{variable_name}" no existe '
                        f'para el indicador "{indicator.indicator}".'
                    ),
                })
        return attrs
