from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.calculations.models import Calculation, CalculationResult
from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorRecord

User = get_user_model()

# 4 variables base requeridas por el motor de cálculo
BASE_VARS = ['plan_anual', 'ano_anterior', 'plan_acumulado', 'real_acumulado']

# Valores realistas por indicador para cada entidad
# Cada tupla: (indicator_code, plan_anual, ano_anterior, plan_acumulado, real_acumulado)
ENTITY_DATA = {
    'EMP-AGROPECUARIA': [
        ('VENTAS_TOT',       Decimal('145881.20'), Decimal('100209.30'), Decimal('75120.50'), Decimal('62180.30')),
        ('INGRESOS_TOT',     Decimal('158200.00'), Decimal('109800.00'), Decimal('82300.00'), Decimal('71200.00')),
        ('GASTOS_TOT',       Decimal('132400.00'), Decimal('95400.00'),  Decimal('71200.00'), Decimal('63400.00')),
        ('UTILIDAD',         Decimal('25800.00'),  Decimal('14400.00'),  Decimal('11100.00'), Decimal('7800.00')),
        ('GASTO_SALARIO_PESO_VAB', Decimal('0.72'), Decimal('0.78'),  Decimal('0.70'),   Decimal('0.68')),
        ('GASTO_TOTAL_PESO_ING',   Decimal('0.84'), Decimal('0.87'),  Decimal('0.87'),   Decimal('0.89')),
        ('VAB',              Decimal('98500.00'),  Decimal('79200.00'),  Decimal('52100.00'), Decimal('47500.00')),
        ('UTIL_ANTES_IMP_PESO_VAB', Decimal('0.18'), Decimal('0.14'),  Decimal('0.16'),   Decimal('0.13')),
        ('FONDO_SALARIO_TOT', Decimal('38200.00'), Decimal('34800.00'), Decimal('19800.00'), Decimal('18500.00')),
        ('PROM_TRAB',        Decimal('245.00'),    Decimal('238.00'),    Decimal('245.00'),  Decimal('242.00')),
        ('PROD_TRAB',        Decimal('402.00'),    Decimal('333.00'),    Decimal('213.00'),  Decimal('196.00')),
        ('SALARIO_MED',      Decimal('156.00'),    Decimal('146.00'),    Decimal('81.00'),   Decimal('76.00')),
        ('CORR_SM_PROD',     Decimal('0.00'),      Decimal('0.00'),      Decimal('0.00'),    Decimal('0.00')),
    ],
    'EMP-COMERCIO': [
        ('VENTAS_TOT',       Decimal('221500.00'), Decimal('185400.00'), Decimal('115400.00'), Decimal('100200.00')),
        ('INGRESOS_TOT',     Decimal('235000.00'), Decimal('196000.00'), Decimal('122500.00'), Decimal('108000.00')),
        ('GASTOS_TOT',       Decimal('198000.00'), Decimal('168000.00'), Decimal('105000.00'), Decimal('94000.00')),
        ('UTILIDAD',         Decimal('37000.00'),  Decimal('28000.00'),  Decimal('17500.00'),  Decimal('14000.00')),
        ('GASTO_SALARIO_PESO_VAB', Decimal('0.65'), Decimal('0.70'),  Decimal('0.63'),   Decimal('0.60')),
        ('GASTO_TOTAL_PESO_ING',   Decimal('0.84'), Decimal('0.86'),  Decimal('0.86'),   Decimal('0.87')),
        ('VAB',              Decimal('145000.00'), Decimal('120000.00'), Decimal('78000.00'), Decimal('68000.00')),
        ('UTIL_ANTES_IMP_PESO_VAB', Decimal('0.22'), Decimal('0.18'),  Decimal('0.19'),   Decimal('0.17')),
        ('FONDO_SALARIO_TOT', Decimal('52000.00'), Decimal('48500.00'), Decimal('27200.00'), Decimal('25800.00')),
        ('PROM_TRAB',        Decimal('320.00'),    Decimal('310.00'),    Decimal('320.00'),  Decimal('315.00')),
        ('PROD_TRAB',        Decimal('453.00'),    Decimal('387.00'),    Decimal('244.00'),  Decimal('216.00')),
        ('SALARIO_MED',      Decimal('163.00'),    Decimal('156.00'),    Decimal('85.00'),   Decimal('82.00')),
        ('CORR_SM_PROD',     Decimal('0.00'),      Decimal('0.00'),      Decimal('0.00'),    Decimal('0.00')),
    ],
    'MIPYME-ESTATAL': [
        ('VENTAS_TOT',       Decimal('89500.00'),  Decimal('68500.00'),  Decimal('46200.00'), Decimal('39800.00')),
        ('INGRESOS_TOT',     Decimal('96800.00'),  Decimal('74000.00'),  Decimal('50100.00'), Decimal('43500.00')),
        ('GASTOS_TOT',       Decimal('82300.00'),  Decimal('64800.00'),  Decimal('43500.00'), Decimal('39000.00')),
        ('UTILIDAD',         Decimal('14500.00'),  Decimal('9200.00'),   Decimal('6600.00'),  Decimal('4500.00')),
        ('GASTO_SALARIO_PESO_VAB', Decimal('0.78'), Decimal('0.82'),  Decimal('0.76'),   Decimal('0.74')),
        ('GASTO_TOTAL_PESO_ING',   Decimal('0.85'), Decimal('0.88'),  Decimal('0.87'),   Decimal('0.90')),
        ('VAB',              Decimal('58900.00'),  Decimal('45200.00'),  Decimal('30800.00'), Decimal('26800.00')),
        ('UTIL_ANTES_IMP_PESO_VAB', Decimal('0.15'), Decimal('0.12'),  Decimal('0.14'),   Decimal('0.11')),
        ('FONDO_SALARIO_TOT', Decimal('24800.00'), Decimal('22100.00'), Decimal('12800.00'), Decimal('11900.00')),
        ('PROM_TRAB',        Decimal('180.00'),    Decimal('175.00'),    Decimal('180.00'),  Decimal('178.00')),
        ('PROD_TRAB',        Decimal('327.00'),    Decimal('258.00'),    Decimal('171.00'),  Decimal('151.00')),
        ('SALARIO_MED',      Decimal('138.00'),    Decimal('126.00'),    Decimal('71.00'),   Decimal('67.00')),
        ('CORR_SM_PROD',     Decimal('0.00'),      Decimal('0.00'),      Decimal('0.00'),    Decimal('0.00')),
    ],
}

SAMPLE_CALCULATION_NAME = 'Demo: Cierre mensual {} {}'


class Command(BaseCommand):
    help = 'Carga datos demo de registros de indicadores y ejecuta cálculos de ejemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--calculate',
            action='store_true',
            help='Ejecutar cálculo automático después de sembrar los registros base.',
        )

    def handle(self, *args, **options):
        should_calculate = options['calculate']
        self._seed_indicator_records()

        if should_calculate:
            self._run_demo_calculations()

        self.stdout.write(self.style.SUCCESS('Datos demo de indicadores cargados correctamente.'))

    def _seed_indicator_records(self):
        indicators = {i.indicator: i for i in Indicator.objects.filter(is_active=True)}
        entities = {e.code: e for e in Entity.objects.filter(is_active=True, is_consolidated=False)}
        periods_qs = Period.objects.filter(is_active=True).order_by('-year', '-month')
        periods_dict = {(p.year, p.month): p for p in periods_qs if p.period_type == 'mensual'}

        created = 0
        updated = 0

        # Usar algunos períodos recientes para cada entidad
        target_periods = [(2025, 1), (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6),
                          (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
                          (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5)]

        for entity_code, indicator_values in ENTITY_DATA.items():
            entity = entities.get(entity_code)
            if not entity:
                self.stdout.write(f'  Entidad {entity_code} no encontrada, saltando.')
                continue

            for year, month in target_periods:
                period = periods_dict.get((year, month))
                if not period:
                    continue

                for indicator_code, plan_anual, ano_anterior, plan_acumulado, real_acumulado in indicator_values:
                    indicator = indicators.get(indicator_code)
                    if not indicator:
                        continue

                    values = {
                        'plan_anual': plan_anual,
                        'ano_anterior': ano_anterior,
                        'plan_acumulado': plan_acumulado,
                        'real_acumulado': real_acumulado,
                    }

                    for var_name, var_value in values.items():
                        _, was_created = IndicatorRecord.objects.update_or_create(
                            entity=entity,
                            indicator=indicator,
                            period=period,
                            variable_name=var_name,
                            defaults={
                                'value': var_value,
                                'source': IndicatorRecord.SOURCE_IMPORTED,
                            },
                        )
                        if was_created:
                            created += 1
                        else:
                            updated += 1

        self.stdout.write(f'  IndicatorRecords: {created} creados, {updated} actualizados.')

    def _run_demo_calculations(self):
        from apps.calculations.services import execute_manual_calculation

        entities = {e.code: e for e in Entity.objects.filter(is_active=True, is_consolidated=False)}
        periods_qs = Period.objects.filter(is_active=True).order_by('-year', '-month')

        demo_user = User.objects.filter(is_staff=True).order_by('id').first()
        if not demo_user:
            self.stdout.write('  No hay usuario staff para ejecutar cálculos, saltando.')
            return

        target_periods = [(2026, 4), (2026, 5)]
        periods_dict = {(p.year, p.month): p for p in periods_qs if p.period_type == 'mensual'}

        runs = 0
        for entity_code in ['EMP-AGROPECUARIA', 'EMP-COMERCIO', 'MIPYME-ESTATAL']:
            entity = entities.get(entity_code)
            if not entity:
                continue
            for year, month in target_periods:
                period = periods_dict.get((year, month))
                if not period:
                    continue

                calc_name = SAMPLE_CALCULATION_NAME.format(entity_code, f'{year}-{month:02d}')
                try:
                    execute_manual_calculation(
                        entity=entity,
                        period=period,
                        user=demo_user,
                        name=calc_name,
                        description='Cálculo de demostración generado por seed_indicator_data.',
                    )
                    runs += 1
                except Exception as e:
                    self.stdout.write(f'  Error ejecutando cálculo {calc_name}: {e}')

        self.stdout.write(f'  Cálculos ejecutados: {runs}.')
