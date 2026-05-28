from django.conf import settings
from django.db import models


class Document(models.Model):
    IMPORT_TYPE_CHOICES = [
        ('presupuesto', 'Presupuesto'),
        ('indicadores', 'Indicadores'),
        ('registros', 'Registros de indicadores'),
    ]

    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('error', 'Error'),
    ]

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/')
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES, default='indicadores')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ImportJob(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]

    document = models.ForeignKey(
        'ingestion.Document',
        on_delete=models.CASCADE,
        related_name='import_jobs',
    )
    entity = models.ForeignKey(
        'catalog.Entity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_jobs',
    )
    period = models.ForeignKey(
        'catalog.Period',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_jobs',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'trabajo de importacion'
        verbose_name_plural = 'trabajos de importacion'

    def __str__(self):
        return f'ImportJob {self.pk} - {self.status}'


class DocumentDetail(models.Model):
    import_job = models.ForeignKey(
        'ingestion.ImportJob',
        on_delete=models.CASCADE,
        related_name='details',
    )
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField(default=dict)
    is_valid = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'detalle de documento'
        verbose_name_plural = 'detalles de documentos'
        indexes = [
            models.Index(
                fields=['import_job', 'row_number'],
                name='idx_docdetail_job_row',
            ),
        ]

    def __str__(self):
        return f'Detalle fila {self.row_number} - Job {self.import_job_id}'
