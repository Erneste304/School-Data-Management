from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import UserActivity
from .thread_local import set_current_request
import re

class AuditMiddleware(MiddlewareMixin):
    EXCLUDE_PATHS = [
        r'^/admin/jsi18n/',
        r'^/static/',
        r'^/media/',
        r'^/favicon.ico',
    ]
    
    def process_request(self, request):
        set_current_request(request)
        if request.user.is_authenticated:
            request._audit_ip = self.get_client_ip(request)
            request._audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
            request._audit_path = request.path
            request._audit_method = request.method
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated:
            activity, created = UserActivity.objects.get_or_create(
                user=request.user,
                session_key=request.session.session_key if hasattr(request, 'session') else '',
                logout_time__isnull=True,
                defaults={
                    'login_time': timezone.now(),
                    'ip_address': getattr(request, '_audit_ip', ''),
                    'user_agent': getattr(request, '_audit_user_agent', ''),
                }
            )
            if not created:
                activity.actions_count += 1
                activity.save()
        
        set_current_request(None)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
