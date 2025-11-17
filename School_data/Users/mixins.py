from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.core.exceptions import ImproperlyConfigured, PermissionDenied


class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        # 1. Check for authentication first
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 2. Check if the user has a profile. If not, it's a server-side issue.
        if not hasattr(request.user, 'profile'):
            raise ImproperlyConfigured(
                "RoleRequiredMixin requires the user to have a 'profile' attribute."
            )
        
        # 3. Check if the user's role is in the allowed list.
        if request.user.profile.role not in self.allowed_roles:
            # For logged-in users without the right role, show a permission denied error.
            raise PermissionDenied

        # 4. If all checks pass, proceed with the view.
        return super().dispatch(request, *args, **kwargs)
    
class AdminOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']

class TeacherOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['TEACHER']