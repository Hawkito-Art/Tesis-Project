from django.urls import path

from .views import CalculationRunContractAPIView

app_name = 'calculations'

urlpatterns = [
    path('run/', CalculationRunContractAPIView.as_view(), name='calculations-run'),
]
