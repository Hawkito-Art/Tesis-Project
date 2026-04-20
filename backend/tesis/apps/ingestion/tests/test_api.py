from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Entity, Period
from apps.indicators.models import Indicator, IndicatorGroup
from apps.indicators.models import IndicatorRecord
from apps.ingestion.models import Document, ImportJob

User = get_user_model()


class IngestionApiTestCase(APITestCase):
    def setUp(self):
        self.documents_url = '/api/ingestion/documents/'
        self.admin_user = User.objects.create_user(
            email='admin-ingestion@test.com',
            password='Passw0rd!123',
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            email='regular-ingestion@test.com',
            password='Passw0rd!123',
        )

    def test_document_upload_requires_authentication(self):
        file_obj = SimpleUploadedFile(
            'indicadores.xlsx',
            b'fake-xlsx-content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response = self.client.post(
            self.documents_url,
            {'name': 'Carga abril', 'file': file_obj},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_document_upload_forbidden_for_user_without_role(self):
        self.client.force_authenticate(user=self.regular_user)
        file_obj = SimpleUploadedFile(
            'indicadores.xlsx',
            b'fake-xlsx-content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        response = self.client.post(
            self.documents_url,
            {'name': 'Carga abril', 'file': file_obj},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_document_upload_creates_document_and_pending_import_job(self):
        self.client.force_authenticate(user=self.admin_user)
        file_obj = SimpleUploadedFile(
            'indicadores.xlsx',
            b'fake-xlsx-content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        response = self.client.post(
            self.documents_url,
            {'name': 'Carga abril', 'file': file_obj},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(ImportJob.objects.count(), 1)

        document = Document.objects.first()
        import_job = ImportJob.objects.first()

        self.assertEqual(document.uploaded_by_id, self.admin_user.id)
        self.assertEqual(document.status, 'pendiente')
        self.assertEqual(import_job.document_id, document.id)
        self.assertEqual(import_job.status, 'pendiente')

    def test_import_job_detail_returns_404_when_missing(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/ingestion/import-jobs/9999/', format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _build_workbook_upload(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['INDICADORES', 'U:M', 'AÑO', 'Año Anter', 'PLAN', 'REAL', 'R/P', 'R/AA', 'Estimado mes', 'Estimado cierre'])
        sheet.append(['Ventas Totales', 'MP', 145881.2, 100209.3, 145881.2, 121785.0, 83.5, 102.3, 10764.9, 145881.2])
        sheet.append(['Indicador Desconocido', 'MP', 100.0, 90.0, 100.0, 80.0, 80.0, 88.9, 88.0, 100.0])

        from io import BytesIO

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            'indicadores.xlsx',
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    def test_import_job_process_is_partial_and_tracks_errors(self):
        group = IndicatorGroup.objects.create(name='Fundamental', group_type='fundamental')
        Indicator.objects.create(
            indicator='VENTAS_TOT',
            name='Ventas Totales',
            unit='MP',
            group=group,
        )
        entity = Entity.objects.create(code='ENT-900', name='Entidad 900', type='empresa')
        period = Period.objects.create(year=2026, month=5, period_type='mensual')

        self.client.force_authenticate(user=self.admin_user)
        upload_response = self.client.post(
            self.documents_url,
            {'name': 'Carga parcial', 'file': self._build_workbook_upload()},
            format='multipart',
        )
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        import_job_id = upload_response.data['import_job']['id']

        process_response = self.client.post(
            f'/api/ingestion/import-jobs/{import_job_id}/',
            {'entity': entity.id, 'period': period.id},
            format='json',
        )
        self.assertEqual(process_response.status_code, status.HTTP_200_OK)
        self.assertEqual(process_response.data['import_job']['status'], 'completado')
        self.assertEqual(process_response.data['import_job']['total_rows'], 2)
        self.assertEqual(process_response.data['import_job']['processed_rows'], 2)
        self.assertEqual(process_response.data['import_job']['error_rows'], 1)
        self.assertIn(
            'Indicador no encontrado por nombre exacto',
            process_response.data['import_job']['error_log'],
        )
        self.assertEqual(process_response.data['upsert']['total'], 4)

        records_count = IndicatorRecord.objects.filter(
            entity=entity,
            period=period,
            indicator__name='Ventas Totales',
        ).count()
        self.assertEqual(records_count, 4)

        details_response = self.client.get(
            f'/api/ingestion/import-jobs/{import_job_id}/details/',
            format='json',
        )
        self.assertEqual(details_response.status_code, status.HTTP_200_OK)
        self.assertEqual(details_response.data['count'], 2)
        invalid_rows = [row for row in details_response.data['results'] if not row['is_valid']]
        self.assertEqual(len(invalid_rows), 1)

    def test_import_job_process_requires_entity_and_period(self):
        self.client.force_authenticate(user=self.admin_user)
        upload_response = self.client.post(
            self.documents_url,
            {'name': 'Carga parcial', 'file': self._build_workbook_upload()},
            format='multipart',
        )
        import_job_id = upload_response.data['import_job']['id']

        process_response = self.client.post(
            f'/api/ingestion/import-jobs/{import_job_id}/',
            {},
            format='json',
        )

        self.assertEqual(process_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', process_response.data)
        self.assertIn('details', process_response.data['error'])
        self.assertIn('entity', process_response.data['error']['details'])
        self.assertIn('period', process_response.data['error']['details'])

    def test_import_job_details_is_paginated(self):
        group = IndicatorGroup.objects.create(name='Fundamental', group_type='fundamental')
        Indicator.objects.create(
            indicator='VENTAS_TOT',
            name='Ventas Totales',
            unit='MP',
            group=group,
        )
        entity = Entity.objects.create(code='ENT-901', name='Entidad 901', type='empresa')
        period = Period.objects.create(year=2026, month=6, period_type='mensual')

        self.client.force_authenticate(user=self.admin_user)
        upload_response = self.client.post(
            self.documents_url,
            {'name': 'Carga paginada', 'file': self._build_workbook_upload()},
            format='multipart',
        )
        import_job_id = upload_response.data['import_job']['id']

        self.client.post(
            f'/api/ingestion/import-jobs/{import_job_id}/',
            {'entity': entity.id, 'period': period.id},
            format='json',
        )

        details_response = self.client.get(
            f'/api/ingestion/import-jobs/{import_job_id}/details/?page=1&page_size=1',
            format='json',
        )
        self.assertEqual(details_response.status_code, status.HTTP_200_OK)
        self.assertEqual(details_response.data['count'], 2)
        self.assertEqual(len(details_response.data['results']), 1)
        self.assertIn('next', details_response.data)
        self.assertIsNotNone(details_response.data['next'])

    def test_import_job_upsert_updates_existing_record_on_reprocess(self):
        group = IndicatorGroup.objects.create(name='Fundamental', group_type='fundamental')
        indicator = Indicator.objects.create(
            indicator='VENTAS_TOT',
            name='Ventas Totales',
            unit='MP',
            group=group,
        )
        entity = Entity.objects.create(code='ENT-902', name='Entidad 902', type='empresa')
        period = Period.objects.create(year=2026, month=7, period_type='mensual')

        self.client.force_authenticate(user=self.admin_user)
        upload_response = self.client.post(
            self.documents_url,
            {'name': 'Carga upsert', 'file': self._build_workbook_upload()},
            format='multipart',
        )
        import_job_id = upload_response.data['import_job']['id']

        first_process = self.client.post(
            f'/api/ingestion/import-jobs/{import_job_id}/',
            {'entity': entity.id, 'period': period.id},
            format='json',
        )
        self.assertEqual(first_process.status_code, status.HTTP_200_OK)

        record = IndicatorRecord.objects.get(
            entity=entity,
            period=period,
            indicator=indicator,
            variable_name='real_acumulado',
        )
        self.assertEqual(str(record.value), '121785.0000')

        second_workbook = Workbook()
        second_sheet = second_workbook.active
        second_sheet.append(['INDICADORES', 'U:M', 'AÑO', 'Año Anter', 'PLAN', 'REAL', 'R/P', 'R/AA', 'Estimado mes', 'Estimado cierre'])
        second_sheet.append(['Ventas Totales', 'MP', 145881.2, 100209.3, 145881.2, 130000.0, 83.5, 102.3, 10764.9, 145881.2])

        from io import BytesIO

        buffer = BytesIO()
        second_workbook.save(buffer)
        buffer.seek(0)
        second_file = SimpleUploadedFile(
            'indicadores-actualizado.xlsx',
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        second_upload = self.client.post(
            self.documents_url,
            {'name': 'Carga upsert 2', 'file': second_file},
            format='multipart',
        )
        self.assertEqual(second_upload.status_code, status.HTTP_201_CREATED)
        second_job_id = second_upload.data['import_job']['id']

        second_process = self.client.post(
            f'/api/ingestion/import-jobs/{second_job_id}/',
            {'entity': entity.id, 'period': period.id},
            format='json',
        )
        self.assertEqual(second_process.status_code, status.HTTP_200_OK)

        updated_record = IndicatorRecord.objects.get(
            entity=entity,
            period=period,
            indicator=indicator,
            variable_name='real_acumulado',
        )
        self.assertEqual(str(updated_record.value), '130000.0000')
