from django.db import IntegrityError
from django.test import TestCase

from apps.budget.models import Budget, BudgetItem
from apps.catalog.models import Entity, Period


class BudgetModelTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(code="ENT-100", name="Entidad", type="empresa")
        self.period = Period.objects.create(year=2026, month=1, period_type="mensual")

    def test_unique_constraint_entity_period(self):
        Budget.objects.create(entity=self.entity, period=self.period)

        with self.assertRaises(IntegrityError):
            Budget.objects.create(entity=self.entity, period=self.period)

    def test_status_defaults_to_draft(self):
        budget = Budget.objects.create(entity=self.entity, period=self.period)

        self.assertEqual(budget.status, Budget.STATUS_DRAFT)


class BudgetItemModelTestCase(TestCase):
    def setUp(self):
        entity = Entity.objects.create(code="ENT-200", name="Entidad", type="empresa")
        period = Period.objects.create(year=2026, month=2, period_type="mensual")
        self.budget = Budget.objects.create(entity=entity, period=period)

    def test_unique_constraint_budget_item_type_code(self):
        BudgetItem.objects.create(
            budget=self.budget,
            item_type="ingreso",
            code="I-001",
            name="Ingreso 1",
        )

        with self.assertRaises(IntegrityError):
            BudgetItem.objects.create(
                budget=self.budget,
                item_type="ingreso",
                code="I-001",
                name="Ingreso duplicado",
            )
