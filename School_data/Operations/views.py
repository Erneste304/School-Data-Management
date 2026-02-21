from django.shortcuts import render
from django.views.generic import ListView
from Users.mixins import RoleRequiredMixin
from .models import AuditLog

# Create your views here.

class AuditLogListView(RoleRequiredMixin, ListView):
    """
    View for Headteacher and Admins to view the system audit trail.
    """
    allowed_roles = ['HEAD', 'ADMIN']
    model = AuditLog
    template_name = 'operations/audit_log_list.html'
    context_object_name = 'audit_logs'

    def get_queryset(self):
        return AuditLog.objects.all().order_by('-timestamp')
