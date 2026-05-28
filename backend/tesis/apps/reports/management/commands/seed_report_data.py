from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.calculations.models import CalculationResult
from apps.calculations.services import execute_manual_calculation
from apps.catalog.models import Entity, Period
from apps.indicators.models import IndicatorRecord

from ...models import Report, EntityClassification
from ...services import build_report_payload, calculate_entity_classification

User = get_user_model()


class Command(BaseCommand):
    help = 'Genera reportes demo, cálculos y clasificaciones a partir de datos existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Limpiar datos existentes.')

    def handle(self, *args, **options):
        if options['clear']:
            self._clear_data()

        self._run_calculations()
        self._seed_classifications()
        self._seed_reports()
        self.stdout.write(self.style.SUCCESS('Datos demo de reportes cargados correctamente.'))

    def _clear_data(self):
        from apps.calculations.models import Calculation
        deleted_calcs, _ = Calculation.objects.all().delete()
        dr, _ = Report.objects.all().delete()
        dc, _ = EntityClassification.objects.all().delete()
        self.stdout.write(f'  Eliminados {deleted_calcs} cálculos, {dr} reportes y {dc} clasificaciones.')

    def _has_calcs(self, entity_id, period_id):
        return CalculationResult.objects.filter(
            entity_id=entity_id, calculation__period_id=period_id
        ).exists()

    def _run_calculations(self):
        """Ejecuta cálculos para toda entidad/período con indicadores que aún no tenga cálculos."""
        user = User.objects.filter(is_staff=True).order_by('id').first()
        if not user:
            self.stdout.write(self.style.WARNING('  No hay usuario staff. Saltando cálculos.'))
            return

        pairs = (
            IndicatorRecord.objects
            .values('entity_id', 'period_id')
            .annotate(total=Count('id'))
            .filter(total__gt=0)
            .distinct()
        )

        ran = 0
        skipped = 0
        for pair in pairs:
            if self._has_calcs(pair['entity_id'], pair['period_id']):
                skipped += 1
                continue
            entity = Entity.objects.get(pk=pair['entity_id'])
            period = Period.objects.get(pk=pair['period_id'])
            try:
                execute_manual_calculation(
                    entity=entity,
                    period=period,
                    user=user,
                    name=f'Seed: {entity.code} {period}',
                    description='Cálculo generado por seed_report_data.',
                )
                ran += 1
            except Exception as e:
                self.stdout.write(f'  Error en cálculo {entity.code}/{period}: {e}')

        self.stdout.write(f'  Cálculos: {ran} ejecutados, {skipped} ya existían.')

    def _seed_classifications(self):
        """Crea clasificaciones para cada entidad/período con cálculos."""
        pairs = (
            CalculationResult.objects
            .values('entity_id', 'calculation__period_id')
            .annotate(total=Count('id'))
            .filter(total__gt=0)
            .distinct()
        )

        created = 0
        for pair in pairs:
            entity = Entity.objects.get(pk=pair['entity_id'])
            period = Period.objects.get(pk=pair['calculation__period_id'])
            try:
                calculate_entity_classification(entity=entity, period=period)
                created += 1
            except Exception as e:
                self.stdout.write(f'  Error clasificando {entity.code}/{period}: {e}')

        self.stdout.write(f'  Clasificaciones: {created}.')

    def _seed_reports(self):
        """Crea reportes para cada entidad/período con indicadores."""
        user = User.objects.filter(is_staff=True).order_by('id').first()
        pairs = (
            IndicatorRecord.objects
            .values('entity_id', 'period_id')
            .annotate(total=Count('id'))
            .filter(total__gt=0)
            .distinct()
        )

        created = 0
        skipped = 0
        for pair in pairs:
            entity = Entity.objects.get(pk=pair['entity_id'])
            period = Period.objects.get(pk=pair['period_id'])
            for rtype in ['operational', 'executive']:
                _, was_created = Report.objects.get_or_create(
                    entity=entity, period=period, report_type=rtype,
                    defaults={'status': Report.STATUS_GENERATED, 'generated_by': user},
                )
                if was_created:
                    payload = build_report_payload(
                        entity=entity, period=period, report_type=rtype,
                        include_stats=True, include_classifications=True, filters={},
                    )
                    Report.objects.filter(pk=_.pk).update(
                        summary=payload['summary'],
                        detail=payload['detail'],
                        metadata=payload['metadata'],
                    )
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(f'  Reportes: {created} creados, {skipped} ya existian.')
