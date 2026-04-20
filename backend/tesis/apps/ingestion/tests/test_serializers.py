from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.catalog.models import Entity, Period
from apps.ingestion.models import Document
from apps.ingestion.serializers import (
    DocumentUploadSerializer,
    ImportJobExecutionSerializer,
    ImportJobProcessSerializer,
)


class DocumentUploadSerializerTestCase(TestCase):
    def test_rejects_non_xlsx_file(self):
        file_obj = SimpleUploadedFile(
            'indicadores.csv',
            b'col1,col2',
            content_type='text/csv',
        )
        serializer = DocumentUploadSerializer(
            data={'name': 'Carga abril', 'file': file_obj}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)

    def test_accepts_xlsx_file(self):
        file_obj = SimpleUploadedFile(
            'indicadores.xlsx',
            b'fake-xlsx-content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        serializer = DocumentUploadSerializer(
            data={'name': 'Carga abril', 'file': file_obj}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)


class ImportJobExecutionSerializerTestCase(TestCase):
    def test_accepts_existing_document_reference(self):
        document = Document.objects.create(name='Doc 1', file='documents/test.xlsx')
        serializer = ImportJobExecutionSerializer(data={'document': document.id})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_missing_document(self):
        serializer = ImportJobExecutionSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('document', serializer.errors)


class ImportJobProcessSerializerTestCase(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(code='ENT-001', name='Entidad 1', type='empresa')
        self.period = Period.objects.create(year=2026, month=4, period_type='mensual')

    def test_accepts_active_entity_and_period(self):
        serializer = ImportJobProcessSerializer(
            data={'entity': self.entity.id, 'period': self.period.id}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_inactive_entity(self):
        self.entity.is_active = False
        self.entity.save(update_fields=['is_active'])

        serializer = ImportJobProcessSerializer(
            data={'entity': self.entity.id, 'period': self.period.id}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('entity', serializer.errors)
