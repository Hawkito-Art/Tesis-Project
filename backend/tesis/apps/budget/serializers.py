from django.db import IntegrityError
from rest_framework import serializers

from apps.catalog.models import Entity, Period

from .models import Budget, BudgetItem


class BudgetItemSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=50)
    name = serializers.CharField(required=True, max_length=255)

    class Meta:
        model = BudgetItem
        fields = [
            'id',
            'budget',
            'item_type',
            'code',
            'name',
            'planned_amount',
            'actual_amount',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_code(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('El codigo es obligatorio.')
        return cleaned

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('El nombre es obligatorio.')
        return cleaned

    def validate_planned_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('El monto planificado no puede ser negativo.')
        return value

    def validate_actual_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('El monto real no puede ser negativo.')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        budget = attrs.get('budget', getattr(self.instance, 'budget', None))

        if budget is None:
            return attrs

        if budget.status == Budget.STATUS_CLOSED:
            raise serializers.ValidationError(
                {'non_field_errors': ['No se permiten cambios en partidas de un presupuesto cerrado.']}
            )

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    'non_field_errors': [
                        'Ya existe una partida con ese codigo y tipo para el presupuesto.'
                    ]
                }
            ) from exc

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    'non_field_errors': [
                        'Ya existe una partida con ese codigo y tipo para el presupuesto.'
                    ]
                }
            ) from exc


class BudgetSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True, read_only=True)
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id',
            'entity',
            'period',
            'entity_code',
            'period_display',
            'description',
            'status',
            'items',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def validate(self, attrs):
        attrs = super().validate(attrs)

        entity = attrs.get('entity', getattr(self.instance, 'entity', None))
        period = attrs.get('period', getattr(self.instance, 'period', None))

        if entity and not Entity.objects.filter(pk=entity.pk, is_active=True).exists():
            raise serializers.ValidationError({'entity': 'La entidad no existe o esta inactiva.'})
        if period and not Period.objects.filter(pk=period.pk, is_active=True).exists():
            raise serializers.ValidationError({'period': 'El periodo no existe o esta inactivo.'})

        if self.instance and self.instance.status == Budget.STATUS_CLOSED and attrs:
            raise serializers.ValidationError(
                {'non_field_errors': ['No se permite editar un presupuesto cerrado.']}
            )

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'non_field_errors': ['Ya existe un presupuesto para esa entidad y periodo.']}
            ) from exc

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'non_field_errors': ['Ya existe un presupuesto para esa entidad y periodo.']}
            ) from exc
