from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Entity, Period

User = get_user_model()


class CalculationPermissionMatrixTestCase(APITestCase):
    def setUp(self):
        self.run_url = '/api/calculations/run/'
        self.admin_user = User.objects.create_user(
            email='admin-calc-perm@test.com', password='Passw0rd!123', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='regular-calc-perm@test.com', password='Passw0rd!123'
        )
        self.entity = Entity.objects.create(code='ENT-PERM', name='Entidad Perm', type='empresa')
        self.period = Period.objects.create(year=2026, month=9, period_type='mensual')

    def test_unauthenticated_user_gets_401(self):
        response = self.client.post(
            self.run_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_without_role_gets_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            self.run_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_execute_run_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            self.run_url,
            {'entity': self.entity.id, 'period': self.period.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
