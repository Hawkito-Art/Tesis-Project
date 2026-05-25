from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Role, UserRole
from apps.catalog.models import Entity, Period

User = get_user_model()

SAMPLE_PERIODS = [
    {"year": 2024, "month": 1, "period_type": "mensual"},
    {"year": 2024, "month": 2, "period_type": "mensual"},
    {"year": 2024, "month": 3, "period_type": "mensual"},
    {"year": 2024, "month": 4, "period_type": "mensual"},
    {"year": 2024, "month": 5, "period_type": "mensual"},
    {"year": 2024, "month": 6, "period_type": "mensual"},
    {"year": 2024, "month": 1, "period_type": "acumulado"},
    {"year": 2024, "month": 6, "period_type": "acumulado"},
    {"year": 2024, "month": 1, "period_type": "anual"},
    {"year": 2025, "month": 1, "period_type": "mensual"},
    {"year": 2025, "month": 2, "period_type": "mensual"},
    {"year": 2025, "month": 3, "period_type": "mensual"},
    {"year": 2025, "month": 4, "period_type": "mensual"},
    {"year": 2025, "month": 5, "period_type": "mensual"},
    {"year": 2025, "month": 6, "period_type": "mensual"},
    {"year": 2025, "month": 7, "period_type": "mensual"},
    {"year": 2025, "month": 8, "period_type": "mensual"},
    {"year": 2025, "month": 9, "period_type": "mensual"},
    {"year": 2025, "month": 10, "period_type": "mensual"},
    {"year": 2025, "month": 11, "period_type": "mensual"},
    {"year": 2025, "month": 12, "period_type": "mensual"},
    {"year": 2025, "month": 1, "period_type": "acumulado"},
    {"year": 2025, "month": 6, "period_type": "acumulado"},
    {"year": 2025, "month": 12, "period_type": "acumulado"},
    {"year": 2025, "month": 1, "period_type": "anual"},
    {"year": 2026, "month": 1, "period_type": "mensual"},
    {"year": 2026, "month": 2, "period_type": "mensual"},
    {"year": 2026, "month": 3, "period_type": "mensual"},
    {"year": 2026, "month": 4, "period_type": "mensual"},
    {"year": 2026, "month": 5, "period_type": "mensual"},
]

ROLES = [
    {"name": "admin", "description": "Acceso completo al sistema"},
    {"name": "analyst", "description": "Puede visualizar y analizar datos"},
    {"name": "operator", "description": "Puede cargar datos y ejecutar procesos"},
]


class Command(BaseCommand):
    help = "Carga datos demo para el modulo de catalogo y directorio."

    def handle(self, *args, **options):
        self._seed_periods()
        self._seed_roles()
        self._seed_user_roles()
        self.stdout.write(self.style.SUCCESS("Datos demo cargados correctamente."))

    def _seed_periods(self):
        created = 0
        skipped = 0
        for item in SAMPLE_PERIODS:
            _, was_created = Period.objects.get_or_create(
                year=item["year"],
                month=item["month"],
                period_type=item["period_type"],
                defaults={"is_active": True},
            )
            if was_created:
                created += 1
            else:
                skipped += 1
        self.stdout.write(f"  Periodos: {created} creados, {skipped} ya existian.")

    def _seed_roles(self):
        created = 0
        skipped = 0
        for item in ROLES:
            _, was_created = Role.objects.get_or_create(
                name=item["name"],
                defaults={"description": item["description"], "is_active": True},
            )
            if was_created:
                created += 1
            else:
                skipped += 1
        self.stdout.write(f"  Roles: {created} creados, {skipped} ya existian.")

    def _seed_user_roles(self):
        try:
            admin_user = User.objects.get(email="arturomontesino@gmail.com")
        except User.DoesNotExist:
            self.stdout.write("  Usuario arturomontesino@gmail.com no encontrado, saltando asignacion de roles.")
            return

        assigned = 0
        admin_role = Role.objects.filter(name="admin").first()
        if admin_role and not UserRole.objects.filter(user=admin_user, role=admin_role).exists():
            UserRole.objects.create(user=admin_user, role=admin_role)
            assigned += 1

        self.stdout.write(f"  Roles de usuario: {assigned} asignados.")
