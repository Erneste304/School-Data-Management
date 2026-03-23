from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import AuditLog, AuditConfig, UserActivity
from accounts.views import role_required
from .utils import get_audit_stats

@login_required
@role_required(['head_teacher', 'admin'])
def audit_dashboard_view(request):
    stats = get_audit_stats()
    recent_logs = AuditLog.objects.select_related('user', 'content_type')[:20]
    active_sessions = UserActivity.objects.filter(logout_time__isnull=True).order_by('-last_activity')[:10]
    
    context = {
        'stats': stats,
        'recent_logs': recent_logs,
        'active_sessions': active_sessions,
    }
    return render(request, 'audit/dashboard.html', context)

@login_required
@role_required(['head_teacher', 'admin'])
def log_list_view(request):
    logs = AuditLog.objects.select_related('user', 'content_type')
    
    # Filtering
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    model_name = request.GET.get('model')
    if model_name:
        logs = logs.filter(model_name=model_name)
    
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    
    # Pagination would go here in a real app
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    context = {
        'logs': logs[:100],  # Limit to 100 for now
        'users': User.objects.filter(is_staff=True),
        'actions': AuditLog.ACTION_CHOICES,
        'models': AuditConfig.objects.values_list('model_name', flat=True),
    }
    return render(request, 'audit/log_list.html', context)

@login_required
@role_required(['head_teacher', 'admin'])
def log_detail_view(request, pk):
    log = get_object_or_404(AuditLog, pk=pk)
    return render(request, 'audit/log_detail.html', {'log': log})

@login_required
@role_required(['head_teacher', 'admin'])
def user_activity_view(request):
    activities = UserActivity.objects.select_related('user').order_by('-login_time')
    return render(request, 'audit/user_activity.html', {'activities': activities})
