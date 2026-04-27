from django.urls import path

from .views import (
    EntityClassificationCalculateContractAPIView,
    EntityClassificationContractDetailAPIView,
    EntityClassificationContractListAPIView,
    ReportContractDetailAPIView,
    ReportContractListAPIView,
    ReportStatsContractAPIView,
)

app_name = 'reports'

urlpatterns = [
    path('', ReportContractListAPIView.as_view(), name='reports-list'),
    path('<int:pk>/', ReportContractDetailAPIView.as_view(), name='reports-detail'),
    path('stats/', ReportStatsContractAPIView.as_view(), name='reports-stats'),
    path(
        'classifications/',
        EntityClassificationContractListAPIView.as_view(),
        name='classifications-list',
    ),
    path(
        'classifications/<int:pk>/',
        EntityClassificationContractDetailAPIView.as_view(),
        name='classifications-detail',
    ),
    path(
        'classifications/calculate/',
        EntityClassificationCalculateContractAPIView.as_view(),
        name='classifications-calculate',
    ),
]
