from django.utils import timezone

from django.test import TestCase

from apps.catalog.models import Entity, Period
from apps.catalog.serializers import EntitySerializer, PeriodSerializer


class EntitySerializerTestCase(TestCase):
    def test_rejects_invalid_code_format(self):
        serializer = EntitySerializer(
            data={
                "code": "bad code",
                "name": "Empresa Demo",
                "type": "empresa",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_rejects_blank_name(self):
        serializer = EntitySerializer(
            data={
                "code": "EMP-DEMO",
                "name": "   ",
                "type": "empresa",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_rejects_duplicate_code_case_insensitive(self):
        Entity.objects.create(code="EMP-001", name="Empresa Uno", type="empresa")

        serializer = EntitySerializer(
            data={
                "code": "emp-001",
                "name": "Empresa Duplicada",
                "type": "empresa",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_accepts_valid_payload_and_normalizes_fields(self):
        serializer = EntitySerializer(
            data={
                "code": "  emp-002  ",
                "name": "  Empresa Dos  ",
                "type": "empresa",
                "description": " demo ",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        entity = serializer.save()
        self.assertEqual(entity.code, "EMP-002")
        self.assertEqual(entity.name, "Empresa Dos")


class PeriodSerializerTestCase(TestCase):
    def test_rejects_month_out_of_range(self):
        serializer = PeriodSerializer(
            data={"year": 2026, "month": 13, "period_type": "mensual"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("month", serializer.errors)

    def test_rejects_year_out_of_valid_range(self):
        serializer = PeriodSerializer(
            data={"year": 1800, "month": 10, "period_type": "mensual"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("year", serializer.errors)

    def test_rejects_duplicate_year_month_period_type(self):
        Period.objects.create(year=2026, month=3, period_type="mensual")

        serializer = PeriodSerializer(
            data={"year": 2026, "month": 3, "period_type": "mensual"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_accepts_valid_period_payload(self):
        current_year = timezone.now().year
        serializer = PeriodSerializer(
            data={"year": current_year, "month": 1, "period_type": "acumulado"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        period = serializer.save()
        self.assertEqual(period.year, current_year)
        self.assertEqual(period.month, 1)
