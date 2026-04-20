from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.budget.models import Budget, BudgetItem
from apps.catalog.models import Entity, Period

User = get_user_model()


class BudgetApiTestCase(APITestCase):
    def setUp(self):
        self.budgets_url = "/api/budgets/"
        self.admin_user = User.objects.create_user(
            email="admin-budget@test.com", password="Passw0rd!123", is_staff=True
        )
        self.reader_user = User.objects.create_user(
            email="reader-budget@test.com", password="Passw0rd!123"
        )
        self.entity = Entity.objects.create(code="ENT-API", name="Entidad API", type="empresa")
        self.period = Period.objects.create(year=2026, month=6, period_type="mensual")

    def test_budget_endpoints_require_authentication(self):
        response = self.client.get(self.budgets_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_budget_list_allows_authenticated_user(self):
        Budget.objects.create(entity=self.entity, period=self.period)
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.get(self.budgets_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_budget_create_requires_admin(self):
        self.client.force_authenticate(user=self.reader_user)
        payload = {"entity": self.entity.id, "period": self.period.id}

        response = self.client.post(self.budgets_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_budget_create_with_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "entity": self.entity.id,
            "period": self.period.id,
            "description": "Presupuesto base",
        }

        response = self.client.post(self.budgets_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Budget.objects.count(), 1)

    def test_budget_partial_update_and_delete_with_admin(self):
        budget = Budget.objects.create(entity=self.entity, period=self.period)
        self.client.force_authenticate(user=self.admin_user)

        patch_response = self.client.patch(
            f"/api/budgets/{budget.id}/", {"description": "Ajustado"}, format="json"
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(f"/api/budgets/{budget.id}/", format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_budget_duplicate_entity_period_returns_400(self):
        Budget.objects.create(entity=self.entity, period=self.period)
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.budgets_url,
            {"entity": self.entity.id, "period": self.period.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_budget_delete_closed_returns_400(self):
        budget = Budget.objects.create(
            entity=self.entity,
            period=self.period,
            status=Budget.STATUS_CLOSED,
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(f"/api/budgets/{budget.id}/", format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_budget_filters_ordering_and_pagination(self):
        active_period = self.period
        other_period = Period.objects.create(year=2026, month=7, period_type="mensual")
        for index in range(25):
            entity = Entity.objects.create(
                code=f"ENT-F{index:03d}",
                name=f"Entidad F {index}",
                type="empresa",
                is_active=(index % 2 == 0),
            )
            Budget.objects.create(
                entity=entity,
                period=active_period if index < 20 else other_period,
                status=Budget.STATUS_DRAFT if index < 10 else Budget.STATUS_APPROVED,
                is_active=index != 1,
            )

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(
            self.budgets_url,
            {
                "period": active_period.id,
                "status": Budget.STATUS_APPROVED,
                "is_active": True,
                "ordering": "-id",
                "page": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 10)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertGreater(response.data["results"][0]["id"], response.data["results"][-1]["id"])


class BudgetItemApiTestCase(APITestCase):
    def setUp(self):
        self.items_url = "/api/budget-items/"
        self.admin_user = User.objects.create_user(
            email="admin-item@test.com", password="Passw0rd!123", is_staff=True
        )
        self.reader_user = User.objects.create_user(
            email="reader-item@test.com", password="Passw0rd!123"
        )
        self.entity = Entity.objects.create(code="ENT-ITM", name="Entidad", type="empresa")
        self.period = Period.objects.create(year=2026, month=8, period_type="mensual")
        self.budget = Budget.objects.create(entity=self.entity, period=self.period)

    def test_budget_item_create_requires_admin(self):
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.post(
            self.items_url,
            {
                "budget": self.budget.id,
                "item_type": "ingreso",
                "code": "I-100",
                "name": "Ingreso",
                "planned_amount": "10.00",
                "actual_amount": "0.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_budget_item_crud_with_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        create_response = self.client.post(
            self.items_url,
            {
                "budget": self.budget.id,
                "item_type": "ingreso",
                "code": "I-101",
                "name": "Ingreso 101",
                "planned_amount": "20.00",
                "actual_amount": "5.00",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        item_id = create_response.data["id"]

        patch_response = self.client.patch(
            f"/api/budget-items/{item_id}/",
            {"name": "Ingreso 101 Ajustado"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(f"/api/budget-items/{item_id}/", format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_budget_item_duplicate_returns_400(self):
        BudgetItem.objects.create(
            budget=self.budget,
            item_type="gasto",
            code="G-001",
            name="Gasto",
            planned_amount="10.00",
            actual_amount="0.00",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.items_url,
            {
                "budget": self.budget.id,
                "item_type": "gasto",
                "code": "G-001",
                "name": "Gasto duplicado",
                "planned_amount": "10.00",
                "actual_amount": "0.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_budget_item_list_filters_ordering_and_pagination(self):
        second_budget = Budget.objects.create(
            entity=Entity.objects.create(code="ENT-IT2", name="Entidad 2", type="empresa"),
            period=Period.objects.create(year=2026, month=9, period_type="mensual"),
        )
        for index in range(25):
            BudgetItem.objects.create(
                budget=self.budget if index < 20 else second_budget,
                item_type="ingreso" if index % 2 == 0 else "gasto",
                code=f"C-{index:03d}",
                name=f"Partida {index}",
                planned_amount="10.00",
                actual_amount="5.00",
                is_active=index != 2,
            )

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(
            self.items_url,
            {
                "budget": self.budget.id,
                "item_type": "ingreso",
                "is_active": True,
                "ordering": "-code",
                "page": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 9)
        self.assertEqual(len(response.data["results"]), 9)
        self.assertEqual(response.data["results"][0]["code"], "C-018")

    def test_closed_budget_blocks_item_update_and_delete(self):
        item = BudgetItem.objects.create(
            budget=self.budget,
            item_type="ingreso",
            code="I-CLOSE",
            name="Ingreso close",
            planned_amount="10.00",
            actual_amount="1.00",
        )
        self.budget.status = Budget.STATUS_CLOSED
        self.budget.save(update_fields=["status"])
        self.client.force_authenticate(user=self.admin_user)

        patch_response = self.client.patch(
            f"/api/budget-items/{item.id}/",
            {"name": "No permitido"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_400_BAD_REQUEST)

        delete_response = self.client.delete(f"/api/budget-items/{item.id}/", format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_400_BAD_REQUEST)
