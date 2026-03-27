from django.test import TestCase


class AppStructureTest(TestCase):
    """Verifica que la estructura base del proyecto esta correctamente configurada."""

    def test_settings_has_all_apps(self):
        from django.conf import settings

        required_apps = [
            'apps.accounts',
            'apps.catalog',
            'apps.budget',
            'apps.indicators',
            'apps.ingestion',
            'apps.calculations',
            'apps.reports',
        ]
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_jwt_configured(self):
        from django.conf import settings

        self.assertIn(
            'rest_framework_simplejwt.authentication.JWTAuthentication',
            settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'],
        )
