from django.db import models


class IndicatorGroup(models.Model):
    GROUP_TYPE_CHOICES = [
        ('fundamental', 'Fundamental'),
        ('limite', 'Limite'),
        ('otro', 'Otro'),
    ]

    name = models.CharField(max_length=255)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'grupo de indicador'
        verbose_name_plural = 'grupos de indicadores'
        ordering = ['order']

    def __str__(self):
        return self.name


class Indicator(models.Model):
    UNIT_CHOICES = [
        ('MP', 'MP'),
        ('U', 'U'),
        ('p', 'p'),
        ('peso', 'Peso'),
        ('Coef', 'Coeficiente'),
    ]

    indicator = models.CharField(
        max_length=50,
        help_text='Codigo unico del indicador',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    group = models.ForeignKey(
        'indicators.IndicatorGroup',
        on_delete=models.CASCADE,
        related_name='indicators',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'indicador'
        verbose_name_plural = 'indicadores'
        constraints = [
            models.UniqueConstraint(
                fields=['indicator', 'name'],
                name='unique_indicator_code_name',
            ),
        ]

    def __str__(self):
        return f'{self.indicator} - {self.name}'


class IndicatorVariable(models.Model):
    STANDARD_VARIABLES = [
        ('plan_anual', 'Plan Anual'),
        ('ano_anterior', 'Ano Anterior'),
        ('plan_acumulado', 'Plan Acumulado'),
        ('real_acumulado', 'Real Acumulado'),
        ('porcentaje_r_p', 'Porciento R/P'),
        ('real_aa', 'Real AA'),
        ('estimado_prox_mes', 'Estimado Proximo Mes'),
        ('estimado_cierre_ano', 'Estimado Cierre Ano'),
    ]

    indicator = models.ForeignKey(
        'indicators.Indicator',
        on_delete=models.CASCADE,
        related_name='variables',
    )
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'variable de indicador'
        verbose_name_plural = 'variables de indicador'
        constraints = [
            models.UniqueConstraint(
                fields=['indicator', 'name'],
                name='unique_indicator_variable',
            ),
        ]

    def __str__(self):
        return f'{self.indicator.indicator} - {self.label}'


class IndicatorRecord(models.Model):
    entity = models.ForeignKey(
        'catalog.Entity',
        on_delete=models.CASCADE,
        related_name='indicator_records',
    )
    indicator = models.ForeignKey(
        'indicators.Indicator',
        on_delete=models.CASCADE,
        related_name='records',
    )
    period = models.ForeignKey(
        'catalog.Period',
        on_delete=models.CASCADE,
        related_name='indicator_records',
    )
    variable_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'registro de indicador'
        verbose_name_plural = 'registros de indicadores'
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'indicator', 'period', 'variable_name'],
                name='unique_indicator_record',
            ),
        ]
        indexes = [
            models.Index(
                fields=['entity', 'indicator', 'period'],
                name='idx_indrec_entity_ind_per',
            ),
        ]

    def __str__(self):
        return f'{self.entity.code} - {self.indicator.indicator} - {self.period} - {self.variable_name}'
