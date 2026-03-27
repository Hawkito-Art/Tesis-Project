from rest_framework import serializers

from .models import EntityClassification


class EntityClassificationSerializer(serializers.ModelSerializer):
    entity_code = serializers.CharField(source='entity.code', read_only=True)
    period_display = serializers.CharField(source='period.__str__', read_only=True)

    class Meta:
        model = EntityClassification
        fields = [
            'id', 'entity', 'period', 'classification_type', 'value',
            'description',
            'entity_code', 'period_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
