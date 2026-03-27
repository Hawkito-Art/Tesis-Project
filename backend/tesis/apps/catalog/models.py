from django.db import models


class Entity(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_consolidated = models.BooleanField(
        default=False,
        help_text='Indica si esta entidad es la agregada/consolidada del municipio',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'entidad'
        verbose_name_plural = 'entidades'

    def __str__(self):
        return f'{self.code} - {self.name}'


class Period(models.Model):
    PERIOD_TYPE_CHOICES = [
        ('mensual', 'Mensual'),
        ('acumulado', 'Acumulado'),
        ('anual', 'Anual'),
    ]

    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'periodo'
        verbose_name_plural = 'periodos'
        constraints = [
            models.UniqueConstraint(
                fields=['year', 'month', 'period_type'],
                name='unique_period',
            ),
        ]
        indexes = [
            models.Index(fields=['year', 'month'], name='idx_period_year_month'),
        ]

    def __str__(self):
        return f'{self.year}-{self.month:02d} ({self.period_type})'
