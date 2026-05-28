from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Calculation
from .permissions import CalculationPermission
from .serializers import (
    CalculationExportXlsxSerializer,
    CalculationListSerializer,
    CalculationResultListQuerySerializer,
    CalculationResultSerializer,
    CalculationRunSerializer,
    CalculationSerializer,
)
from .services import build_export_workbook, execute_manual_calculation, render_workbook_to_bytes


class CalculationListContractAPIView(APIView):
    permission_classes = [IsAuthenticated, CalculationPermission]

    def get(self, request):
        queryset = Calculation.objects.select_related('period', 'executed_by')

        period = request.query_params.get('period')
        if period:
            queryset = queryset.filter(period_id=period)

        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        ordering = request.query_params.get('ordering')
        allowed_orderings = {
            'created_at', '-created_at', 'name', '-name',
            'status', '-status', 'started_at', '-started_at',
            'finished_at', '-finished_at',
        }
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')

        page = self.paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = CalculationListSerializer(page, many=True, context={'request': request})
            return self.paginator.get_paginated_response(serializer.data)

        serializer = CalculationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            from rest_framework.settings import api_settings
            pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
            self._paginator = pagination_class() if pagination_class else None
        return self._paginator


class CalculationRunContractAPIView(APIView):
    """Contrato inicial para ejecución manual de cálculos."""

    permission_classes = [IsAuthenticated, CalculationPermission]

    def post(self, request):
        serializer = CalculationRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calculation = execute_manual_calculation(
            entity=serializer.validated_data['entity'],
            period=serializer.validated_data['period'],
            user=request.user,
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description', ''),
        )

        return Response(
            CalculationSerializer(calculation, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class CalculationExportXlsxContractAPIView(APIView):
    permission_classes = [IsAuthenticated, CalculationPermission]

    def post(self, request):
        serializer = CalculationExportXlsxSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workbook = build_export_workbook(
            entity=serializer.validated_data.get('entity'),
            period=serializer.validated_data.get('period'),
        )
        content = render_workbook_to_bytes(workbook)
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            status=status.HTTP_200_OK,
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class CalculationContractDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, CalculationPermission]

    def get(self, request, pk: int):
        calculation = get_object_or_404(
            Calculation.objects.select_related(
                'period', 'executed_by'
            ).prefetch_related('results__entity', 'results__indicator'),
            pk=pk,
        )
        serializer = CalculationSerializer(calculation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CalculationResultContractListAPIView(APIView):
    permission_classes = [IsAuthenticated, CalculationPermission]

    def get(self, request, pk: int):
        calculation = get_object_or_404(
            Calculation.objects.select_related('period', 'executed_by'),
            pk=pk,
        )

        query_serializer = CalculationResultListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        queryset = calculation.results.select_related('entity', 'indicator').all()

        entity = params.get('entity')
        indicator = params.get('indicator')
        variable_name = params.get('variable_name')
        ordering = params.get('ordering', '-id')

        if entity:
            queryset = queryset.filter(entity=entity)
        if indicator:
            queryset = queryset.filter(indicator_id=indicator)
        if variable_name:
            queryset = queryset.filter(variable_name=variable_name)

        queryset = queryset.order_by(ordering)

        page = self.paginator.paginate_queryset(queryset, request, view=self)
        serializer = CalculationResultSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            from rest_framework.settings import api_settings

            pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
            self._paginator = pagination_class() if pagination_class else None
        return self._paginator
