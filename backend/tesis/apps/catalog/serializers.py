from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from .models import Entity, Period


class EntitySerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=50)
    name = serializers.CharField(required=True, max_length=255)

    class Meta:
        model = Entity
        fields = [
            'id', 'code', 'name', 'type', 'description',
            'is_consolidated', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_code(self, value):
        normalized = value.strip().upper()
        if not normalized:
            raise serializers.ValidationError('El codigo de entidad es obligatorio.')

        allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
        if any(char not in allowed_chars for char in normalized):
            raise serializers.ValidationError(
                'El codigo solo admite letras, numeros, guion y guion bajo.'
            )

        queryset = Entity.objects.filter(code__iexact=normalized)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Ya existe una entidad con ese codigo.')

        return normalized

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('El nombre de entidad es obligatorio.')
        if len(cleaned) < 3:
            raise serializers.ValidationError(
                'El nombre de entidad debe tener al menos 3 caracteres.'
            )
        return cleaned

    def validate(self, attrs):
        attrs = super().validate(attrs)
        entity_type = attrs.get('type', getattr(self.instance, 'type', None))
        is_consolidated = attrs.get(
            'is_consolidated',
            getattr(self.instance, 'is_consolidated', False),
        )
        if entity_type == Entity.TYPE_CONSOLIDADO and not is_consolidated:
            raise serializers.ValidationError(
                {
                    'is_consolidated': [
                        'Las entidades de tipo consolidado deben marcarse como consolidadas.'
                    ]
                }
            )
        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'code': ['Ya existe una entidad con ese codigo.']}
            ) from exc

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'code': ['Ya existe una entidad con ese codigo.']}
            ) from exc


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
        current_year = timezone.now().year
        if not 2000 <= value <= current_year + 10:
            raise serializers.ValidationError(
                f'El ano debe estar entre 2000 y {current_year + 10}.'
            )
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        year = attrs.get('year', getattr(self.instance, 'year', None))
        month = attrs.get('month', getattr(self.instance, 'month', None))
        period_type = attrs.get('period_type', getattr(self.instance, 'period_type', None))

        if year is None or month is None or period_type is None:
            return attrs

        queryset = Period.objects.filter(year=year, month=month, period_type=period_type)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {'non_field_errors': ['Ya existe un periodo con ano, mes y tipo especificados.']}
            )

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'non_field_errors': ['Ya existe un periodo con ano, mes y tipo especificados.']}
            ) from exc
