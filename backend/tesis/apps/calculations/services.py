from decimal import Decimal, ROUND_HALF_UP
from unicodedata import normalize

from django.db import transaction
from django.utils import timezone

from .models import Calculation, CalculationResult
from apps.indicators.models import Indicator, IndicatorRecord

BASE_VARIABLES = ('plan_anual', 'ano_anterior', 'plan_acumulado', 'real_acumulado')
DERIVED_VARIABLES = ('porcentaje_r_p', 'real_aa', 'estimado_prox_mes')
CORRELATION_VARIABLES = ('plan_anual', 'ano_anterior', 'plan_acumulado', 'real_acumulado')
ZERO = Decimal('0')
FOUR_DECIMALS = Decimal('0.0001')


def run_formula_engine(*, entity, period) -> dict[int, dict[str, Decimal]]:
    """Calcula variables derivadas por indicador para una entidad/período."""
    records = IndicatorRecord.objects.filter(
        entity=entity,
        period=period,
        variable_name__in=BASE_VARIABLES,
    ).select_related('indicator')

    by_indicator: dict[int, dict[str, Decimal | None]] = {}
    indicator_objects: dict[int, Indicator] = {}
    for record in records:
        indicator_id = record.indicator_id
        indicator_objects[indicator_id] = record.indicator
        by_indicator.setdefault(indicator_id, {})[record.variable_name] = record.value

    computed: dict[int, dict[str, Decimal]] = {}
    for indicator_id, values in by_indicator.items():
        computed[indicator_id] = compute_standard_derived_values(
            plan_acumulado=values.get('plan_acumulado'),
            real_acumulado=values.get('real_acumulado'),
            ano_anterior=values.get('ano_anterior'),
        )

    _inject_correlation_values(by_indicator=by_indicator, indicator_objects=indicator_objects, computed=computed)
    return computed


def execute_manual_calculation(*, entity, period, user, name: str | None = None, description: str = '') -> Calculation:
    """Ejecuta cálculo manual y persiste resultados."""
    calculation_name = name or f'Calculo {entity.code} {period}'
    calculation = Calculation.objects.create(
        name=calculation_name,
        description=description,
        period=period,
        status='en_progreso',
        executed_by=user,
        started_at=timezone.now(),
    )

    try:
        computed = run_formula_engine(entity=entity, period=period)
        with transaction.atomic():
            results_to_create: list[CalculationResult] = []
            indicators = Indicator.objects.in_bulk(computed.keys())

            for indicator_id, variable_map in computed.items():
                indicator = indicators.get(indicator_id)
                if indicator is None:
                    continue

                for variable_name, value in variable_map.items():
                    results_to_create.append(
                        CalculationResult(
                            calculation=calculation,
                            entity=entity,
                            indicator=indicator,
                            variable_name=variable_name,
                            value=value,
                        )
                    )

            if results_to_create:
                CalculationResult.objects.bulk_create(results_to_create)

            calculation.status = 'completado'
            calculation.finished_at = timezone.now()
            calculation.save(update_fields=['status', 'finished_at'])
    except Exception:
        calculation.status = 'error'
        calculation.finished_at = timezone.now()
        calculation.save(update_fields=['status', 'finished_at'])
        raise

    return calculation


def compute_standard_derived_values(
    *,
    plan_acumulado: Decimal | None,
    real_acumulado: Decimal | None,
    ano_anterior: Decimal | None,
) -> dict[str, Decimal]:
    """Aplica fórmulas R/P, R/AA y estimado próximo mes."""
    safe_real = _to_decimal(real_acumulado)
    return {
        'porcentaje_r_p': _safe_division_percent(safe_real, plan_acumulado),
        'real_aa': _safe_division_percent(safe_real, ano_anterior),
        'estimado_prox_mes': _quantize(safe_real + (safe_real * Decimal('0.1'))),
    }


def _inject_correlation_values(*, by_indicator, indicator_objects, computed):
    salario_indicator_id = None
    productividad_indicator_id = None
    correlacion_indicator_id = None

    for indicator_id, indicator in indicator_objects.items():
        normalized_name = _normalize(indicator.name)
        if normalized_name == _normalize('Salario Medio'):
            salario_indicator_id = indicator_id
        elif normalized_name == _normalize('Productividad del Trabajo'):
            productividad_indicator_id = indicator_id
        elif normalized_name in {
            _normalize('Correlación Salario Medio/Product.'),
            _normalize('Correlacion Salario Medio/Product.'),
            _normalize('Correlación Salario Medio/Productividad del Trabajo'),
            _normalize('Correlacion Salario Medio/Productividad del Trabajo'),
        }:
            correlacion_indicator_id = indicator_id

    if not salario_indicator_id or not productividad_indicator_id or not correlacion_indicator_id:
        return

    salario_values = by_indicator.get(salario_indicator_id, {})
    productividad_values = by_indicator.get(productividad_indicator_id, {})

    correlation_values: dict[str, Decimal] = {}
    for variable_name in CORRELATION_VARIABLES:
        correlation_values[variable_name] = _safe_division(
            salario_values.get(variable_name),
            productividad_values.get(variable_name),
        )

    computed[correlacion_indicator_id] = correlation_values


def _safe_division_percent(numerator: Decimal | None, denominator: Decimal | None) -> Decimal:
    if denominator in (None, ZERO):
        return ZERO
    if numerator is None:
        return ZERO
    return _quantize((numerator / denominator) * Decimal('100'))


def _safe_division(numerator: Decimal | None, denominator: Decimal | None) -> Decimal:
    if denominator in (None, ZERO):
        return ZERO
    if numerator is None:
        return ZERO
    return _quantize(numerator / denominator)


def _to_decimal(value: Decimal | None) -> Decimal:
    return value if value is not None else ZERO


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(FOUR_DECIMALS, rounding=ROUND_HALF_UP)


def _normalize(value: str) -> str:
    normalized = normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    return ' '.join(normalized.lower().strip().split())
