from django.core.management.base import BaseCommand

from apps.catalog.models import Entity


BASE_ENTITIES = [
    {
        "code": "CONSOLIDADO-MUN",
        "name": "Consolidado Municipal",
        "type": Entity.TYPE_CONSOLIDADO,
        "is_consolidated": True,
    },
    {
        "code": "EMP-AGROPECUARIA",
        "name": "Emp.Agropecuaria",
        "type": Entity.TYPE_EMPRESA,
        "is_consolidated": False,
    },
    {
        "code": "EMP-ALQUITEX",
        "name": "Empresa Alquitex",
        "type": Entity.TYPE_EMPRESA,
        "is_consolidated": False,
    },
    {
        "code": "EMP-COMERCIO",
        "name": "Empresa de Comercio",
        "type": Entity.TYPE_EMPRESA,
        "is_consolidated": False,
    },
    {
        "code": "MIPYME-ESTATAL",
        "name": "MIPYME ESTATAL",
        "type": Entity.TYPE_MIPYME,
        "is_consolidated": False,
    },
    {
        "code": "IAGROP",
        "name": "IaGROP",
        "type": Entity.TYPE_UNIDAD_PRESUPUESTADA,
        "is_consolidated": False,
    },
]


class Command(BaseCommand):
    help = "Carga o actualiza entidades base de catalogo de forma idempotente."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in BASE_ENTITIES:
            _, created = Entity.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "type": item["type"],
                    "is_consolidated": item["is_consolidated"],
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed catalog completado: {created_count} creadas, {updated_count} actualizadas."
            )
        )
