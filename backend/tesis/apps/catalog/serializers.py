from rest_framework import serializers

from .models import Entity, Period


class EntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entity
        fields = [
            'id', 'code', 'name', 'description',
            'is_consolidated', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class PeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Period
        fields = ['id', 'year', 'month', 'period_type', 'is_active', 'created_at']
        read_only_fields = ['created_at']

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError('El mes debe estar entre 1 y 12.')
        return value

    def validate_year(self, value):
        if not 2000 <= value <= 2100:
            raise serializers.ValidationError('El ano debe estar entre 2000 y 2100.')
        return value
