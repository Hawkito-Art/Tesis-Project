from django.conf import settings
from django.db import models


class Budget(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_APPROVED = 'approved'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Borrador'),
        (STATUS_APPROVED, 'Aprobado'),
        (STATUS_CLOSED, 'Cerrado'),
    ]

    entity = models.ForeignKey(
        'catalog.Entity',
        on_delete=models.CASCADE,
        related_name='budgets',
    )
    period = models.ForeignKey(
        'catalog.Period',
        on_delete=models.CASCADE,
        related_name='budgets',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_budgets',
    )

    class Meta:
        verbose_name = 'presupuesto'
        verbose_name_plural = 'presupuestos'
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'period'],
                name='unique_budget_entity_period',
            ),
        ]

    def __str__(self):
        return f'Presupuesto {self.entity.code} - {self.period}'


class BudgetItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    budget = models.ForeignKey(
        'budget.Budget',
        on_delete=models.CASCADE,
        related_name='items',
    )
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    planned_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'partida presupuestaria'
        verbose_name_plural = 'partidas presupuestarias'
        constraints = [
            models.UniqueConstraint(
                fields=['budget', 'item_type', 'code'],
                name='unique_budget_item',
            ),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'
