from rest_framework import serializers

from .models import Budget, BudgetItem


def ensure_budget_not_closed_for_mutation(budget: Budget) -> None:
    """Evita operaciones de escritura sobre presupuestos cerrados."""
    if budget.status == Budget.STATUS_CLOSED:
        raise serializers.ValidationError(
            {'non_field_errors': ['No se permite modificar ni eliminar un presupuesto cerrado.']}
        )


def ensure_budget_item_not_closed_for_mutation(item: BudgetItem) -> None:
    """Evita operaciones de escritura sobre partidas de presupuestos cerrados."""
    if item.budget.status == Budget.STATUS_CLOSED:
        raise serializers.ValidationError(
            {
                'non_field_errors': [
                    'No se permite modificar ni eliminar partidas de un presupuesto cerrado.'
                ]
            }
        )
