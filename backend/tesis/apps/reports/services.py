from collections import defaultdict
from decimal import Decimal

from django.utils import timezone

from apps.calculations.models import CalculationResult
from apps.indicators.models import IndicatorRecord

from .models import EntityClassification


def build_report_payload(*, entity, period, report_type: str, include_stats: bool, include_classifications: bool, filters: dict):
    records_qs = IndicatorRecord.objects.select_related('indicator', 'indicator__group').filter(
        entity=entity,
        period=period,
    )

    indicator_filter = filters.get('indicator')
    group_filter = filters.get('group')
    source_filter = filters.get('source')

    if indicator_filter:
        records_qs = records_qs.filter(indicator_id=indicator_filter)
    if group_filter:
        records_qs = records_qs.filter(indicator__group_id=group_filter)
    if source_filter:
        records_qs = records_qs.filter(source=source_filter)

    records = list(records_qs.order_by('indicator__indicator', 'variable_name'))

    source_counts = defaultdict(int)
    by_indicator = defaultdict(dict)
    for record in records:
        source_counts[record.source] += 1
        by_indicator[record.indicator.indicator][record.variable_name] = (
            str(record.value) if record.value is not None else None
        )

    calc_results_qs = CalculationResult.objects.select_related('calculation').filter(
        entity=entity,
        calculation__period=period,
    )
    latest_calc = calc_results_qs.order_by('-calculation__created_at').first()

    summary = {
        'total_records': len(records),
        'records_with_value': sum(1 for r in records if r.value is not None),
        'records_by_source': dict(source_counts),
        'total_calculation_results': calc_results_qs.count(),
        'latest_calculation_id': latest_calc.calculation_id if latest_calc else None,
    }

    detail = {
        'indicators': by_indicator,
    }

    metadata = {
        'entity_id': entity.id,
        'entity_code': entity.code,
        'period_id': period.id,
        'period_display': str(period),
        'report_type': report_type,
        'filters_applied': filters,
        'generated_at': timezone.now().isoformat(),
        'source_modules': ['indicators', 'calculations'],
    }

    if include_stats:
        detail['stats'] = {
            'distinct_indicators': len(by_indicator.keys()),
            'distinct_variables': len({r.variable_name for r in records}),
        }

    if include_classifications:
        classifications = list(
            EntityClassification.objects.filter(entity=entity, period=period)
            .order_by('classification_type', '-updated_at')
            .values(
                'id',
                'classification_type',
                'value',
                'description',
                'rule_version',
                'criteria_snapshot',
                'updated_at',
            )
        )

        for row in classifications:
            row['updated_at'] = row['updated_at'].isoformat() if row['updated_at'] else None

        detail['classifications'] = {
            'included': True,
            'count': len(classifications),
            'items': classifications,
            'status': 'available' if classifications else 'empty',
        }

        if not classifications:
            metadata['warnings'] = metadata.get('warnings', [])
            metadata['warnings'].append(
                'No existen clasificaciones persistidas para la entidad/periodo solicitado.'
            )

    return {
        'summary': summary,
        'detail': detail,
        'metadata': metadata,
    }


def build_stats_payload(*, entity=None, period=None, indicator=None):
    records_qs = IndicatorRecord.objects.select_related('indicator', 'period', 'entity')
    calc_results_qs = CalculationResult.objects.select_related('indicator', 'calculation', 'entity')

    if entity:
        records_qs = records_qs.filter(entity=entity)
        calc_results_qs = calc_results_qs.filter(entity=entity)
    if period:
        records_qs = records_qs.filter(period=period)
        calc_results_qs = calc_results_qs.filter(calculation__period=period)
    if indicator:
        records_qs = records_qs.filter(indicator=indicator)
        calc_results_qs = calc_results_qs.filter(indicator=indicator)

    records = list(records_qs)
    calc_results = list(calc_results_qs)

    records_by_indicator = defaultdict(int)
    values_by_indicator = defaultdict(list)
    records_by_source = defaultdict(int)
    for rec in records:
        records_by_indicator[rec.indicator.indicator] += 1
        records_by_source[rec.source] += 1
        if rec.value is not None:
            values_by_indicator[rec.indicator.indicator].append(float(rec.value))

    average_by_indicator = {
        code: round(sum(values) / len(values), 4)
        for code, values in values_by_indicator.items()
        if values
    }

    latest_calc = None
    if calc_results:
        latest_calc = max(calc_results, key=lambda item: item.calculation.created_at)

    return {
        'filters_applied': {
            'entity': entity.id if entity else None,
            'period': period.id if period else None,
            'indicator': indicator.id if indicator else None,
        },
        'totals': {
            'indicator_records': len(records),
            'calculation_results': len(calc_results),
            'distinct_indicators': len(set(rec.indicator_id for rec in records)),
            'distinct_entities': len(set(rec.entity_id for rec in records)),
        },
        'records_by_source': dict(records_by_source),
        'records_by_indicator': dict(records_by_indicator),
        'average_value_by_indicator': average_by_indicator,
        'latest_calculation': {
            'id': latest_calc.calculation_id if latest_calc else None,
            'created_at': latest_calc.calculation.created_at.isoformat() if latest_calc else None,
        },
    }


def calculate_entity_classification(*, entity, period, classification_type: str = 'overall_performance'):
    values_qs = CalculationResult.objects.filter(
        entity=entity,
        calculation__period=period,
        value__isnull=False,
    ).values_list('value', flat=True)

    values = [Decimal(value) for value in values_qs]
    total_results = len(values)

    if total_results == 0:
        classification_value = 'sin_datos'
        description = 'No existen resultados de calculo para clasificar la entidad en el periodo.'
        average_value = None
    else:
        average_value = sum(values) / Decimal(total_results)
        if average_value >= Decimal('85'):
            classification_value = 'alto_desempeno'
            description = 'Desempeno alto segun promedio de resultados de calculo.'
        elif average_value >= Decimal('60'):
            classification_value = 'desempeno_medio'
            description = 'Desempeno medio segun promedio de resultados de calculo.'
        else:
            classification_value = 'desempeno_bajo'
            description = 'Desempeno bajo segun promedio de resultados de calculo.'

    criteria_snapshot = {
        'input': {
            'calculation_results_count': total_results,
            'average_value': float(round(average_value, 4)) if average_value is not None else None,
        },
        'rules': {
            'high_threshold': 85,
            'medium_threshold': 60,
        },
        'engine': {
            'classification_type': classification_type,
            'rule_version': EntityClassification.RULE_VERSION_INITIAL,
        },
    }

    classification, _ = EntityClassification.objects.update_or_create(
        entity=entity,
        period=period,
        classification_type=classification_type,
        defaults={
            'value': classification_value,
            'description': description,
            'rule_version': EntityClassification.RULE_VERSION_INITIAL,
            'criteria_snapshot': criteria_snapshot,
        },
    )

    return classification
