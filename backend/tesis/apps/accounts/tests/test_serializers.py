from django.test import TestCase

from apps.accounts.serializers import LoginSerializer, UserCreateSerializer
from apps.catalog.serializers import PeriodSerializer
from apps.budget.serializers import BudgetItemSerializer
from apps.indicators.serializers import IndicatorRecordSerializer
from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorGroup


class UserCreateSerializerTest(TestCase):

    def test_duplicate_email_rejected(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.create_user(email='dup@test.com', password='pass1234')

        data = {'email': 'dup@test.com', 'password': 'pass12345'}
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_valid_user_created(self):
        data = {'email': 'new@test.com', 'password': 'pass12345', 'first_name': 'Test'}
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class LoginSerializerTest(TestCase):

    def test_login_serializer_requires_email_and_password(self):
        serializer = LoginSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('password', serializer.errors)

    def test_login_serializer_accepts_valid_payload(self):
        serializer = LoginSerializer(
            data={'email': 'valid@test.com', 'password': 'Passw0rd!123'},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)


class PeriodSerializerTest(TestCase):

    def test_month_zero_rejected(self):
        data = {'year': 2025, 'month': 0, 'period_type': 'mensual'}
        serializer = PeriodSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('month', serializer.errors)

    def test_month_thirteen_rejected(self):
        data = {'year': 2025, 'month': 13, 'period_type': 'mensual'}
        serializer = PeriodSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('month', serializer.errors)

    def test_valid_month_accepted(self):
        data = {'year': 2025, 'month': 6, 'period_type': 'mensual'}
        serializer = PeriodSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class BudgetItemSerializerTest(TestCase):

    def test_negative_planned_amount_rejected(self):
        data = {
            'budget': 1, 'item_type': 'ingreso', 'code': 'A01',
            'name': 'Test', 'planned_amount': -100, 'actual_amount': 0,
        }
        serializer = BudgetItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('planned_amount', serializer.errors)

    def test_negative_actual_amount_rejected(self):
        data = {
            'budget': 1, 'item_type': 'ingreso', 'code': 'A01',
            'name': 'Test', 'planned_amount': 0, 'actual_amount': -50,
        }
        serializer = BudgetItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('actual_amount', serializer.errors)


class IndicatorRecordSerializerTest(TestCase):

    def setUp(self):
        self.group = IndicatorGroup.objects.create(
            name='Test Group', group_type='fundamental',
        )
        self.indicator = Indicator.objects.create(
            indicator='I001', name='Test Indicator',
            unit='MP', group=self.group,
        )
        from apps.indicators.models import IndicatorVariable
        self.variable = IndicatorVariable.objects.create(
            indicator=self.indicator, name='plan_anual', label='Plan Anual',
        )

    def test_invalid_variable_rejected(self):
        entity = Entity.objects.create(code='E001', name='Entity')
        period = Period.objects.create(year=2025, month=1, period_type='mensual')

        data = {
            'entity': entity.pk, 'indicator': self.indicator.pk,
            'period': period.pk, 'variable_name': 'no_existe',
            'value': 100,
        }
        serializer = IndicatorRecordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('variable_name', serializer.errors)

    def test_valid_variable_accepted(self):
        entity = Entity.objects.create(code='E002', name='Entity 2')
        period = Period.objects.create(year=2025, month=2, period_type='mensual')

        data = {
            'entity': entity.pk, 'indicator': self.indicator.pk,
            'period': period.pk, 'variable_name': 'plan_anual',
            'value': 100,
        }
        serializer = IndicatorRecordSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
