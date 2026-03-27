from django.db import models


class EntityClassification(models.Model):
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

    def __str__(self):
        return f'{self.entity.code} - {self.classification_type} - {self.period}'
