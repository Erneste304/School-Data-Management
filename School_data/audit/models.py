from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json

User = get_user_model()

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('restore', 'Restore'),
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.CharField(max_length=100, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=200, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    app_name = models.CharField(max_length=100, blank=True)
    
    old_data = models.JSONField(default=dict, blank=True)
    new_data = models.JSONField(default=dict, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    
    description = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
    
    def get_change_summary(self):
        if not self.changes:
            return "No changes"
        summary = []
        for field, change in self.changes.items():
            old_val = change.get('old', 'N/A')
            new_val = change.get('new', 'N/A')
            summary.append(f"{field}: {old_val} → {new_val}")
        return ", ".join(summary)

class AuditConfig(models.Model):
    model_name = models.CharField(max_length=200, unique=True)
    app_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    track_views = models.BooleanField(default=False)
    track_creates = models.BooleanField(default=True)
    track_updates = models.BooleanField(default=True)
    track_deletes = models.BooleanField(default=True)
    exclude_fields = models.JSONField(default=list, blank=True)
    retention_days = models.IntegerField(default=365)
    
    class Meta:
        ordering = ['app_name', 'model_name']
    
    def __str__(self):
        return f"{self.app_name}.{self.model_name}"

class AuditSnapshot(models.Model):
    snapshot_type = models.CharField(max_length=20, choices=(('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')
    data = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']

class AuditExport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_exports')
    export_type = models.CharField(max_length=50)
    filters = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')), default='pending')
    file = models.FileField(upload_to='audit_exports/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    session_key = models.CharField(max_length=40, blank=True)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    actions_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = "User Activities"
    
    def __str__(self):
        return f"{self.user} - {self.login_time}"
