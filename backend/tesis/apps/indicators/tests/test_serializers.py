from django.test import TestCase

from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorRecord
from apps.indicators.serializers import IndicatorRecordSerializer


class IndicatorRecordSerializerTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(code='ENT-VAL', name='Entidad Validacion', type='empresa')
        self.period = Period.objects.create(year=2026, month=3, period_type='mensual')
        self.indicator_a = Indicator.objects.get(indicator='VENTAS_TOT')
        self.indicator_b = Indicator.objects.get(indicator='CORR_SM_PROD')

    def test_rejects_variable_name_not_belonging_to_indicator(self):
        serializer = IndicatorRecordSerializer(
            data={
                'entity': self.entity.id,
                'indicator': self.indicator_a.id,
                'period': self.period.id,
                'variable_name': 'variable_inexistente',
                'value': '10.0000',
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('variable_name', serializer.errors)

    def test_accepts_valid_standard_variable_for_indicator(self):
        serializer = IndicatorRecordSerializer(
            data={
                'entity': self.entity.id,
                'indicator': self.indicator_a.id,
                'period': self.period.id,
                'variable_name': 'plan_anual',
                'value': '100.0000',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_exposes_traceability_fields(self):
        record = IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=self.indicator_a,
            period=self.period,
            variable_name='plan_anual',
            value='100.0000',
            source='manual',
        )

        serializer = IndicatorRecordSerializer(record)

        self.assertEqual(serializer.data['source'], 'manual')
        self.assertEqual(serializer.data['source_display'], 'Manual')
        self.assertIsNone(serializer.data['import_job'])
        self.assertIsNone(serializer.data['calculation'])

    def test_partial_update_revalidates_variable_indicator_match(self):
        record = IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=self.indicator_a,
            period=self.period,
            variable_name='plan_anual',
            value='1.0000',
        )

        serializer = IndicatorRecordSerializer(
            record,
            data={'variable_name': 'variable_inexistente'},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('variable_name', serializer.errors)
