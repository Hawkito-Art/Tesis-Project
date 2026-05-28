from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.budget.models import Budget, BudgetItem
from apps.catalog.models import Entity, Period

User = get_user_model()

INGRESO_ITEMS = [
    {'code': 'ING-001', 'name': 'Ventas de bienes', 'planned': Decimal('85000.00'), 'actual': Decimal('78200.00')},
    {'code': 'ING-002', 'name': 'Ventas de servicios', 'planned': Decimal('32000.00'), 'actual': Decimal('29800.00')},
    {'code': 'ING-003', 'name': 'Subvenciones estatales', 'planned': Decimal('25000.00'), 'actual': Decimal('25000.00')},
    {'code': 'ING-004', 'name': 'Otros ingresos', 'planned': Decimal('12500.00'), 'actual': Decimal('9800.00')},
]

GASTO_ITEMS = [
    {'code': 'GAS-001', 'name': 'Salarios y prestaciones', 'planned': Decimal('45000.00'), 'actual': Decimal('43200.00')},
    {'code': 'GAS-002', 'name': 'Materias primas', 'planned': Decimal('28000.00'), 'actual': Decimal('26500.00')},
    {'code': 'GAS-003', 'name': 'Servicios contratados', 'planned': Decimal('15000.00'), 'actual': Decimal('14200.00')},
    {'code': 'GAS-004', 'name': 'Gastos de transporte', 'planned': Decimal('8500.00'), 'actual': Decimal('7900.00')},
    {'code': 'GAS-005', 'name': 'Servicios públicos', 'planned': Decimal('6200.00'), 'actual': Decimal('5800.00')},
    {'code': 'GAS-006', 'name': 'Gastos de oficina', 'planned': Decimal('3500.00'), 'actual': Decimal('3100.00')},
    {'code': 'GAS-007', 'name': 'Mantenimiento', 'planned': Decimal('4800.00'), 'actual': Decimal('4200.00')},
    {'code': 'GAS-008', 'name': 'Otros gastos', 'planned': Decimal('2500.00'), 'actual': Decimal('2100.00')},
]


class Command(BaseCommand):
    help = 'Carga datos demo de presupuestos y partidas para pruebas.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todos los presupuestos existentes antes de sembrar.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self._clear_data()

        self._seed_budgets()
        self.stdout.write(self.style.SUCCESS('Datos demo de presupuestos cargados correctamente.'))

    def _clear_data(self):
        deleted_items, _ = BudgetItem.objects.all().delete()
        deleted_budgets, _ = Budget.objects.all().delete()
        self.stdout.write(f'  Eliminados {deleted_budgets} presupuestos y {deleted_items} partidas.')

    def _seed_budgets(self):
        entities = Entity.objects.filter(is_active=True, is_consolidated=False).order_by('id')
        periods = Period.objects.filter(
            is_active=True, period_type='mensual', year=2026
        ).order_by('month')

        if not entities:
            self.stdout.write(self.style.WARNING('  No hay entidades activas no consolidadas. Ejecutá seed_catalog primero.'))
            return
        if not periods:
            self.stdout.write(self.style.WARNING('  No hay periodos mensuales para 2026. Ejecutá seed_demo_data primero.'))
            return

        user = User.objects.filter(is_staff=True).order_by('id').first()
        if not user:
            self.stdout.write(self.style.WARNING('  No hay usuarios staff. Se usará created_by=None.'))

        created_budgets = 0
        skipped_budgets = 0
        created_items = 0
        skipped_items = 0

        for entity in entities:
            for period in periods:
                month = period.month
                if month <= 2:
                    status = Budget.STATUS_CLOSED
                elif month <= 4:
                    status = Budget.STATUS_APPROVED
                else:
                    status = Budget.STATUS_DRAFT

                budget, was_created = Budget.objects.get_or_create(
                    entity=entity,
                    period=period,
                    defaults={
                        'status': status,
                        'description': f'Presupuesto {entity.name} - {period}',
                        'is_active': True,
                        'created_by': user,
                    },
                )

                if was_created:
                    created_budgets += 1
                    for item_data in INGRESO_ITEMS:
                        _, item_created = BudgetItem.objects.get_or_create(
                            budget=budget,
                            item_type='ingreso',
                            code=item_data['code'],
                            defaults={
                                'name': item_data['name'],
                                'planned_amount': item_data['planned'],
                                'actual_amount': item_data['actual'],
                                'is_active': True,
                            },
                        )
                        if item_created:
                            created_items += 1
                        else:
                            skipped_items += 1

                    for item_data in GASTO_ITEMS:
                        _, item_created = BudgetItem.objects.get_or_create(
                            budget=budget,
                            item_type='gasto',
                            code=item_data['code'],
                            defaults={
                                'name': item_data['name'],
                                'planned_amount': item_data['planned'],
                                'actual_amount': item_data['actual'],
                                'is_active': True,
                            },
                        )
                        if item_created:
                            created_items += 1
                        else:
                            skipped_items += 1
                else:
                    skipped_budgets += 1

        self.stdout.write(f'  Presupuestos: {created_budgets} creados, {skipped_budgets} ya existian.')
        self.stdout.write(f'  Partidas: {created_items} creadas, {skipped_items} ya existian.')
