from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EntityClassification, Report
from .permissions import ReportPermission
from .serializers import (
    EntityClassificationCalculateRequestSerializer,
    EntityClassificationListQuerySerializer,
    EntityClassificationSerializer,
    ReportGenerateRequestSerializer,
    ReportListQuerySerializer,
    ReportOutputSerializer,
    ReportSerializer,
    ReportStatsOutputSerializer,
    ReportStatsQuerySerializer,
)
from .services import build_report_payload, build_stats_payload, calculate_entity_classification


class ContractNotImplementedMixin:
    def not_implemented_response(self):
        return Response(
            {'detail': 'Not Implemented. Endpoint de contrato en fase R1.'},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class ReportContractListAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, ReportPermission]

    def get(self, request):
        query_serializer = ReportListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        queryset = Report.objects.select_related('entity', 'period', 'generated_by').order_by('-created_at')

        entity = params.get('entity')
        period = params.get('period')
        report_type = params.get('report_type')
        status_param = params.get('status')
        created_from = params.get('created_from')
        created_to = params.get('created_to')

        if entity:
            queryset = queryset.filter(entity=entity)
        if period:
            queryset = queryset.filter(period=period)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if created_from:
            queryset = queryset.filter(created_at__date__gte=created_from)
        if created_to:
            queryset = queryset.filter(created_at__date__lte=created_to)

        ordering = params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)

        paginator = PageNumberPagination()
        page_size = params.get('page_size')
        if page_size:
            paginator.page_size = page_size

        page = paginator.paginate_queryset(queryset, request)
        serialized = ReportSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serialized.data)

    def post(self, request):
        serializer = ReportGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = build_report_payload(
            entity=serializer.validated_data['entity'],
            period=serializer.validated_data['period'],
            report_type=serializer.validated_data['report_type'],
            include_stats=serializer.validated_data['include_stats'],
            include_classifications=serializer.validated_data['include_classifications'],
            filters=serializer.validated_data.get('filters', {}),
        )
        output_serializer = ReportOutputSerializer(data=payload)
        output_serializer.is_valid(raise_exception=True)

        report = Report.objects.create(
            entity=serializer.validated_data['entity'],
            period=serializer.validated_data['period'],
            report_type=serializer.validated_data['report_type'],
            status=Report.STATUS_GENERATED,
            summary=output_serializer.validated_data['summary'],
            detail=output_serializer.validated_data['detail'],
            metadata=output_serializer.validated_data['metadata'],
            generated_by=request.user,
        )

        return Response(
            ReportSerializer(report, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ReportContractDetailAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, ReportPermission]

    def get(self, request, pk: int):
        report = Report.objects.select_related('entity', 'period', 'generated_by').filter(pk=pk).first()
        if not report:
            return Response({'detail': 'Report no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            ReportSerializer(report, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class ReportStatsContractAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, ReportPermission]

    def get(self, request):
        query_serializer = ReportStatsQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        payload = build_stats_payload(
            entity=query_serializer.validated_data.get('entity'),
            period=query_serializer.validated_data.get('period'),
            indicator=query_serializer.validated_data.get('indicator'),
        )
        output_serializer = ReportStatsOutputSerializer(data=payload)
        output_serializer.is_valid(raise_exception=True)

        return Response(output_serializer.validated_data, status=status.HTTP_200_OK)


class EntityClassificationContractListAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, ReportPermission]

    def get(self, request):
        query_serializer = EntityClassificationListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        queryset = EntityClassification.objects.select_related('entity', 'period').order_by('-created_at')

        entity = params.get('entity')
        period = params.get('period')
        category = params.get('value')
        classification_type = params.get('classification_type')

        if entity:
            queryset = queryset.filter(entity=entity)
        if period:
            queryset = queryset.filter(period=period)
        if category:
            queryset = queryset.filter(value=category)
        if classification_type:
            queryset = queryset.filter(classification_type=classification_type)

        ordering = params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)

        paginator = PageNumberPagination()
        page_size = params.get('page_size')
        if page_size:
            paginator.page_size = page_size

        page = paginator.paginate_queryset(queryset, request)
        serialized = EntityClassificationSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serialized.data)


class EntityClassificationContractDetailAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, ReportPermission]

    def get(self, request, pk: int):
        classification = EntityClassification.objects.select_related('entity', 'period').filter(pk=pk).first()
        if not classification:
            return Response(
                {'detail': 'Clasificacion no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            EntityClassificationSerializer(classification, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class EntityClassificationCalculateContractAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, ReportPermission]

    def post(self, request):
        serializer = EntityClassificationCalculateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        classification = calculate_entity_classification(
            entity=serializer.validated_data['entity'],
            period=serializer.validated_data['period'],
            classification_type=serializer.validated_data['classification_type'],
        )

        return Response(
            EntityClassificationSerializer(classification, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
