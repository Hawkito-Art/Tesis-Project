from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, UserRole
from apps.indicators.models import Indicator, IndicatorGroup
from apps.catalog.models import Entity, Period
from apps.indicators.models import IndicatorRecord

User = get_user_model()


class IndicatorGroupApiTestCase(APITestCase):
    def setUp(self):
        self.groups_url = '/api/indicators/groups/'
        self.admin_user = User.objects.create_user(
            email='admin-indicators@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            email='regular-indicators@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.regular_user, role=analyst_role)

    def test_groups_list_requires_authentication(self):
        response = self.client.get(self.groups_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_groups_list_allows_authenticated_read(self):
        IndicatorGroup.objects.create(name='Grupo X', group_type='otro', order=9)
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.groups_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 4)

    def test_group_create_requires_admin(self):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.post(
            self.groups_url,
            {'name': 'Nuevo Grupo', 'group_type': 'otro', 'order': 10},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_create_patch_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        create_response = self.client.post(
            self.groups_url,
            {'name': 'Temporal', 'group_type': 'otro', 'order': 10},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        group_id = create_response.data['id']

        patch_response = self.client.patch(
            f'/api/indicators/groups/{group_id}/',
            {'name': 'Temporal Editado', 'order': 11},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], 'Temporal Editado')

        delete_response = self.client.delete(
            f'/api/indicators/groups/{group_id}/',
            format='json',
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(IndicatorGroup.objects.filter(id=group_id).exists())


class IndicatorApiTestCase(APITestCase):
    def setUp(self):
        self.indicators_url = '/api/indicators/'
        self.admin_user = User.objects.create_user(
            email='admin-indicator@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-indicator@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

        self.group_fundamental = IndicatorGroup.objects.get(group_type='fundamental')
        self.group_otro = IndicatorGroup.objects.get(group_type='otro')

    def test_indicators_list_requires_authentication(self):
        response = self.client.get(self.indicators_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_indicators_list_allows_analyst_and_supports_search(self):
        self.client.force_authenticate(user=self.analyst_user)

        response = self.client.get(
            self.indicators_url,
            {'search': 'VENTAS_TOT'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['indicator'], 'VENTAS_TOT')

    def test_indicator_create_requires_admin(self):
        self.client.force_authenticate(user=self.analyst_user)

        payload = {
            'indicator': 'TEST_IND_NO_ADMIN',
            'name': 'Indicador sin admin',
            'unit': 'MP',
            'group': self.group_otro.id,
            'is_active': True,
        }
        response = self.client.post(self.indicators_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_indicator_create_patch_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            'indicator': 'TEST_IND_ADMIN',
            'name': 'Indicador admin',
            'unit': 'U',
            'group': self.group_otro.id,
            'is_active': True,
        }
        create_response = self.client.post(self.indicators_url, payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        indicator_id = create_response.data['id']

        patch_response = self.client.patch(
            f'/api/indicators/{indicator_id}/',
            {'name': 'Indicador admin editado', 'group': self.group_fundamental.id},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], 'Indicador admin editado')

        delete_response = self.client.delete(f'/api/indicators/{indicator_id}/', format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Indicator.objects.filter(id=indicator_id).exists())

    def test_indicators_filter_by_group_and_unit(self):
        Indicator.objects.create(
            indicator='TEST_FILTER_MP',
            name='Indicador filtro MP',
            unit='MP',
            group=self.group_fundamental,
            is_active=True,
        )
        Indicator.objects.create(
            indicator='TEST_FILTER_U',
            name='Indicador filtro U',
            unit='U',
            group=self.group_otro,
            is_active=True,
        )

        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.indicators_url,
            {'group': self.group_fundamental.id, 'unit': 'MP', 'ordering': 'indicator'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        returned_codes = {item['indicator'] for item in response.data['results']}
        self.assertIn('TEST_FILTER_MP', returned_codes)


class IndicatorVariableApiTestCase(APITestCase):
    def setUp(self):
        self.variables_url = '/api/indicators/variables/'
        self.admin_user = User.objects.create_user(
            email='admin-variable@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-variable@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

        self.indicator = Indicator.objects.get(indicator='VENTAS_TOT')

    def test_variables_list_requires_authentication(self):
        response = self.client.get(self.variables_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_variables_list_allows_analyst(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.variables_url,
            {'indicator': self.indicator.id, 'ordering': 'name'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 8)

    def test_variable_create_requires_admin(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.post(
            self.variables_url,
            {
                'indicator': self.indicator.id,
                'name': 'custom_no_admin',
                'label': 'Custom no admin',
                'description': '',
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_variable_create_patch_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        create_response = self.client.post(
            self.variables_url,
            {
                'indicator': self.indicator.id,
                'name': 'custom_admin_var',
                'label': 'Custom admin var',
                'description': 'var temporal',
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        variable_id = create_response.data['id']

        patch_response = self.client.patch(
            f'/api/indicators/variables/{variable_id}/',
            {'label': 'Custom admin var editada'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['label'], 'Custom admin var editada')

        delete_response = self.client.delete(f'/api/indicators/variables/{variable_id}/', format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_variable_uniqueness_per_indicator_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.variables_url,
            {
                'indicator': self.indicator.id,
                'name': 'plan_anual',
                'label': 'Duplicada',
                'description': '',
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        details = response.data['error'].get('details', {})
        self.assertTrue('name' in details or 'non_field_errors' in details)


class IndicatorRecordApiTestCase(APITestCase):
    def setUp(self):
        self.records_url = '/api/indicators/records/'
        self.admin_user = User.objects.create_user(
            email='admin-record@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-record@test.com',
            password='Passw0rd!123',
        )
        self.regular_user = User.objects.create_user(
            email='regular-record@test.com',
            password='Passw0rd!123',
        )
        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

        self.entity_a = Entity.objects.create(code='ENT-A', name='Entidad A', type='empresa')
        self.entity_b = Entity.objects.create(code='ENT-B', name='Entidad B', type='empresa')
        self.period_1 = Period.objects.create(year=2026, month=1, period_type='mensual')
        self.period_2 = Period.objects.create(year=2026, month=2, period_type='mensual')

        self.indicator_fundamental = Indicator.objects.get(indicator='VENTAS_TOT')
        self.indicator_otro = Indicator.objects.get(indicator='CORR_SM_PROD')

        IndicatorRecord.objects.create(
            entity=self.entity_a,
            indicator=self.indicator_fundamental,
            period=self.period_1,
            variable_name='plan_anual',
            value='10.0000',
            source='manual',
        )
        IndicatorRecord.objects.create(
            entity=self.entity_a,
            indicator=self.indicator_fundamental,
            period=self.period_2,
            variable_name='real_acumulado',
            value='20.0000',
            source='manual',
        )
        IndicatorRecord.objects.create(
            entity=self.entity_b,
            indicator=self.indicator_otro,
            period=self.period_2,
            variable_name='plan_anual',
            value='30.0000',
            source='manual',
        )

    def test_records_list_requires_authentication(self):
        response = self.client.get(self.records_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_records_list_forbidden_for_user_without_allowed_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.records_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_records_list_allows_analyst_with_pagination(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(self.records_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3)

    def test_records_filters_support_composition(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.records_url,
            {
                'entity': self.entity_a.id,
                'indicator': self.indicator_fundamental.id,
                'group': self.indicator_fundamental.group_id,
                'period': self.period_2.id,
                'variable_name': 'real_acumulado',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['value'], '20.0000')
        self.assertEqual(response.data['results'][0]['source'], 'manual')
        self.assertEqual(response.data['results'][0]['source_display'], 'Manual')

    def test_records_ordering_works(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(
            self.records_url,
            {'ordering': 'value'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        values = [item['value'] for item in response.data['results']]
        self.assertEqual(values, ['10.0000', '20.0000', '30.0000'])
