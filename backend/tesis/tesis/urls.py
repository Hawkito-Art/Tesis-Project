from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.accounts.views import RoleViewSet, UserViewSet
from apps.calculations.views import CalculationExportXlsxContractAPIView
from apps.catalog.views import EntityViewSet, PeriodViewSet
from apps.reports.views import (
    EntityClassificationCalculateContractAPIView,
    EntityClassificationContractDetailAPIView,
    EntityClassificationContractListAPIView,
    ReportStatsContractAPIView,
)


@api_view()
def api_root(request):
    return Response({"message": "API de Tesis", "status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/auth/", include("apps.accounts.urls")),
    path(
        "api/users/",
        UserViewSet.as_view({"get": "list", "post": "create"}),
        name="users-list",
    ),
    path(
        "api/users/<int:pk>/",
        UserViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="users-detail",
    ),
    path(
        "api/roles/",
        RoleViewSet.as_view({"get": "list", "post": "create"}),
        name="roles-list",
    ),
    path(
        "api/roles/<int:pk>/",
        RoleViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="roles-detail",
    ),
    path("api/catalog/", include("apps.catalog.urls")),
    path(
        "api/entities/",
        EntityViewSet.as_view({"get": "list", "post": "create"}),
        name="entities-list",
    ),
    path(
        "api/entities/<int:pk>/",
        EntityViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="entities-detail",
    ),
    path(
        "api/periods/",
        PeriodViewSet.as_view({"get": "list", "post": "create"}),
        name="periods-list",
    ),
    path(
        "api/periods/<int:pk>/",
        PeriodViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="periods-detail",
    ),
    path("api/", include("apps.budget.urls")),
    path("api/indicators/", include("apps.indicators.urls")),
    path("api/ingestion/", include("apps.ingestion.urls")),
    path("api/calculations/", include("apps.calculations.urls")),
    path("api/exports/xlsx/", CalculationExportXlsxContractAPIView.as_view(), name="exports-xlsx"),
    path("api/stats/", ReportStatsContractAPIView.as_view(), name="stats"),
    path("api/reports/stats/", ReportStatsContractAPIView.as_view(), name="reports-stats-legacy"),
    path(
        "api/classifications/calculate/",
        EntityClassificationCalculateContractAPIView.as_view(),
        name="classifications-calculate",
    ),
    path(
        "api/classifications/",
        EntityClassificationContractListAPIView.as_view(),
        name="classifications-list",
    ),
    path(
        "api/classifications/<int:pk>/",
        EntityClassificationContractDetailAPIView.as_view(),
        name="classifications-detail",
    ),
    path(
        "api/reports/classifications/calculate/",
        EntityClassificationCalculateContractAPIView.as_view(),
        name="reports-classifications-calculate-legacy",
    ),
    path(
        "api/reports/classifications/",
        EntityClassificationContractListAPIView.as_view(),
        name="reports-classifications-list-legacy",
    ),
    path(
        "api/reports/classifications/<int:pk>/",
        EntityClassificationContractDetailAPIView.as_view(),
        name="reports-classifications-detail-legacy",
    ),
    path("api/reports/", include("apps.reports.urls")),
]
