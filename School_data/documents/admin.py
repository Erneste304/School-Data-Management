from django.contrib import admin
from .models import (
    DocumentCategory, Document, DocumentSignature, DocumentShare,
    DocumentAccessLog, DocumentVersion
)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploaded_by', 'upload_date', 'file_size', 'is_public', 'requires_signature']
    list_filter = ['category', 'is_public', 'requires_signature', 'upload_date']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['upload_date', 'file_size', 'download_count']


@admin.register(DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    list_display = ['document', 'signed_by', 'signed_at', 'status']
    list_filter = ['status', 'signed_at']
    search_fields = ['document__title', 'signed_by__first_name', 'signed_by__last_name']
    readonly_fields = ['signed_at']


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ['document', 'shared_with', 'shared_by', 'shared_at', 'can_edit', 'can_download']
    list_filter = ['can_edit', 'can_download', 'can_share', 'shared_at']
    search_fields = ['document__title', 'shared_with__first_name', 'shared_with__last_name']
    readonly_fields = ['shared_at']


@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'accessed_by', 'action', 'access_time']
    list_filter = ['action', 'access_time']
    search_fields = ['document__title', 'accessed_by__first_name', 'accessed_by__last_name']
    readonly_fields = ['access_time']


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'uploaded_by', 'upload_date', 'file_size']
    list_filter = ['upload_date', 'version_number']
    search_fields = ['document__title', 'change_notes']
    readonly_fields = ['upload_date']
