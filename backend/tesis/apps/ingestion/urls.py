from django.urls import path

from .views import (
    DocumentUploadContractAPIView,
    ImportJobDetailContractAPIView,
    ImportJobDetailsContractAPIView,
    ImportJobListContractAPIView,
    ImportJobRetryContractAPIView,
)

app_name = 'ingestion'

urlpatterns = [
    path('documents/', DocumentUploadContractAPIView.as_view(), name='documents-upload'),
    path('import-jobs/', ImportJobListContractAPIView.as_view(), name='import-job-list'),
    path('import-jobs/<int:pk>/', ImportJobDetailContractAPIView.as_view(), name='import-job-detail'),
    path(
        'import-jobs/<int:pk>/details/',
        ImportJobDetailsContractAPIView.as_view(),
        name='import-job-details',
    ),
    path(
        'import-jobs/<int:pk>/retry/',
        ImportJobRetryContractAPIView.as_view(),
        name='import-job-retry',
    ),
]
