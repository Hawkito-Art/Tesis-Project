from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Entity, Period

User = get_user_model()


class EntityApiTestCase(APITestCase):
    def setUp(self):
        self.entities_url = "/api/entities/"
        self.admin_user = User.objects.create_user(
            email="admin-catalog@test.com", password="Passw0rd!123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email="regular-catalog@test.com", password="Passw0rd!123"
        )

    def test_entity_list_requires_authentication(self):
        response = self.client.get(self.entities_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_entity_list_allows_authenticated_read(self):
        Entity.objects.create(code="EMP-100", name="Entidad Test", type="empresa")
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(self.entities_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)

    def test_entity_create_requires_admin(self):
        payload = {"code": "EMP-200", "name": "Entidad 200", "type": "empresa"}
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.post(self.entities_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_entity_create_as_admin(self):
        payload = {
            "code": "CONSOL-01",
            "name": "Consolidado Municipal",
            "type": "consolidado",
            "is_consolidated": True,
        }
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.entities_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entity.objects.count(), 1)

    def test_entity_detail_patch_and_delete_for_admin(self):
        entity = Entity.objects.create(code="EMP-301", name="Entidad 301", type="empresa")
        self.client.force_authenticate(user=self.admin_user)

        patch_response = self.client.patch(
            f"/api/entities/{entity.id}/", {"name": "Entidad 301 Renombrada"}, format="json"
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(f"/api/entities/{entity.id}/", format="json")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Entity.objects.filter(id=entity.id).exists())

    def test_entity_filters_ordering_and_pagination(self):
        for index in range(25):
            Entity.objects.create(
                code=f"EMP-{index:03d}",
                name=f"Empresa {index:03d}",
                type="empresa" if index < 20 else "mipyme",
                is_consolidated=(index == 0),
            )

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(
            self.entities_url,
            {
                "type": "empresa",
                "ordering": "-code",
                "page": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 20)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertEqual(response.data["results"][0]["code"], "EMP-019")

    def test_entity_filters_by_code_and_is_consolidated(self):
        Entity.objects.create(
            code="CONS-001",
            name="Consolidado",
            type="consolidado",
            is_consolidated=True,
        )
        Entity.objects.create(
            code="EMP-500",
            name="Empresa 500",
            type="empresa",
            is_consolidated=False,
        )

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(
            self.entities_url,
            {"code": "CONS-001", "is_consolidated": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Consolidado")


class PeriodApiTestCase(APITestCase):
    def setUp(self):
        self.periods_url = "/api/periods/"
        self.admin_user = User.objects.create_user(
            email="admin-period@test.com", password="Passw0rd!123", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email="regular-period@test.com", password="Passw0rd!123"
        )

    def test_period_create_requires_admin(self):
        payload = {"year": 2026, "month": 5, "period_type": "mensual"}
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.post(self.periods_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_period_crud_partial_with_admin_and_duplicate_constraint(self):
        self.client.force_authenticate(user=self.admin_user)

        create_response = self.client.post(
            self.periods_url,
            {"year": 2026, "month": 6, "period_type": "mensual"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        period_id = create_response.data["id"]

        patch_response = self.client.patch(
            f"/api/periods/{period_id}/", {"month": 7}, format="json"
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        duplicate_response = self.client.post(
            self.periods_url,
            {"year": 2026, "month": 7, "period_type": "mensual"},
            format="json",
        )
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_period_list_filters_ordering_and_pagination(self):
        for month in range(1, 13):
            Period.objects.create(year=2026, month=month, period_type="mensual")
        Period.objects.create(year=2025, month=12, period_type="anual")

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(
            self.periods_url,
            {"year": 2026, "ordering": "-month"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(response.data["results"][0]["month"], 12)

    def test_period_filters_by_month(self):
        Period.objects.create(year=2026, month=2, period_type="mensual")
        Period.objects.create(year=2026, month=3, period_type="mensual")

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(
            self.periods_url,
            {"year": 2026, "month": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["month"], 2)
