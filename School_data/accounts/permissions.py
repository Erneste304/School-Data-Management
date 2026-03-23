from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from rest_framework.permissions import BasePermission


# ── Django view mixins (for template views) ───────────────────────────────────

class RoleRequiredMixin(UserPassesTestMixin):
    """Base mixin — set allowed_roles on the view class."""
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.role in self.allowed_roles or user.is_admin
        )

    def handle_no_permission(self):
        return redirect('accounts:login')


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']


class HeadTeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'head_teacher']


class DOSRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'head_teacher', 'dos']


class DODRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'head_teacher', 'dod']


class AccountantRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'accountant']


class AnimateurRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'head_teacher', 'animateur', 'animatrice']


# ── DRF permissions (for REST API views) ─────────────────────────────────────

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsHeadTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'head_teacher')


class IsDOSOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'admin', 'head_teacher', 'dos'
        )


class IsDODOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'admin', 'head_teacher', 'dod'
        )


class IsAccountantOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'admin', 'accountant'
        )


class IsStaffMember(BasePermission):
    """Any authenticated non-public user."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != 'public'