from django.contrib import admin
from .models import AuditLog, AuditConfig, AuditSnapshot, AuditExport, UserActivity

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'model_name', 'object_repr']
    list_filter = ['action', 'app_name', 'timestamp']
    search_fields = ['object_repr', 'user__username', 'description']
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

class AuditConfigAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'app_name', 'enabled', 'track_creates', 'track_updates', 'track_deletes']
    list_filter = ['app_name', 'enabled']
    search_fields = ['model_name']

admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(AuditConfig, AuditConfigAdmin)
admin.site.register(AuditSnapshot)
admin.site.register(AuditExport)
admin.site.register(UserActivity)
