from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, UserRole

User = get_user_model()


class AccountsDirectoryApiTestCase(APITestCase):
    def setUp(self):
        self.users_url = '/api/users/'
        self.roles_url = '/api/roles/'

        self.admin_user = User.objects.create_user(
            email='admin-directory@test.com',
            password='Passw0rd!123',
            is_staff=True,
            email_verified=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst-directory@test.com',
            password='Passw0rd!123',
            email_verified=True,
        )

        analyst_role, _ = Role.objects.get_or_create(name='analyst', defaults={'description': 'Analyst'})
        UserRole.objects.get_or_create(user=self.analyst_user, role=analyst_role)

    def test_users_list_requires_authentication(self):
        response = self.client.get(self.users_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_list_allows_authenticated_read(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(self.users_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_users_create_requires_admin(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.post(
            self.users_url,
            {
                'email': 'new-user@test.com',
                'password': 'Passw0rd!123',
                'first_name': 'New',
                'last_name': 'User',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_create_patch_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        create_response = self.client.post(
            self.users_url,
            {
                'email': 'created-user@test.com',
                'password': 'Passw0rd!123',
                'first_name': 'Created',
                'last_name': 'User',
                'email_verified': True,
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        user_id = create_response.data['id']
        detail_url = f'/api/users/{user_id}/'

        patch_response = self.client.patch(
            detail_url,
            {'first_name': 'Updated', 'is_active': False},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['first_name'], 'Updated')
        self.assertFalse(patch_response.data['is_active'])

        delete_response = self.client.delete(detail_url, format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_roles_list_requires_authentication(self):
        response = self.client.get(self.roles_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_roles_list_allows_authenticated_read(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.get(self.roles_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_roles_create_requires_admin(self):
        self.client.force_authenticate(user=self.analyst_user)
        response = self.client.post(
            self.roles_url,
            {'name': 'planner', 'description': 'Planner role'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_roles_create_patch_delete_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        create_response = self.client.post(
            self.roles_url,
            {'name': 'planner', 'description': 'Planner role'},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        role_id = create_response.data['id']
        detail_url = f'/api/roles/{role_id}/'

        patch_response = self.client.patch(
            detail_url,
            {'description': 'Planner role updated', 'is_active': False},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['description'], 'Planner role updated')
        self.assertFalse(patch_response.data['is_active'])

        delete_response = self.client.delete(detail_url, format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
