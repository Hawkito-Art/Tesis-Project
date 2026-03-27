from rest_framework import serializers

from .models import Document, DocumentDetail, ImportJob


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'name', 'file', 'status',
            'uploaded_by', 'uploaded_by_email',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'uploaded_by', 'created_at', 'updated_at']


class DocumentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentDetail
        fields = [
            'id', 'import_job', 'row_number',
            'raw_data', 'is_valid', 'error_message',
            'created_at',
        ]
        read_only_fields = ['created_at']


class ImportJobSerializer(serializers.ModelSerializer):
    details = DocumentDetailSerializer(many=True, read_only=True)
    document_name = serializers.CharField(source='document.name', read_only=True)

    class Meta:
        model = ImportJob
        fields = [
            'id', 'document', 'document_name', 'status',
            'total_rows', 'processed_rows', 'error_rows',
            'error_log', 'details',
            'started_at', 'finished_at', 'created_at',
        ]
        read_only_fields = [
            'status', 'total_rows', 'processed_rows', 'error_rows',
            'error_log', 'started_at', 'finished_at', 'created_at',
        ]
