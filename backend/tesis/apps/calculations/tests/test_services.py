from decimal import Decimal

from django.test import TestCase

from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorGroup, IndicatorRecord
from apps.calculations.services import compute_standard_derived_values, run_formula_engine


class CalculationFormulaServiceTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(code='ENT-CALC', name='Entidad Cálculo', type='empresa')
        self.period = Period.objects.create(year=2026, month=7, period_type='mensual')
        self.group = IndicatorGroup.objects.get(group_type='otro')

    def _create_indicator(self, code: str, name: str, unit: str = 'MP') -> Indicator:
        return Indicator.objects.create(
            indicator=code,
            name=name,
            unit=unit,
            group=self.group,
        )

    def _record(self, indicator, variable_name, value):
        IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=indicator,
            period=self.period,
            variable_name=variable_name,
            value=value,
        )

    def test_compute_standard_values_with_business_formulas(self):
        values = compute_standard_derived_values(
            plan_acumulado=Decimal('145881.2'),
            real_acumulado=Decimal('121785.0'),
            ano_anterior=Decimal('100209.3'),
        )

        self.assertEqual(values['porcentaje_r_p'], Decimal('83.4823'))
        self.assertEqual(values['real_aa'], Decimal('121.5306'))
        self.assertEqual(values['estimado_prox_mes'], Decimal('133963.5000'))

    def test_compute_standard_values_division_by_zero_returns_zero(self):
        values = compute_standard_derived_values(
            plan_acumulado=Decimal('0'),
            real_acumulado=Decimal('121785.0'),
            ano_anterior=None,
        )

        self.assertEqual(values['porcentaje_r_p'], Decimal('0'))
        self.assertEqual(values['real_aa'], Decimal('0'))
        self.assertEqual(values['estimado_prox_mes'], Decimal('133963.5000'))

    def test_run_formula_engine_includes_correlation_indicator(self):
        ventas = self._create_indicator('VENTAS_TOT_CALC', 'Ventas Totales Calc')
        salario = self._create_indicator('SALARIO_MED_CALC', 'Salario Medio', unit='p')
        productividad = self._create_indicator('PROD_TRAB_CALC', 'Productividad del Trabajo', unit='p')
        correlacion = self._create_indicator(
            'CORR_SM_PT_CALC',
            'Correlación Salario Medio/Product.',
            unit='Coef',
        )

        for variable_name, value in (
            ('plan_acumulado', Decimal('145881.2')),
            ('real_acumulado', Decimal('121785.0')),
            ('ano_anterior', Decimal('100209.3')),
        ):
            self._record(ventas, variable_name, value)

        for variable_name, value in (
            ('plan_anual', Decimal('4091.00')),
            ('ano_anterior', Decimal('2917.00')),
            ('plan_acumulado', Decimal('4091.00')),
            ('real_acumulado', Decimal('2980.00')),
        ):
            self._record(salario, variable_name, value)

        for variable_name, value in (
            ('plan_anual', Decimal('43815.00')),
            ('ano_anterior', Decimal('30571.00')),
            ('plan_acumulado', Decimal('43815.00')),
            ('real_acumulado', Decimal('48628.00')),
        ):
            self._record(productividad, variable_name, value)

        # Presencia del indicador de correlación en records base para que el motor lo incluya.
        self._record(correlacion, 'plan_anual', Decimal('0'))

        result = run_formula_engine(entity=self.entity, period=self.period)

        self.assertIn(ventas.id, result)
        self.assertIn(correlacion.id, result)
        self.assertEqual(result[ventas.id]['estimado_prox_mes'], Decimal('133963.5000'))
        self.assertEqual(result[correlacion.id]['plan_anual'], Decimal('0.0934'))
        self.assertEqual(result[correlacion.id]['ano_anterior'], Decimal('0.0954'))
        self.assertEqual(result[correlacion.id]['real_acumulado'], Decimal('0.0613'))

    def test_run_formula_engine_handles_zero_division_in_records(self):
        ventas = self._create_indicator('VENTAS_TOT_ZERO', 'Ventas Totales Zero')
        self._record(ventas, 'plan_acumulado', Decimal('0'))
        self._record(ventas, 'real_acumulado', Decimal('200.00'))
        self._record(ventas, 'ano_anterior', Decimal('0'))

        result = run_formula_engine(entity=self.entity, period=self.period)

        self.assertEqual(result[ventas.id]['porcentaje_r_p'], Decimal('0'))
        self.assertEqual(result[ventas.id]['real_aa'], Decimal('0'))
        self.assertEqual(result[ventas.id]['estimado_prox_mes'], Decimal('220.0000'))

    def test_execute_manual_calculation_persists_traceability_in_indicator_records(self):
        from django.contrib.auth import get_user_model

        from apps.calculations.services import execute_manual_calculation

        user = get_user_model().objects.create_user(
            email='trace-calc@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        ventas = self._create_indicator('VENTAS_TOT_TRACE', 'Ventas Totales Trace')
        self._record(ventas, 'plan_acumulado', Decimal('145881.2'))
        self._record(ventas, 'real_acumulado', Decimal('121785.0'))
        self._record(ventas, 'ano_anterior', Decimal('100209.3'))

        calculation = execute_manual_calculation(
            entity=self.entity,
            period=self.period,
            user=user,
            name='calculo trazable',
            description='test',
        )

        derived = IndicatorRecord.objects.get(
            entity=self.entity,
            period=self.period,
            indicator=ventas,
            variable_name='porcentaje_r_p',
        )
        self.assertEqual(derived.source, IndicatorRecord.SOURCE_CALCULATED)
        self.assertEqual(derived.calculation_id, calculation.id)
        self.assertIsNone(derived.import_job_id)
