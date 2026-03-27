from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.accounts.models import Role, UserRole
from tesis.permissions import (
    IsAdmin,
    IsAdminOrAnalyst,
    IsAdminOrOperator,
    IsAnalyst,
    IsOperator,
    get_user_roles,
    has_role,
)

User = get_user_model()


class RoleHelperTest(TestCase):

    def setUp(self):
        self.admin_role = Role.objects.create(name='admin')
        self.analyst_role = Role.objects.create(name='analyst')
        self.operator_role = Role.objects.create(name='operator')

    def test_get_user_roles_returns_empty_for_anonymous(self):
        from unittest.mock import MagicMock
        anon = MagicMock()
        anon.is_authenticated = False
        self.assertEqual(get_user_roles(anon), set())

    def test_get_user_roles_returns_assigned_roles(self):
        user = User.objects.create_user(email='test@test.com', password='pass1234')
        UserRole.objects.create(user=user, role=self.analyst_role)
        roles = get_user_roles(user)
        self.assertIn('analyst', roles)

    def test_has_role_returns_true_for_staff_admin(self):
        user = User.objects.create_user(
            email='staff@test.com', password='pass1234', is_staff=True,
        )
        self.assertTrue(has_role(user, 'admin'))

    def test_has_role_returns_true_for_assigned_role(self):
        user = User.objects.create_user(email='user@test.com', password='pass1234')
        UserRole.objects.create(user=user, role=self.operator_role)
        self.assertTrue(has_role(user, 'operator'))
        self.assertFalse(has_role(user, 'admin'))

    def test_has_role_multiple_roles(self):
        user = User.objects.create_user(email='multi@test.com', password='pass1234')
        UserRole.objects.create(user=user, role=self.analyst_role)
        self.assertTrue(has_role(user, 'admin', 'analyst'))


class PermissionClassTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_role = Role.objects.create(name='admin')
        self.analyst_role = Role.objects.create(name='analyst')
        self.operator_role = Role.objects.create(name='operator')

        self.admin_user = User.objects.create_user(
            email='admin@test.com', password='pass1234', is_staff=True,
        )
        self.analyst_user = User.objects.create_user(
            email='analyst@test.com', password='pass1234',
        )
        UserRole.objects.create(user=self.analyst_user, role=self.analyst_role)

        self.operator_user = User.objects.create_user(
            email='operator@test.com', password='pass1234',
        )
        UserRole.objects.create(user=self.operator_user, role=self.operator_role)

        self.regular_user = User.objects.create_user(
            email='regular@test.com', password='pass1234',
        )

    def _make_request(self, method, user):
        req = getattr(self.factory, method.lower())('/test/')
        req.user = user
        return req

    def test_is_admin_allows_staff(self):
        perm = IsAdmin()
        req = self._make_request('GET', self.admin_user)
        self.assertTrue(perm.has_permission(req, None))

    def test_is_admin_denies_analyst(self):
        perm = IsAdmin()
        req = self._make_request('GET', self.analyst_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_is_analyst_allows_analyst(self):
        perm = IsAnalyst()
        req = self._make_request('GET', self.analyst_user)
        self.assertTrue(perm.has_permission(req, None))

    def test_is_analyst_denies_operator(self):
        perm = IsAnalyst()
        req = self._make_request('GET', self.operator_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_is_admin_or_analyst_allows_both(self):
        perm = IsAdminOrAnalyst()
        for user in (self.admin_user, self.analyst_user):
            req = self._make_request('GET', user)
            self.assertTrue(perm.has_permission(req, None))

    def test_is_admin_or_analyst_denies_operator(self):
        perm = IsAdminOrAnalyst()
        req = self._make_request('GET', self.operator_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_is_admin_or_operator_allows_both(self):
        perm = IsAdminOrOperator()
        for user in (self.admin_user, self.operator_user):
            req = self._make_request('GET', user)
            self.assertTrue(perm.has_permission(req, None))

    def test_is_admin_or_operator_denies_analyst(self):
        perm = IsAdminOrOperator()
        req = self._make_request('GET', self.analyst_user)
        self.assertFalse(perm.has_permission(req, None))

    def test_all_permissions_deny_unauthenticated(self):
        from unittest.mock import MagicMock
        anon = MagicMock()
        anon.is_authenticated = False
        req = self._make_request('GET', anon)
        for perm_class in (IsAdmin, IsAnalyst, IsOperator, IsAdminOrAnalyst, IsAdminOrOperator):
            self.assertFalse(perm_class().has_permission(req, None))
