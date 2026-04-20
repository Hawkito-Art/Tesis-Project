from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IngestionPermission
from .serializers import (
    DocumentDetailSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
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
            return Response(
                {'detail': 'ImportJob no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            ImportJobSerializer(import_job, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk: int):
        from .models import ImportJob

        import_job = ImportJob.objects.select_related('document').filter(pk=pk).first()
        if not import_job:
            return Response(
                {'detail': 'ImportJob no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

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


class ImportJobDetailsContractAPIView(APIView):
    """Contrato inicial para errores/detalles por fila."""

    permission_classes = [IsAuthenticated, IngestionPermission]

    def get(self, request, pk: int):
        from .models import DocumentDetail, ImportJob

        import_job = ImportJob.objects.filter(pk=pk).first()
        if not import_job:
            return Response(
                {'detail': 'ImportJob no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        details_qs = DocumentDetail.objects.filter(import_job=import_job).order_by('row_number')

        paginator = PageNumberPagination()
        page_size = request.query_params.get('page_size')
        if page_size:
            try:
                paginator.page_size = max(1, min(int(page_size), 100))
            except (TypeError, ValueError):
                paginator.page_size = 20

        page = paginator.paginate_queryset(details_qs, request)
        serialized = DocumentDetailSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serialized.data)
