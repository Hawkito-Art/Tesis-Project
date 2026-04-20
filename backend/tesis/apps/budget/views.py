from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import ValidationError

from .models import Budget, BudgetItem
from .permissions import BudgetWriteAdminReadAuthenticated
from .serializers import BudgetItemSerializer, BudgetSerializer
from .services import (
    ensure_budget_item_not_closed_for_mutation,
    ensure_budget_not_closed_for_mutation,
)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('entity', 'period', 'created_by').prefetch_related(
        'items'
    )
    serializer_class = BudgetSerializer
    permission_classes = [BudgetWriteAdminReadAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['entity', 'period', 'status', 'is_active']
    ordering_fields = ['id', 'created_at', 'updated_at']
    ordering = ['id']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        ensure_budget_not_closed_for_mutation(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        try:
            ensure_budget_not_closed_for_mutation(instance)
        except ValidationError as exc:
            raise ValidationError(exc.detail)
        instance.delete()


class BudgetItemViewSet(viewsets.ModelViewSet):
    queryset = BudgetItem.objects.select_related(
        'budget', 'budget__entity', 'budget__period'
    ).order_by('id')
    serializer_class = BudgetItemSerializer
    permission_classes = [BudgetWriteAdminReadAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['budget', 'item_type', 'code', 'is_active']
    ordering_fields = ['id', 'code', 'created_at', 'updated_at']
    ordering = ['id']

    def perform_create(self, serializer):
        budget = serializer.validated_data['budget']
        ensure_budget_not_closed_for_mutation(budget)
        serializer.save()

    def perform_update(self, serializer):
        budget = serializer.validated_data.get('budget', serializer.instance.budget)
        ensure_budget_not_closed_for_mutation(budget)
        serializer.save()

    def perform_destroy(self, instance):
        ensure_budget_item_not_closed_for_mutation(instance)
        instance.delete()
