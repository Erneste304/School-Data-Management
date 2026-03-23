from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser, StaffProfile
from accounts.views import role_required
from .forms import StaffProfileForm, StaffUserForm

@login_required
@role_required(['head_teacher', 'admin'])
def staff_list_view(request):
    staff_members = CustomUser.objects.exclude(role='public')
    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})

@login_required
@role_required(['head_teacher', 'admin'])
def staff_toggle_status(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot disable your own account.")
    else:
        user.is_active = not user.is_active
        user.save()
        status = "enabled" if user.is_active else "disabled"
        messages.success(request, f"Staff {user.get_full_name()} has been {status}.")
    return redirect('staff:staff_list')

@login_required
@role_required(['head_teacher', 'admin'])
def staff_create_view(request):
    if request.method == 'POST':
        user_form = StaffUserForm(request.POST, request.FILES)
        profile_form = StaffProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.created_by = request.user
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, f"Staff {user.get_full_name()} created successfully.")
            return redirect('staff:staff_list')
    else:
        user_form = StaffUserForm()
        profile_form = StaffProfileForm()
    
    return render(request, 'staff/staff_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Create Staff'
    })
