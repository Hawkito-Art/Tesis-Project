from django.test import TestCase

from apps.budget.models import Budget, BudgetItem
from apps.budget.serializers import BudgetItemSerializer, BudgetSerializer
from apps.catalog.models import Entity, Period


class BudgetSerializerTestCase(TestCase):
    def setUp(self):
        self.active_entity = Entity.objects.create(
            code="ENT-ACT",
            name="Entidad Activa",
            type="empresa",
            is_active=True,
        )
        self.inactive_entity = Entity.objects.create(
            code="ENT-INACT",
            name="Entidad Inactiva",
            type="empresa",
            is_active=False,
        )
        self.active_period = Period.objects.create(
            year=2026,
            month=3,
            period_type="mensual",
            is_active=True,
        )
        self.inactive_period = Period.objects.create(
            year=2026,
            month=4,
            period_type="mensual",
            is_active=False,
        )

    def test_rejects_inactive_entity(self):
        serializer = BudgetSerializer(
            data={
                "entity": self.inactive_entity.id,
                "period": self.active_period.id,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("entity", serializer.errors)

    def test_rejects_inactive_period(self):
        serializer = BudgetSerializer(
            data={
                "entity": self.active_entity.id,
                "period": self.inactive_period.id,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("period", serializer.errors)

    def test_rejects_closed_budget_updates(self):
        budget = Budget.objects.create(
            entity=self.active_entity,
            period=self.active_period,
            status=Budget.STATUS_CLOSED,
        )
        serializer = BudgetSerializer(
            budget,
            data={"description": "nuevo texto"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class BudgetItemSerializerTestCase(TestCase):
    def setUp(self):
        entity = Entity.objects.create(code="ENT-BUD", name="Entidad", type="empresa")
        period = Period.objects.create(year=2026, month=5, period_type="mensual")
        self.budget = Budget.objects.create(entity=entity, period=period)

    def test_rejects_negative_planned_amount(self):
        serializer = BudgetItemSerializer(
            data={
                "budget": self.budget.id,
                "item_type": "ingreso",
                "code": "I-NEG",
                "name": "Ingreso negativo",
                "planned_amount": "-1.00",
                "actual_amount": "0.00",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("planned_amount", serializer.errors)

    def test_rejects_missing_required_fields(self):
        serializer = BudgetItemSerializer(
            data={
                "budget": self.budget.id,
                "planned_amount": "10.00",
                "actual_amount": "5.00",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)
        self.assertIn("name", serializer.errors)
        self.assertIn("item_type", serializer.errors)

    def test_rejects_budget_item_create_when_budget_closed(self):
        self.budget.status = Budget.STATUS_CLOSED
        self.budget.save(update_fields=["status"])

        serializer = BudgetItemSerializer(
            data={
                "budget": self.budget.id,
                "item_type": "gasto",
                "code": "G-001",
                "name": "Gasto 1",
                "planned_amount": "10.00",
                "actual_amount": "0.00",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_rejects_budget_item_update_when_budget_closed(self):
        item = BudgetItem.objects.create(
            budget=self.budget,
            item_type="ingreso",
            code="I-001",
            name="Ingreso",
            planned_amount="10.00",
            actual_amount="5.00",
        )
        self.budget.status = Budget.STATUS_CLOSED
        self.budget.save(update_fields=["status"])

        serializer = BudgetItemSerializer(
            item,
            data={"name": "Ingreso actualizado"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
