from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from apps.catalog.models import Entity, Period


class EntityModelTestCase(TestCase):
    def test_code_must_be_unique(self):
        Entity.objects.create(code="ENT-001", name="Entidad Uno", type="empresa")

        with self.assertRaises(IntegrityError):
            Entity.objects.create(code="ENT-001", name="Entidad Duplicada", type="empresa")


class PeriodModelTestCase(TestCase):
    def test_unique_constraint_year_month_period_type(self):
        Period.objects.create(year=2026, month=4, period_type="mensual")

        with self.assertRaises(IntegrityError):
            Period.objects.create(year=2026, month=4, period_type="mensual")


class SeedCatalogCommandTestCase(TestCase):
    def test_seed_catalog_creates_six_base_entities_idempotently(self):
        call_command("seed_catalog")
        self.assertEqual(Entity.objects.count(), 6)

        call_command("seed_catalog")
        self.assertEqual(Entity.objects.count(), 6)

        consolidated = Entity.objects.get(type=Entity.TYPE_CONSOLIDADO)
        self.assertTrue(consolidated.is_consolidated)
