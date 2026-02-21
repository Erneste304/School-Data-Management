from django.urls import path
from .views import AuditLogListView

app_name = 'operations'

urlpatterns = [
    path('audit-logs/', AuditLogListView.as_view(), name='audit_log_list'),
]
