import django_filters

from .models import IndicatorRecord


class IndicatorRecordFilter(django_filters.FilterSet):
    group = django_filters.NumberFilter(field_name='indicator__group_id')

    class Meta:
        model = IndicatorRecord
        fields = ['entity', 'indicator', 'period', 'group', 'variable_name']
