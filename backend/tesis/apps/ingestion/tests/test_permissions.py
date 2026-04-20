from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class IngestionPermissionMatrixTestCase(APITestCase):
    def setUp(self):
        self.upload_url = '/api/ingestion/documents/'
        self.job_detail_url = '/api/ingestion/import-jobs/1/'
        self.admin_user = User.objects.create_user(
            email='admin-ing-perm@test.com', password='Passw0rd!123', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email='regular-ing-perm@test.com', password='Passw0rd!123'
        )

    def test_unauthenticated_user_gets_401(self):
        response = self.client.get(self.job_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_without_role_gets_403(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.job_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_ingestion_endpoints(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.job_detail_url, format='json')
        # El recurso puede no existir, pero debe pasar autorización.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
