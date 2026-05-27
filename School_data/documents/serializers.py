from rest_framework import serializers
from .models import Document, DocumentCategory


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description']


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'category', 'category_name', 'file',
                  'uploaded_by', 'uploaded_by_name', 'upload_date', 'file_size', 'file_type',
                  'is_public', 'download_count', 'tags']
        read_only_fields = ['uploaded_by', 'upload_date', 'download_count']
