from django.conf import settings
from django.db import models


class Report(models.Model):
    REPORT_TYPE_OPERATIONAL = 'operational'
    REPORT_TYPE_EXECUTIVE = 'executive'
    REPORT_TYPE_CHOICES = [
        (REPORT_TYPE_OPERATIONAL, 'Operacional'),
        (REPORT_TYPE_EXECUTIVE, 'Ejecutivo'),
    ]

    STATUS_GENERATED = 'generated'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = [
        (STATUS_GENERATED, 'Generado'),
        (STATUS_ERROR, 'Error'),
    ]

    entity = models.ForeignKey(
        'catalog.Entity',
        on_delete=models.CASCADE,
        related_name='reports',
    )
    period = models.ForeignKey(
        'catalog.Period',
        on_delete=models.CASCADE,
        related_name='reports',
    )
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES, default=REPORT_TYPE_OPERATIONAL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_GENERATED)
    summary = models.JSONField(default=dict, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'reporte'
        verbose_name_plural = 'reportes'
        indexes = [
            models.Index(fields=['entity', 'period'], name='idx_reports_entity_period'),
            models.Index(fields=['report_type', 'status'], name='idx_reports_type_status'),
            models.Index(fields=['-created_at'], name='idx_reports_created_desc'),
        ]

    def __str__(self):
        return f'Reporte {self.entity.code} - {self.period} - {self.report_type}'


class EntityClassification(models.Model):
    RULE_VERSION_INITIAL = 'r7-v1'

    entity = models.ForeignKey(
        'catalog.Entity',
        on_delete=models.CASCADE,
        related_name='classifications',
    )
    period = models.ForeignKey(
        'catalog.Period',
        on_delete=models.CASCADE,
        related_name='entity_classifications',
    )
    classification_type = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rule_version = models.CharField(max_length=50, default=RULE_VERSION_INITIAL)
    criteria_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'clasificacion de entidad'
        verbose_name_plural = 'clasificaciones de entidades'
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'period', 'classification_type'],
                name='unique_entity_classification',
            ),
        ]
        indexes = [
            models.Index(fields=['entity', 'period'], name='idx_class_entity_period'),
            models.Index(fields=['period', 'classification_type'], name='idx_class_period_type'),
        ]

    def __str__(self):
        return f'{self.entity.code} - {self.classification_type} - {self.period}'
