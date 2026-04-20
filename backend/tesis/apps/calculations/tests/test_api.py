from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.calculations.models import Calculation, CalculationResult
from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorGroup, IndicatorRecord

User = get_user_model()


class CalculationRunApiTestCase(APITestCase):
    def setUp(self):
        self.run_url = '/api/calculations/run/'
        self.admin_user = User.objects.create_user(
            email='admin-calc@test.com', password='Passw0rd!123', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='regular-calc@test.com', password='Passw0rd!123'
        )

        self.entity = Entity.objects.create(code='ENT-CAL-01', name='Entidad Cálculo', type='empresa')
        self.period = Period.objects.create(year=2026, month=8, period_type='mensual')
        self.group = IndicatorGroup.objects.create(name='Fundamental', group_type='fundamental')
        self.ventas = Indicator.objects.create(
            indicator='VENTAS_TOT',
            name='Ventas Totales',
            unit='MP',
            group=self.group,
        )
        for variable_name, value in (
            ('plan_acumulado', Decimal('145881.2')),
            ('real_acumulado', Decimal('121785.0')),
            ('ano_anterior', Decimal('100209.3')),
            ('plan_anual', Decimal('145881.2')),
        ):
            IndicatorRecord.objects.create(
                entity=self.entity,
                indicator=self.ventas,
                period=self.period,
                variable_name=variable_name,
                value=value,
            )

    def test_run_calculation_requires_authentication(self):
        response = self.client.post(
            self.run_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_run_calculation_forbidden_for_user_without_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            self.run_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_run_calculation_creates_calculation_and_results(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.run_url,
            {
                'entity': self.entity.id,
                'period': self.period.id,
                'name': 'Calculo mensual agosto',
                'description': 'Ejecución manual',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Calculation.objects.count(), 1)
        calculation = Calculation.objects.first()
        self.assertEqual(calculation.status, 'completado')
        self.assertEqual(calculation.executed_by_id, self.admin_user.id)
        self.assertGreaterEqual(CalculationResult.objects.filter(calculation=calculation).count(), 3)

        result_map = {
            result.variable_name: result.value
            for result in CalculationResult.objects.filter(calculation=calculation, indicator=self.ventas)
        }
        self.assertEqual(result_map['porcentaje_r_p'], Decimal('83.4823'))
        self.assertEqual(result_map['real_aa'], Decimal('121.5306'))
        self.assertEqual(result_map['estimado_prox_mes'], Decimal('133963.5000'))

    def test_run_calculation_only_runs_when_endpoint_called(self):
        self.assertEqual(Calculation.objects.count(), 0)
        self.assertEqual(CalculationResult.objects.count(), 0)

    def test_run_calculation_requires_valid_payload_fields(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.run_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data['error'])
        self.assertIn('entity', response.data['error']['details'])
        self.assertIn('period', response.data['error']['details'])

    def test_run_calculation_with_zero_denominators_persists_zero_values(self):
        IndicatorRecord.objects.filter(
            entity=self.entity,
            indicator=self.ventas,
            period=self.period,
            variable_name='plan_acumulado',
        ).update(value=Decimal('0'))
        IndicatorRecord.objects.filter(
            entity=self.entity,
            indicator=self.ventas,
            period=self.period,
            variable_name='ano_anterior',
        ).update(value=Decimal('0'))

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.run_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        calculation = Calculation.objects.latest('id')
        result_map = {
            result.variable_name: result.value
            for result in CalculationResult.objects.filter(calculation=calculation, indicator=self.ventas)
        }
        self.assertEqual(result_map['porcentaje_r_p'], Decimal('0.0000'))
        self.assertEqual(result_map['real_aa'], Decimal('0.0000'))
        self.assertEqual(result_map['estimado_prox_mes'], Decimal('133963.5000'))
