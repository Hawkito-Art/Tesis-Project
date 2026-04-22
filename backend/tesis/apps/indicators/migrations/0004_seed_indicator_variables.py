from django.db import migrations


def seed_indicator_variables(apps, schema_editor):
    Indicator = apps.get_model('indicators', 'Indicator')
    IndicatorVariable = apps.get_model('indicators', 'IndicatorVariable')

    standard_variables = [
        ('plan_anual', 'Plan Anual'),
        ('ano_anterior', 'Ano Anterior'),
        ('plan_acumulado', 'Plan Acumulado'),
        ('real_acumulado', 'Real Acumulado'),
        ('porcentaje_r_p', 'Porciento R/P'),
        ('real_aa', 'Real AA'),
        ('estimado_prox_mes', 'Estimado Proximo Mes'),
        ('estimado_cierre_ano', 'Estimado Cierre Ano'),
    ]

    for indicator in Indicator.objects.filter(is_active=True):
        for variable_name, variable_label in standard_variables:
            IndicatorVariable.objects.update_or_create(
                indicator=indicator,
                name=variable_name,
                defaults={
                    'label': variable_label,
                    'is_active': True,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ('indicators', '0003_seed_indicators'),
    ]

    operations = [
        migrations.RunPython(seed_indicator_variables, migrations.RunPython.noop),
    ]
