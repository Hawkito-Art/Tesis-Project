from django.db import migrations


def seed_indicators(apps, schema_editor):
    Indicator = apps.get_model('indicators', 'Indicator')
    IndicatorGroup = apps.get_model('indicators', 'IndicatorGroup')

    groups = {
        group.group_type: group
        for group in IndicatorGroup.objects.filter(
            group_type__in=['fundamental', 'limite', 'otro']
        )
    }

    seeds = [
        # Fundamentales
        {'indicator': 'VENTAS_TOT', 'name': 'Ventas Totales', 'unit': 'MP', 'group_type': 'fundamental'},
        {'indicator': 'INGRESOS_TOT', 'name': 'Total de Ingresos', 'unit': 'MP', 'group_type': 'fundamental'},
        {'indicator': 'GASTOS_TOT', 'name': 'Total de Gastos', 'unit': 'MP', 'group_type': 'fundamental'},
        {'indicator': 'UTILIDAD', 'name': 'Utilidad', 'unit': 'MP', 'group_type': 'fundamental'},
        # Limites
        {
            'indicator': 'GASTO_SALARIO_PESO_VAB',
            'name': 'Gasto de Salario x peso V.A.',
            'unit': 'peso',
            'group_type': 'limite',
        },
        # Otros
        {
            'indicator': 'GASTO_TOTAL_PESO_ING',
            'name': 'Gasto ToTal x peso de ing.Tot',
            'unit': 'peso',
            'group_type': 'otro',
        },
        {'indicator': 'VAB', 'name': 'Valor Agregado Bruto', 'unit': 'U', 'group_type': 'otro'},
        {
            'indicator': 'UTIL_ANTES_IMP_PESO_VAB',
            'name': 'Utilidad Antes  Imp. x $ de VAB',
            'unit': 'peso',
            'group_type': 'otro',
        },
        {
            'indicator': 'FONDO_SALARIO_TOT',
            'name': 'Fondo de Salario Total',
            'unit': 'MP',
            'group_type': 'otro',
        },
        {
            'indicator': 'PROM_TRAB',
            'name': 'Promedio de Trabajadores',
            'unit': 'U',
            'group_type': 'otro',
        },
        {
            'indicator': 'PROD_TRAB',
            'name': 'Productividad del Trabajo',
            'unit': 'p',
            'group_type': 'otro',
        },
        {'indicator': 'SALARIO_MED', 'name': 'Salario Medio', 'unit': 'p', 'group_type': 'otro'},
        {
            'indicator': 'CORR_SM_PROD',
            'name': 'Correlación Salario Medio/Product.',
            'unit': 'Coef',
            'group_type': 'otro',
        },
    ]

    for seed in seeds:
        group = groups.get(seed['group_type'])
        if group is None:
            continue

        existing = Indicator.objects.filter(indicator=seed['indicator']).order_by('id').first()
        if existing:
            existing.name = seed['name']
            existing.unit = seed['unit']
            existing.group = group
            existing.is_active = True
            existing.save(update_fields=['name', 'unit', 'group', 'is_active'])
            continue

        Indicator.objects.create(
            indicator=seed['indicator'],
            name=seed['name'],
            unit=seed['unit'],
            group=group,
            is_active=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('indicators', '0002_seed_indicator_groups'),
    ]

    operations = [
        migrations.RunPython(seed_indicators, migrations.RunPython.noop),
    ]
