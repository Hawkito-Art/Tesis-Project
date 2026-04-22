from django.apps import apps as django_apps
from django.test import TestCase


class IndicatorGroupSeedMigrationTestCase(TestCase):
    def test_seed_groups_exist_with_expected_order(self):
        IndicatorGroup = django_apps.get_model('indicators', 'IndicatorGroup')

        by_type = {
            row.group_type: row
            for row in IndicatorGroup.objects.filter(
                group_type__in=['fundamental', 'limite', 'otro']
            )
        }

        self.assertEqual(len(by_type), 3)
        self.assertEqual(by_type['fundamental'].name, 'Indicadores Fundamentales')
        self.assertEqual(by_type['fundamental'].order, 1)
        self.assertEqual(by_type['limite'].name, 'Indicadores Limites')
        self.assertEqual(by_type['limite'].order, 2)
        self.assertEqual(by_type['otro'].name, 'Otros Indicadores')
        self.assertEqual(by_type['otro'].order, 3)


class IndicatorSeedMigrationTestCase(TestCase):
    def test_seed_indicators_exist_with_expected_groups_and_units(self):
        Indicator = django_apps.get_model('indicators', 'Indicator')

        indicators = list(Indicator.objects.filter(is_active=True))
        self.assertEqual(len(indicators), 13)

        by_code = {row.indicator: row for row in indicators}
        self.assertEqual(by_code['VENTAS_TOT'].group.group_type, 'fundamental')
        self.assertEqual(by_code['VENTAS_TOT'].unit, 'MP')
        self.assertEqual(by_code['GASTO_SALARIO_PESO_VAB'].group.group_type, 'limite')
        self.assertEqual(by_code['GASTO_SALARIO_PESO_VAB'].unit, 'peso')
        self.assertEqual(by_code['CORR_SM_PROD'].group.group_type, 'otro')
        self.assertEqual(by_code['CORR_SM_PROD'].unit, 'Coef')


class IndicatorVariableSeedMigrationTestCase(TestCase):
    def test_each_indicator_has_eight_standard_variables(self):
        Indicator = django_apps.get_model('indicators', 'Indicator')
        IndicatorVariable = django_apps.get_model('indicators', 'IndicatorVariable')

        expected_names = {
            'plan_anual',
            'ano_anterior',
            'plan_acumulado',
            'real_acumulado',
            'porcentaje_r_p',
            'real_aa',
            'estimado_prox_mes',
            'estimado_cierre_ano',
        }

        indicators = Indicator.objects.filter(is_active=True)
        self.assertEqual(indicators.count(), 13)

        for indicator in indicators:
            variables = IndicatorVariable.objects.filter(indicator=indicator, is_active=True)
            self.assertEqual(variables.count(), 8)
            self.assertSetEqual({row.name for row in variables}, expected_names)
