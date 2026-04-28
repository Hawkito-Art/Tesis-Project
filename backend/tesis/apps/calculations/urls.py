from django.urls import path

from .views import (
    CalculationContractDetailAPIView,
    CalculationExportXlsxContractAPIView,
    CalculationResultContractListAPIView,
    CalculationRunContractAPIView,
)

app_name = 'calculations'

urlpatterns = [
    path('run/', CalculationRunContractAPIView.as_view(), name='calculations-run'),
    path('exports/xlsx/', CalculationExportXlsxContractAPIView.as_view(), name='calculations-export-xlsx'),
    path('<int:pk>/', CalculationContractDetailAPIView.as_view(), name='calculations-detail'),
    path('<int:pk>/results/', CalculationResultContractListAPIView.as_view(), name='calculations-results'),
]
