"""Ejemplo de patrón Controlador (backend - Django/DRF).

Este módulo muestra un Controller (ViewSet ligero) que orquesta la entrada HTTP,
delega en la capa de servicios y normaliza la salida.

En producción vive en: tesis/apps/<app>/views.py
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Sum, Avg, Count, Q
from django.shortcuts import get_object_or_404

from .models import Entity, Indicator, IndicatorRecord
from .serializers import EntitySerializer, IndicatorSerializer, IndicatorComputeSerializer
from .services import IndicatorExpert


class EntityViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Entity.objects.filter(is_active=True).order_by('name')
        serializer = EntitySerializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })

    def retrieve(self, request, pk=None):
        entity = get_object_or_404(Entity, pk=pk, is_active=True)
        serializer = EntitySerializer(entity)
        return Response(serializer.data)

    def create(self, request):
        serializer = EntitySerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        entity = serializer.save()
        return Response(
            EntitySerializer(entity).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        entity = get_object_or_404(Entity, pk=pk)
        serializer = EntitySerializer(entity, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        entity = serializer.save()
        return Response(EntitySerializer(entity).data)

    def destroy(self, request, pk=None):
        entity = get_object_or_404(Entity, pk=pk)
        entity.is_active = False
        entity.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IndicatorViewSet(viewsets.ViewSet):
    """Controller principal para indicadores económicos municipales."""

    def list(self, request):
        period = request.query_params.get("period")
        entity_id = request.query_params.get("entity")
        category = request.query_params.get("category")

        queryset = Indicator.objects.select_related('entity').filter(is_active=True)

        if period:
            queryset = queryset.filter(period=period)
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        if category:
            queryset = queryset.filter(category=category)

        serializer = IndicatorSerializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })

    def retrieve(self, request, pk=None):
        indicator = get_object_or_404(
            Indicator.objects.select_related('entity'),
            pk=pk,
            is_active=True
        )
        serializer = IndicatorSerializer(indicator)
        return Response(serializer.data)

    def create(self, request):
        serializer = IndicatorSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        indicator = serializer.save()
        return Response(
            IndicatorSerializer(indicator).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"])
    def compute(self, request):
        serializer = IndicatorComputeSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        validated = serializer.validated_data
        period = validated.get("period")
        category = validated.get("category")
        entity_id = validated.get("entity")

        queryset = Indicator.objects.filter(is_active=True, period=period)
        if category:
            queryset = queryset.filter(category=category)
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)

        expert = IndicatorExpert()
        rows = list(queryset.values('id', 'entity__name', 'value', 'category'))
        result = expert.compute_accumulated(rows)

        return Response({
            "period": period,
            "accumulated": result,
            "records_count": len(rows)
        })

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Resumen estadístico de indicadores por entidad."""
        entity_id = request.query_params.get("entity")
        period = request.query_params.get("period")

        filters = Q(is_active=True)
        if entity_id:
            filters &= Q(entity_id=entity_id)
        if period:
            filters &= Q(period=period)

        summary = (
            Indicator.objects
            .filter(filters)
            .values('entity__name', 'category')
            .annotate(
                total=Sum('value'),
                average=Avg('value'),
                count=Count('id')
            )
            .order_by('entity__name', 'category')
        )

        return Response({
            "period": period,
            "summary": list(summary)
        })

    @action(detail=True, methods=["post"])
    def link_records(self, request, pk=None):
        """Vincula indicadores a registros históricos."""
        indicator = get_object_or_404(Indicator, pk=pk, is_active=True)

        record_ids = request.data.get("record_ids", [])
        if not record_ids:
            raise ValidationError({"record_ids": "Required non-empty list"})

        linked_count = 0
        for record_id in record_ids:
            try:
                record = IndicatorRecord.objects.get(pk=record_id)
                record.indicator = indicator
                record.save()
                linked_count += 1
            except IndicatorRecord.DoesNotExist:
                continue

        return Response({
            "indicator_id": pk,
            "linked_records": linked_count
        })


if __name__ == "__main__":
    print("Controller ejemplo: paterns/controller.py")
