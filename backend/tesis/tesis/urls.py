from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def api_root(request):
    return Response({"message": "API de Tesis", "status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/catalog/", include("apps.catalog.urls")),
    path("api/budget/", include("apps.budget.urls")),
    path("api/indicators/", include("apps.indicators.urls")),
    path("api/ingestion/", include("apps.ingestion.urls")),
    path("api/calculations/", include("apps.calculations.urls")),
    path("api/reports/", include("apps.reports.urls")),
]
