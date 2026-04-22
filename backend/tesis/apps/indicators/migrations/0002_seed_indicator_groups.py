from django.db import migrations


def seed_indicator_groups(apps, schema_editor):
    IndicatorGroup = apps.get_model('indicators', 'IndicatorGroup')

    seeds = [
        {
            'group_type': 'fundamental',
            'name': 'Indicadores Fundamentales',
            'order': 1,
        },
        {
            'group_type': 'limite',
            'name': 'Indicadores Limites',
            'order': 2,
        },
        {
            'group_type': 'otro',
            'name': 'Otros Indicadores',
            'order': 3,
        },
    ]

    for seed in seeds:
        existing = IndicatorGroup.objects.filter(group_type=seed['group_type']).order_by('id').first()
        if existing:
            existing.name = seed['name']
            existing.order = seed['order']
            existing.is_active = True
            existing.save(update_fields=['name', 'order', 'is_active'])
            continue

        IndicatorGroup.objects.create(
            name=seed['name'],
            group_type=seed['group_type'],
            order=seed['order'],
            is_active=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('indicators', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_indicator_groups, migrations.RunPython.noop),
    ]
