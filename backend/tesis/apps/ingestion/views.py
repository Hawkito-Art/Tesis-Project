from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IngestionPermission
from .serializers import (
    DocumentDetailSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
    ImportJobListSerializer,
    ImportJobProcessSerializer,
    ImportJobSerializer,
)
from .services import create_document_and_import_job
from .services import process_import_job_partial
from .services import upsert_indicator_records_from_import_job


class DocumentUploadContractAPIView(APIView):
    """Contrato inicial para carga de documentos de ingesta."""

    permission_classes = [IsAuthenticated, IngestionPermission]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document, import_job = create_document_and_import_job(
            validated_data=serializer.validated_data,
            uploaded_by=request.user,
        )

        return Response(
            {
                'document': DocumentSerializer(document, context={'request': request}).data,
                'import_job': ImportJobSerializer(import_job, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ImportJobDetailContractAPIView(APIView):
    """Contrato inicial para consulta de estado de importación."""

    permission_classes = [IsAuthenticated, IngestionPermission]

    def get(self, request, pk: int):
        from .models import ImportJob

        import_job = ImportJob.objects.select_related('document').filter(pk=pk).first()
        if not import_job:
            raise NotFound('ImportJob no encontrado.')

        return Response(
            ImportJobSerializer(import_job, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk: int):
        from .models import ImportJob

        import_job = ImportJob.objects.select_related('document').filter(pk=pk).first()
        if not import_job:
            raise NotFound('ImportJob no encontrado.')

        process_serializer = ImportJobProcessSerializer(data=request.data)
        process_serializer.is_valid(raise_exception=True)

        processed_job = process_import_job_partial(import_job=import_job)
        upsert_stats = upsert_indicator_records_from_import_job(
            import_job=processed_job,
            entity=process_serializer.validated_data['entity'],
            period=process_serializer.validated_data['period'],
        )
        return Response(
            {
                'import_job': ImportJobSerializer(processed_job, context={'request': request}).data,
                'upsert': upsert_stats,
            },
            status=status.HTTP_200_OK,
        )


class ImportJobListContractAPIView(APIView):
    permission_classes = [IsAuthenticated, IngestionPermission]

    def get(self, request):
        from .models import ImportJob

        queryset = ImportJob.objects.select_related('document').order_by('-created_at')

        page = self.paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ImportJobListSerializer(page, many=True, context={'request': request})
            return self.paginator.get_paginated_response(serializer.data)

        serializer = ImportJobListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            from rest_framework.settings import api_settings
            pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
            self._paginator = pagination_class() if pagination_class else None
        return self._paginator


class ImportJobRetryContractAPIView(APIView):
    permission_classes = [IsAuthenticated, IngestionPermission]

    def post(self, request, pk: int):
        from .models import DocumentDetail, ImportJob
        from apps.indicators.models import IndicatorRecord

        import_job = ImportJob.objects.select_related('document').filter(pk=pk).first()
        if not import_job:
            raise NotFound('ImportJob no encontrado.')

        IndicatorRecord.objects.filter(import_job=import_job).delete()
        DocumentDetail.objects.filter(import_job=import_job).delete()

        import_job.status = 'pendiente'
        import_job.total_rows = 0
        import_job.processed_rows = 0
        import_job.error_rows = 0
        import_job.error_log = ''
        import_job.started_at = None
        import_job.finished_at = None
        import_job.save(update_fields=[
            'status', 'total_rows', 'processed_rows', 'error_rows',
            'error_log', 'started_at', 'finished_at',
        ])

        import_job.document.status = 'pendiente'
        import_job.document.save(update_fields=['status'])

        return Response(
            ImportJobSerializer(import_job, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class ImportJobDetailsContractAPIView(APIView):
    """Contrato inicial para errores/detalles por fila."""

    permission_classes = [IsAuthenticated, IngestionPermission]

    def get(self, request, pk: int):
        from .models import DocumentDetail, ImportJob

        import_job = ImportJob.objects.filter(pk=pk).first()
        if not import_job:
            raise NotFound('ImportJob no encontrado.')

        details_qs = DocumentDetail.objects.filter(import_job=import_job).order_by('row_number')

        page = self.paginator.paginate_queryset(details_qs, request, view=self)
        serialized = DocumentDetailSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serialized.data)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            from rest_framework.settings import api_settings

            pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
            self._paginator = pagination_class() if pagination_class else None
        return self._paginator
