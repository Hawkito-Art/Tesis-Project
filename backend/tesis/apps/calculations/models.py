from django.conf import settings
from django.db import models


class Calculation(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    period = models.ForeignKey(
        'catalog.Period',
        on_delete=models.CASCADE,
        related_name='calculations',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executed_calculations',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'calculo'
        verbose_name_plural = 'calculos'

    def __str__(self):
        return f'{self.name} - {self.period}'


class CalculationResult(models.Model):
    calculation = models.ForeignKey(
        'calculations.Calculation',
        on_delete=models.CASCADE,
        related_name='results',
    )
    entity = models.ForeignKey(
        'catalog.Entity',
        on_delete=models.CASCADE,
        related_name='calculation_results',
    )
    indicator = models.ForeignKey(
        'indicators.Indicator',
        on_delete=models.CASCADE,
        related_name='calculation_results',
    )
    variable_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'resultado de calculo'
        verbose_name_plural = 'resultados de calculo'
        constraints = [
            models.UniqueConstraint(
                fields=['calculation', 'entity', 'indicator', 'variable_name'],
                name='unique_calculation_result',
            ),
        ]

    def __str__(self):
        return f'{self.calculation.name} - {self.entity.code} - {self.indicator.indicator}'
