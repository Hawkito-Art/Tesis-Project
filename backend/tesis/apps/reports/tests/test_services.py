from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.calculations.models import Calculation, CalculationResult
from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator
from apps.reports.models import EntityClassification
from apps.indicators.models import IndicatorRecord
from apps.reports.services import build_stats_payload, calculate_entity_classification

User = get_user_model()


class EntityClassificationServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='svc-reports@test.com', password='Passw0rd!123')
        self.entity = Entity.objects.create(code='ENT-R7', name='Entidad R7', type='empresa')
        self.period = Period.objects.create(year=2026, month=4, period_type='mensual')
        self.indicator = Indicator.objects.get(indicator='VENTAS_TOT')

    def _create_result(self, *, value: str):
        calculation = Calculation.objects.create(
            name=f'calc-{value}',
            period=self.period,
            status='completado',
            executed_by=self.user,
        )
        return CalculationResult.objects.create(
            calculation=calculation,
            entity=self.entity,
            indicator=self.indicator,
            variable_name=f'var_{calculation.id}',
            value=value,
        )

    def test_calculate_entity_classification_creates_high_performance(self):
        self._create_result(value='90.0000')
        self._create_result(value='85.0000')

        classification = calculate_entity_classification(entity=self.entity, period=self.period)

        self.assertEqual(classification.value, 'alto_desempeno')
        self.assertEqual(classification.rule_version, EntityClassification.RULE_VERSION_INITIAL)
        self.assertEqual(classification.criteria_snapshot['input']['calculation_results_count'], 2)
        self.assertEqual(classification.criteria_snapshot['input']['average_value'], 87.5)

    def test_calculate_entity_classification_is_reproducible_without_duplicates(self):
        self._create_result(value='70.0000')
        self._create_result(value='75.0000')

        first = calculate_entity_classification(entity=self.entity, period=self.period)
        second = calculate_entity_classification(entity=self.entity, period=self.period)

        self.assertEqual(first.id, second.id)
        self.assertEqual(second.value, 'desempeno_medio')
        self.assertEqual(
            EntityClassification.objects.filter(
                entity=self.entity,
                period=self.period,
                classification_type='overall_performance',
            ).count(),
            1,
        )

    def test_calculate_entity_classification_returns_sin_datos_when_no_results(self):
        classification = calculate_entity_classification(entity=self.entity, period=self.period)

        self.assertEqual(classification.value, 'sin_datos')
        self.assertIn('No existen resultados', classification.description)
        self.assertIsNone(classification.criteria_snapshot['input']['average_value'])

    def test_calculate_entity_classification_creates_low_performance(self):
        self._create_result(value='40.0000')
        self._create_result(value='50.0000')

        classification = calculate_entity_classification(entity=self.entity, period=self.period)

        self.assertEqual(classification.value, 'desempeno_bajo')
        self.assertEqual(classification.criteria_snapshot['input']['average_value'], 45.0)


class ReportStatsServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='svc-stats@test.com', password='Passw0rd!123')
        self.entity_a = Entity.objects.create(code='ENT-SA', name='Entidad Stats A', type='empresa')
        self.entity_b = Entity.objects.create(code='ENT-SB', name='Entidad Stats B', type='empresa')
        self.period = Period.objects.create(year=2026, month=4, period_type='mensual')
        self.indicator = Indicator.objects.get(indicator='VENTAS_TOT')

    def test_build_stats_payload_consistent_with_input_records(self):
        IndicatorRecord.objects.create(
            entity=self.entity_a,
            indicator=self.indicator,
            period=self.period,
            variable_name='plan_anual',
            value='100.0000',
            source=IndicatorRecord.SOURCE_IMPORTED,
        )
        IndicatorRecord.objects.create(
            entity=self.entity_a,
            indicator=self.indicator,
            period=self.period,
            variable_name='real_acumulado',
            value='80.0000',
            source=IndicatorRecord.SOURCE_CALCULATED,
        )
        IndicatorRecord.objects.create(
            entity=self.entity_b,
            indicator=self.indicator,
            period=self.period,
            variable_name='plan_anual',
            value='90.0000',
            source=IndicatorRecord.SOURCE_MANUAL,
        )

        payload = build_stats_payload(period=self.period)

        self.assertEqual(payload['totals']['indicator_records'], 3)
        self.assertEqual(payload['totals']['distinct_entities'], 2)
        self.assertEqual(payload['records_by_source']['imported'], 1)
        self.assertEqual(payload['records_by_source']['calculated'], 1)
        self.assertEqual(payload['records_by_source']['manual'], 1)
        self.assertEqual(payload['records_by_indicator'][self.indicator.indicator], 3)
        self.assertEqual(payload['average_value_by_indicator'][self.indicator.indicator], 90.0)

    def test_build_stats_payload_ignores_null_values_for_average(self):
        IndicatorRecord.objects.create(
            entity=self.entity_a,
            indicator=self.indicator,
            period=self.period,
            variable_name='plan_anual',
            value=None,
            source=IndicatorRecord.SOURCE_IMPORTED,
        )

        payload = build_stats_payload(entity=self.entity_a, period=self.period, indicator=self.indicator)

        self.assertEqual(payload['totals']['indicator_records'], 1)
        self.assertEqual(payload['totals']['distinct_entities'], 1)
        self.assertEqual(payload['average_value_by_indicator'], {})
