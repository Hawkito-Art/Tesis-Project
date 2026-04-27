from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, UserRole
from apps.calculations.models import Calculation, CalculationResult
from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorGroup, IndicatorRecord
from apps.reports.models import EntityClassification, Report

User = get_user_model()


class ReportsGenerateApiTestCase(APITestCase):
    def setUp(self):
        self.reports_url = '/api/reports/'
        self.admin_user = User.objects.create_user(
            email='admin-reports@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-reports@test.com',
            password='Passw0rd!123',
        )
        self.regular_user = User.objects.create_user(
            email='regular-reports@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

        self.entity = Entity.objects.create(code='ENT-R1', name='Entidad Reporte 1', type='empresa')
        self.period = Period.objects.create(year=2026, month=4, period_type='mensual')
        self.group = IndicatorGroup.objects.get(group_type='fundamental')
        self.indicator = Indicator.objects.get(indicator='VENTAS_TOT')

        IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=self.indicator,
            period=self.period,
            variable_name='plan_anual',
            value='100.0000',
            source=IndicatorRecord.SOURCE_IMPORTED,
        )
        IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=self.indicator,
            period=self.period,
            variable_name='real_acumulado',
            value='80.0000',
            source=IndicatorRecord.SOURCE_CALCULATED,
        )

        calculation = Calculation.objects.create(
            name='calc-report',
            period=self.period,
            status='completado',
            executed_by=self.admin_user,
        )
        CalculationResult.objects.create(
            calculation=calculation,
            entity=self.entity,
            indicator=self.indicator,
            variable_name='porcentaje_r_p',
            value='80.0000',
        )

    def test_post_reports_requires_authentication(self):
        response = self.client.post(
            self.reports_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_reports_forbidden_for_user_without_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            self.reports_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_reports_forbidden_for_analyst_write(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.post(
            self.reports_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_reports_generates_and_persists_report_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.reports_url,
            {
                'entity': self.entity.id,
                'period': self.period.id,
                'report_type': 'operational',
                'include_stats': True,
                'include_classifications': True,
                'filters': {'group': self.group.id},
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['entity'], self.entity.id)
        self.assertEqual(response.data['period'], self.period.id)
        self.assertEqual(response.data['report_type'], 'operational')
        self.assertEqual(response.data['status'], 'generated')
        self.assertEqual(response.data['generated_by'], self.admin_user.id)

        self.assertIn('summary', response.data)
        self.assertIn('detail', response.data)
        self.assertIn('metadata', response.data)
        self.assertIn('stats', response.data['detail'])
        self.assertIn('classifications', response.data['detail'])

        report = Report.objects.get(id=response.data['id'])
        self.assertEqual(report.entity_id, self.entity.id)
        self.assertEqual(report.period_id, self.period.id)
        self.assertEqual(report.generated_by_id, self.admin_user.id)

    def test_get_reports_list_allows_analyst_with_pagination_and_filters(self):
        Report.objects.create(
            entity=self.entity,
            period=self.period,
            report_type='operational',
            status='generated',
            summary={'total_records': 2},
            detail={'indicators': {}},
            metadata={'entity_code': self.entity.code},
            generated_by=self.admin_user,
        )
        Report.objects.create(
            entity=self.entity,
            period=self.period,
            report_type='executive',
            status='error',
            summary={'total_records': 0},
            detail={'indicators': {}},
            metadata={'entity_code': self.entity.code},
            generated_by=self.admin_user,
        )

        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.reports_url,
            {
                'entity': self.entity.id,
                'period': self.period.id,
                'report_type': 'operational',
                'status': 'generated',
                'ordering': '-created_at',
                'page_size': 5,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['report_type'], 'operational')

    def test_get_reports_list_returns_400_for_invalid_ordering(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.reports_url,
            {'ordering': 'invalid_field'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data['error'])
        self.assertIn('ordering', response.data['error']['details'])

    def test_get_reports_list_filters_by_created_date_range(self):
        report = Report.objects.create(
            entity=self.entity,
            period=self.period,
            report_type='operational',
            status='generated',
            summary={'total_records': 2},
            detail={'indicators': {}},
            metadata={'entity_code': self.entity.code},
            generated_by=self.admin_user,
        )

        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.reports_url,
            {
                'created_from': report.created_at.date().isoformat(),
                'created_to': report.created_at.date().isoformat(),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], report.id)

    def test_get_reports_list_returns_400_for_invalid_date_range(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.reports_url,
            {
                'created_from': '2026-05-01',
                'created_to': '2026-04-01',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data['error'])
        self.assertIn('created_to', response.data['error']['details'])

    def test_get_reports_detail_returns_404_when_missing(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get('/api/reports/9999/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_reports_detail_returns_report_for_analyst(self):
        report = Report.objects.create(
            entity=self.entity,
            period=self.period,
            report_type='operational',
            status='generated',
            summary={'total_records': 2},
            detail={'indicators': {}},
            metadata={'entity_code': self.entity.code},
            generated_by=self.admin_user,
        )

        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(f'/api/reports/{report.id}/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], report.id)
        self.assertEqual(response.data['entity'], self.entity.id)
        self.assertEqual(response.data['period'], self.period.id)


class ReportsStatsApiTestCase(APITestCase):
    def setUp(self):
        self.stats_url = '/api/stats/'
        self.admin_user = User.objects.create_user(
            email='admin-stats@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-stats@test.com',
            password='Passw0rd!123',
        )
        self.regular_user = User.objects.create_user(
            email='regular-stats@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

        self.entity = Entity.objects.create(code='ENT-S1', name='Entidad Stats', type='empresa')
        self.period = Period.objects.create(year=2026, month=4, period_type='mensual')
        self.indicator = Indicator.objects.get(indicator='VENTAS_TOT')

        IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=self.indicator,
            period=self.period,
            variable_name='plan_anual',
            value='100.0000',
            source=IndicatorRecord.SOURCE_IMPORTED,
        )
        IndicatorRecord.objects.create(
            entity=self.entity,
            indicator=self.indicator,
            period=self.period,
            variable_name='real_acumulado',
            value='80.0000',
            source=IndicatorRecord.SOURCE_CALCULATED,
        )

        calculation = Calculation.objects.create(
            name='calc-stats',
            period=self.period,
            status='completado',
            executed_by=self.admin_user,
        )
        CalculationResult.objects.create(
            calculation=calculation,
            entity=self.entity,
            indicator=self.indicator,
            variable_name='porcentaje_r_p',
            value='80.0000',
        )

    def test_get_stats_requires_authentication(self):
        response = self.client.get(self.stats_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_stats_forbidden_for_user_without_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.stats_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_stats_allows_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.stats_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_stats_returns_payload_for_analyst(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.stats_url,
            {
                'entity': self.entity.id,
                'period': self.period.id,
                'indicator': self.indicator.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('filters_applied', response.data)
        self.assertIn('totals', response.data)
        self.assertIn('records_by_source', response.data)
        self.assertIn('records_by_indicator', response.data)
        self.assertIn('average_value_by_indicator', response.data)
        self.assertIn('latest_calculation', response.data)

        self.assertEqual(response.data['filters_applied']['entity'], self.entity.id)
        self.assertEqual(response.data['filters_applied']['period'], self.period.id)
        self.assertEqual(response.data['filters_applied']['indicator'], self.indicator.id)
        self.assertEqual(response.data['totals']['indicator_records'], 2)
        self.assertEqual(response.data['totals']['calculation_results'], 1)

    def test_get_stats_returns_400_for_invalid_indicator(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(self.stats_url, {'indicator': 999999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data['error'])
        self.assertIn('indicator', response.data['error']['details'])


class ReportsClassificationsApiTestCase(APITestCase):
    def setUp(self):
        self.calculate_url = '/api/classifications/calculate/'
        self.list_url = '/api/classifications/'
        self.admin_user = User.objects.create_user(
            email='admin-class@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-class@test.com',
            password='Passw0rd!123',
        )
        self.regular_user = User.objects.create_user(
            email='regular-class@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

        self.entity = Entity.objects.create(code='ENT-C1', name='Entidad Clasif', type='empresa')
        self.period = Period.objects.create(year=2026, month=4, period_type='mensual')
        self.indicator = Indicator.objects.get(indicator='VENTAS_TOT')

        calc = Calculation.objects.create(
            name='calc-class',
            period=self.period,
            status='completado',
            executed_by=self.admin_user,
        )
        CalculationResult.objects.create(
            calculation=calc,
            entity=self.entity,
            indicator=self.indicator,
            variable_name='var_1',
            value='90.0000',
        )

    def test_post_classifications_calculate_requires_authentication(self):
        response = self.client.post(
            self.calculate_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_classifications_calculate_forbidden_for_analyst(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.post(
            self.calculate_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_classifications_calculate_forbidden_for_user_without_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            self.calculate_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_classifications_calculate_generates_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.calculate_url,
            {
                'entity': self.entity.id,
                'period': self.period.id,
                'classification_type': 'overall_performance',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['entity'], self.entity.id)
        self.assertEqual(response.data['period'], self.period.id)
        self.assertEqual(response.data['classification_type'], 'overall_performance')
        self.assertEqual(response.data['value'], 'alto_desempeno')
        self.assertEqual(response.data['rule_version'], 'r7-v1')
        self.assertIn('criteria_snapshot', response.data)

    def test_get_classifications_list_allows_analyst_with_filters(self):
        EntityClassification.objects.create(
            entity=self.entity,
            period=self.period,
            classification_type='overall_performance',
            value='alto_desempeno',
            description='ok',
            rule_version='r7-v1',
            criteria_snapshot={'input': {'calculation_results_count': 1, 'average_value': 90.0}},
        )

        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.list_url,
            {
                'entity': self.entity.id,
                'period': self.period.id,
                'category': 'alto_desempeno',
                'classification_type': 'overall_performance',
                'page_size': 10,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['value'], 'alto_desempeno')

    def test_get_classifications_list_requires_authentication(self):
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_classifications_list_forbidden_for_user_without_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_classifications_detail_allows_analyst(self):
        classification = EntityClassification.objects.create(
            entity=self.entity,
            period=self.period,
            classification_type='overall_performance',
            value='alto_desempeno',
            description='ok',
            rule_version='r7-v1',
            criteria_snapshot={'input': {'calculation_results_count': 1, 'average_value': 90.0}},
        )

        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(f'/api/classifications/{classification.id}/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], classification.id)
        self.assertEqual(response.data['classification_type'], 'overall_performance')

    def test_get_classifications_detail_returns_404_when_missing(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get('/api/classifications/9999/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_classifications_detail_requires_authentication(self):
        classification = EntityClassification.objects.create(
            entity=self.entity,
            period=self.period,
            classification_type='overall_performance',
            value='alto_desempeno',
            description='ok',
            rule_version='r7-v1',
            criteria_snapshot={'input': {'calculation_results_count': 1, 'average_value': 90.0}},
        )
        response = self.client.get(f'/api/classifications/{classification.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_classifications_detail_forbidden_for_user_without_role(self):
        classification = EntityClassification.objects.create(
            entity=self.entity,
            period=self.period,
            classification_type='overall_performance',
            value='alto_desempeno',
            description='ok',
            rule_version='r7-v1',
            criteria_snapshot={'input': {'calculation_results_count': 1, 'average_value': 90.0}},
        )
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(f'/api/classifications/{classification.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
