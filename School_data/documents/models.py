from django.db import models
from django.conf import settings


class DocumentCategory(models.Model):
    """Categories for organizing documents"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Document Categories"

    def __str__(self):
        return self.name


class Document(models.Model):
    """Document library for storing school documents"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, related_name='documents')
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)  # in bytes
    file_type = models.CharField(max_length=50, blank=True)
    is_public = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    class Meta:
        verbose_name_plural = "Documents"
        ordering = ['-upload_date']

    def __str__(self):
        return self.title

    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
        self.save()


class DocumentSignature(models.Model):
    """Electronic signatures for documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='signatures')
    signed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_signatures')
    signature_data = models.TextField(help_text="Base64 encoded signature image or digital signature data")
    signed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Signed', 'Signed'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Document Signatures"
        unique_together = ('document', 'signed_by')

    def __str__(self):
        return f"{self.signed_by.get_full_name()} - {self.document.title}"


class DocumentShare(models.Model):
    """Share documents with specific users or groups"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_documents')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_shares')
    shared_at = models.DateTimeField(auto_now_add=True)
    can_edit = models.BooleanField(default=False)
    can_download = models.BooleanField(default=True)
    can_share = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Document Shares"
        unique_together = ('document', 'shared_with')

    def __str__(self):
        return f"{self.document.title} shared with {self.shared_with.get_full_name()}"


class DocumentAccessLog(models.Model):
    """Track document access and downloads"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_logs')
    accessed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_access_logs')
    action = models.CharField(
        max_length=50,
        choices=[
            ('Viewed', 'Viewed'),
            ('Downloaded', 'Downloaded'),
            ('Shared', 'Shared'),
            ('Signed', 'Signed'),
        ]
    )
    access_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Document Access Logs"
        ordering = ['-access_time']

    def __str__(self):
        return f"{self.accessed_by.get_full_name()} {self.action} {self.document.title}"


class DocumentVersion(models.Model):
    """Version control for documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to='documents/versions/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_versions')
    upload_date = models.DateTimeField(auto_now_add=True)
    change_notes = models.TextField(blank=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Document Versions"
        unique_together = ('document', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
