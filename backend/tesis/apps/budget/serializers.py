from rest_framework import serializers

from apps.catalog.models import Entity, Period

from .models import Budget, BudgetItem


class BudgetItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = BudgetItem
        fields = [
            'id', 'budget', 'item_type', 'code', 'name',
            'planned_amount', 'actual_amount',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_planned_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('El monto planificado no puede ser negativo.')
        return value

    def validate_actual_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('El monto real no puede ser negativo.')
        return value


class BudgetSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True, read_only=True)
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    period_display = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'entity', 'period', 'entity_code', 'period_display',
            'description', 'items', 'is_active',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def validate(self, attrs):
        entity = attrs.get('entity')
        period = attrs.get('period')

        if entity and period:
            if not Entity.objects.filter(pk=entity.pk, is_active=True).exists():
                raise serializers.ValidationError(
                    {'entity': 'La entidad no existe o esta inactiva.'}
                )
            if not Period.objects.filter(pk=period.pk, is_active=True).exists():
                raise serializers.ValidationError(
                    {'period': 'El periodo no existe o esta inactivo.'}
                )
        return attrs
