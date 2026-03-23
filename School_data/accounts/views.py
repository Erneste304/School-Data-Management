from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from functools import wraps
import json

from .models import CustomUser, StaffProfile
from .forms import LoginForm, StaffCreateForm, StaffEditForm, StaffProfileForm
from .permissions import HeadTeacherRequiredMixin, AdminRequiredMixin

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role in allowed_roles or request.user.role == 'admin':
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'Access denied: {request.user.role} role not authorized.')
                return redirect('dashboard:home')
        return _wrapped_view
    return decorator


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return render(request, self.template_name, {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Your account has been disabled. Contact the head teacher.')
                return render(request, self.template_name, {'form': form})
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'dashboard:home'))
        return render(request, self.template_name, {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def dashboard_home(request):
    user = request.user
    context = {'user': user}

    if user.is_management:
        context['total_staff']    = CustomUser.objects.filter(is_staff_member=True).count() if False else \
                                    CustomUser.objects.exclude(role='public').count()
        context['active_staff']   = CustomUser.objects.exclude(role='public').filter(is_active=True).count()
        context['inactive_staff'] = CustomUser.objects.exclude(role='public').filter(is_active=False).count()
        return render(request, 'dashboard/head_teacher.html', context)

    elif user.is_dos:
        return redirect('academics:admin_academics_dashboard')

    elif user.is_dod:
        return redirect('discipline:dashboard')

    elif user.is_accountant:
        return redirect('finance:dashboard')

    elif user.is_animateur:
        return redirect('activities:dashboard')

    return render(request, 'dashboard/default.html', context)


@login_required
def staff_list(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    staff = CustomUser.objects.exclude(role='public').select_related('profile').order_by('role', 'last_name')
    return render(request, 'accounts/staff_list.html', {'staff': staff})


@login_required
def staff_create(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = StaffCreateForm(request.POST, request.FILES, requesting_user=request.user)
        profile_form = StaffProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, f'Staff member {user.get_full_name()} created successfully.')
            return redirect('accounts:staff_list')
    else:
        form = StaffCreateForm(requesting_user=request.user)
        profile_form = StaffProfileForm()

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'profile_form': profile_form,
        'action': 'Create',
    })


@login_required
def staff_edit(request, pk):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    staff_user = get_object_or_404(CustomUser, pk=pk)
    profile, _ = StaffProfile.objects.get_or_create(user=staff_user)

    if staff_user.is_admin and not request.user.is_admin:
        messages.error(request, 'Only admin can edit another admin account.')
        return redirect('accounts:staff_list')

    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=staff_user, requesting_user=request.user)
        profile_form = StaffProfileForm(request.POST, instance=profile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, f'{staff_user.get_full_name()} updated successfully.')
            return redirect('accounts:staff_list')
    else:
        form = StaffEditForm(instance=staff_user, requesting_user=request.user)
        profile_form = StaffProfileForm(instance=profile)

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'profile_form': profile_form,
        'staff_user': staff_user,
        'action': 'Edit',
    })


@login_required
def staff_detail(request, pk):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    staff_user = get_object_or_404(CustomUser, pk=pk)
    profile, _ = StaffProfile.objects.get_or_create(user=staff_user)
    return render(request, 'accounts/staff_detail.html', {
        'staff_user': staff_user,
        'profile': profile,
    })


@login_required
@require_POST
def staff_toggle_access(request, pk):
    if not request.user.is_management:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)

    staff_user = get_object_or_404(CustomUser, pk=pk)

    if staff_user == request.user:
        return JsonResponse({'success': False, 'error': 'You cannot disable your own account'}, status=400)
    if staff_user.is_admin and not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Only admin can disable admin accounts'}, status=403)

    data = json.loads(request.body)
    staff_user.is_active = data.get('enabled', True)
    staff_user.save(update_fields=['is_active'])

    action = 'enabled' if staff_user.is_active else 'disabled'
    messages.success(request, f'{staff_user.get_full_name()} has been {action}.')

    return JsonResponse({'success': True, 'is_active': staff_user.is_active})


@login_required
def staff_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Only admin can delete accounts.')
        return redirect('accounts:staff_list')

    staff_user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        name = staff_user.get_full_name()
        staff_user.delete()
        messages.success(request, f'{name} has been removed from the system.')
        return redirect('accounts:staff_list')

    return render(request, 'accounts/staff_confirm_delete.html', {'staff_user': staff_user})