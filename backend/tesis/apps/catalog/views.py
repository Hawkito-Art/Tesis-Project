from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from .models import Entity, Period
from .permissions import CatalogPermission
from .serializers import EntitySerializer, PeriodSerializer


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all().order_by('id')
    serializer_class = EntitySerializer
    permission_classes = [CatalogPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'name', 'type', 'is_consolidated', 'is_active']
    search_fields = ['code', 'name']
    ordering_fields = ['id', 'code', 'name', 'type', 'created_at', 'updated_at']
    ordering = ['id']


class PeriodViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Period.objects.all().order_by('-year', '-month', 'period_type', '-id')
    serializer_class = PeriodSerializer
    permission_classes = [CatalogPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['year', 'month', 'period_type', 'is_active']
    ordering_fields = ['id', 'year', 'month', 'period_type', 'created_at']
    ordering = ['-year', '-month', 'period_type', '-id']
