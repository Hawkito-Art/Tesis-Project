from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IndicatorRecordFilter
from .models import Indicator, IndicatorGroup, IndicatorRecord, IndicatorVariable
from .permissions import IndicatorPermission, IndicatorRecordPermission
from .serializers import (
    IndicatorGroupSerializer,
    IndicatorRecordSerializer,
    IndicatorSerializer,
    IndicatorVariableSerializer,
)


class ContractNotImplementedMixin:
    def not_implemented_response(self):
        return Response(
            {'detail': 'Not Implemented. Endpoint de contrato en fase IND1.'},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class IndicatorGroupViewSet(viewsets.ModelViewSet):
    queryset = IndicatorGroup.objects.all().order_by('order', 'id')
    serializer_class = IndicatorGroupSerializer
    permission_classes = [IsAuthenticated, IndicatorPermission]


class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.select_related('group').prefetch_related('variables').order_by('id')
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticated, IndicatorPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['unit', 'group', 'is_active']
    search_fields = ['indicator', 'name']
    ordering_fields = ['id', 'indicator', 'name', 'created_at', 'updated_at']
    ordering = ['id']


class IndicatorVariableViewSet(viewsets.ModelViewSet):
    queryset = IndicatorVariable.objects.select_related('indicator', 'indicator__group').order_by(
        'indicator_id', 'name', 'id'
    )
    serializer_class = IndicatorVariableSerializer
    permission_classes = [IsAuthenticated, IndicatorPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['indicator', 'name', 'is_active']
    search_fields = ['name', 'label', 'indicator__indicator', 'indicator__name']
    ordering_fields = ['id', 'indicator', 'name']
    ordering = ['indicator', 'name', 'id']


class IndicatorRecordListAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = IndicatorRecord.objects.select_related(
        'entity',
        'indicator',
        'indicator__group',
        'period',
        'import_job',
        'calculation',
    ).order_by('-period__year', '-period__month', 'entity__code', 'indicator__indicator', 'variable_name')
    serializer_class = IndicatorRecordSerializer
    permission_classes = [IsAuthenticated, IndicatorRecordPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = IndicatorRecordFilter
    ordering_fields = [
        'id',
        'value',
        'variable_name',
        'period__year',
        'period__month',
        'entity__code',
        'indicator__indicator',
        'created_at',
        'updated_at',
    ]
    ordering = ['-period__year', '-period__month', 'entity__code', 'indicator__indicator', 'variable_name']
class IndicatorRecordContractListAPIView(ContractNotImplementedMixin, APIView):
    permission_classes = [IsAuthenticated, IndicatorRecordPermission]

    def get(self, request):
        return self.not_implemented_response()
