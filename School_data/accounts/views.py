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

from .models import CustomUser, StaffProfile, ParentProfile, ParentStudentRelationship
from .forms import LoginForm, StaffCreateForm, StaffEditForm, StaffProfileForm, StudentCreateForm, ParentCreateForm, ParentProfileForm, ParentStudentLinkForm, UserProfileForm, UserPasswordChangeForm
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

    elif user.is_teacher:
        from academics.models import TeacherProfile
        try:
            teacher_profile = TeacherProfile.objects.get(user=user)
            context['subject_count'] = teacher_profile.subjects.count()
            context['student_count'] = CustomUser.objects.filter(role='student').count()
            context['class_count'] = teacher_profile.subjects.values('classschedule__class_assigned').distinct().count()
        except TeacherProfile.DoesNotExist:
            context['subject_count'] = 0
            context['student_count'] = 0
            context['class_count'] = 0
        return render(request, 'dashboard/teacher.html', context)

    elif user.is_student:
        from academics.models import Student
        try:
            student = Student.objects.get(user=user)
            context['gpa'] = student.calculate_gpa()
            context['attendance_rate'] = student.get_attendance_rate()
            context['pending_assignments'] = student.get_pending_assignments()
        except Student.DoesNotExist:
            context['gpa'] = 0.00
            context['attendance_rate'] = 0
            context['pending_assignments'] = 0
        return render(request, 'dashboard/student.html', context)

    elif user.is_parent:
        from accounts.models import ParentProfile
        try:
            parent_profile = ParentProfile.objects.get(user=user)
            context['children_count'] = parent_profile.get_children_count()
            children = parent_profile.get_children()
            if children:
                total_gpa = sum(child.calculate_gpa() for child in children)
                total_attendance = sum(child.get_attendance_rate() for child in children)
                context['avg_gpa'] = round(total_gpa / children.count(), 2)
                context['avg_attendance'] = round(total_attendance / children.count(), 2)
            else:
                context['avg_gpa'] = 0.00
                context['avg_attendance'] = 0
        except ParentProfile.DoesNotExist:
            context['children_count'] = 0
            context['avg_gpa'] = 0.00
            context['avg_attendance'] = 0
        return render(request, 'dashboard/parent.html', context)

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


@login_required
def student_list(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    from academics.models import Student
    students = Student.objects.select_related('user').prefetch_related('parents__parent').order_by('user__last_name', 'user__first_name')
    return render(request, 'accounts/student_list.html', {'students': students})


@login_required
def student_create(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    from academics.models import Student, Class

    if request.method == 'POST':
        form = StudentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            
            # Create Student record
            student = Student.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                enrollment_date=form.cleaned_data['enrollment_date'],
                current_class=form.cleaned_data.get('current_class')
            )
            
            # Create enrollment if class is assigned
            if student.current_class:
                from academics.models import Enrollment
                Enrollment.objects.get_or_create(
                    student=student,
                    enrolled_class=student.current_class,
                    academic_year='2025-2026'
                )
            
            messages.success(request, f'Student {user.get_full_name()} created successfully.')
            return redirect('accounts:student_list')
    else:
        form = StudentCreateForm()

    return render(request, 'accounts/student_form.html', {
        'form': form,
        'action': 'Create',
    })


@login_required
def student_detail(request, pk):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    from academics.models import Student
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'accounts/student_detail.html', {'student': student})


@login_required
def parent_list(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    parents = CustomUser.objects.filter(role='parent').select_related('parent_profile').prefetch_related('parent_profile__children').order_by('last_name', 'first_name')
    return render(request, 'accounts/parent_list.html', {'parents': parents})


@login_required
def parent_create(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = ParentCreateForm(request.POST, request.FILES)
        profile_form = ParentProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, f'Parent {user.get_full_name()} created successfully.')
            return redirect('accounts:parent_list')
    else:
        form = ParentCreateForm()
        profile_form = ParentProfileForm()

    return render(request, 'accounts/parent_form.html', {
        'form': form,
        'profile_form': profile_form,
        'action': 'Create',
    })


@login_required
def parent_detail(request, pk):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    parent_user = get_object_or_404(CustomUser, pk=pk, role='parent')
    profile, _ = ParentProfile.objects.get_or_create(user=parent_user)
    return render(request, 'accounts/parent_detail.html', {
        'parent_user': parent_user,
        'profile': profile,
    })


@login_required
def link_parent_student(request):
    if not request.user.is_management:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    from academics.models import Student

    if request.method == 'POST':
        form = ParentStudentLinkForm(request.POST)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            students = form.cleaned_data['students']
            
            for student_user in students:
                student = get_object_or_404(Student, user=student_user)
                parent_profile = get_object_or_404(ParentProfile, user=parent)
                
                # Create or update relationship
                relationship, created = ParentStudentRelationship.objects.get_or_create(
                    parent=parent_profile,
                    student=student,
                    defaults={
                        'relationship_type': form.cleaned_data['relationship_type'],
                        'is_primary_guardian': form.cleaned_data['is_primary_guardian'],
                        'can_view_grades': form.cleaned_data['can_view_grades'],
                        'can_view_attendance': form.cleaned_data['can_view_attendance'],
                        'can_view_discipline': form.cleaned_data['can_view_discipline'],
                        'can_view_fees': form.cleaned_data['can_view_fees'],
                    }
                )
                
                if not created:
                    # Update existing relationship
                    relationship.relationship_type = form.cleaned_data['relationship_type']
                    relationship.is_primary_guardian = form.cleaned_data['is_primary_guardian']
                    relationship.can_view_grades = form.cleaned_data['can_view_grades']
                    relationship.can_view_attendance = form.cleaned_data['can_view_attendance']
                    relationship.can_view_discipline = form.cleaned_data['can_view_discipline']
                    relationship.can_view_fees = form.cleaned_data['can_view_fees']
                    relationship.save()
            
            messages.success(request, f'Parent {parent.get_full_name()} linked to {students.count()} student(s).')
            return redirect('accounts:parent_list')
    else:
        form = ParentStudentLinkForm()

    return render(request, 'accounts/parent_student_link.html', {'form': form})


@login_required
def student_grades(request):
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from academics.models import Student, ExamResult
    student = get_object_or_404(Student, user=request.user)
    results = ExamResult.objects.filter(
        enrollment__student=student
    ).select_related('exam__subject').order_by('-exam__date')
    
    return render(request, 'accounts/student_grades.html', {
        'student': student,
        'results': results,
    })


@login_required
def student_attendance(request):
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from academics.models import Student, Attendance
    student = get_object_or_404(Student, user=request.user)
    attendance_records = Attendance.objects.filter(
        enrollment__student=student
    ).select_related('enrollment__enrolled_class').order_by('-date')
    
    return render(request, 'accounts/student_attendance.html', {
        'student': student,
        'attendance_records': attendance_records,
    })


@login_required
def student_assignments(request):
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from academics.models import Student, Assignment, AssignmentSubmission
    student = get_object_or_404(Student, user=request.user)
    
    # Get all assignments for the student's class
    assignments = Assignment.objects.filter(
        subject__classschedule__class_assigned=student.current_class
    ).distinct().order_by('-due_date')
    
    # Get submissions for this student
    submissions = AssignmentSubmission.objects.filter(
        enrollment__student=student
    ).select_related('assignment')
    
    return render(request, 'accounts/student_assignments.html', {
        'student': student,
        'assignments': assignments,
        'submissions': submissions,
    })


@login_required
def teacher_subjects(request):
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from academics.models import TeacherProfile, Subject
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    subjects = teacher_profile.subjects.all().prefetch_related('classschedule_set')
    
    return render(request, 'accounts/teacher_subjects.html', {
        'teacher_profile': teacher_profile,
        'subjects': subjects,
    })


@login_required
def teacher_grades(request):
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from academics.models import TeacherProfile, Subject, Class, Student, Enrollment, ExamResult
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    subjects = teacher_profile.subjects.all()
    
    # Get all students in classes where teacher teaches
    classes = Class.objects.filter(
        classschedule__subject__in=subjects
    ).distinct()
    
    students = Student.objects.filter(
        current_class__in=classes,
        is_active=True
    ).select_related('user', 'current_class')
    
    return render(request, 'accounts/teacher_grades.html', {
        'teacher_profile': teacher_profile,
        'subjects': subjects,
        'students': students,
    })


@login_required
def teacher_attendance(request):
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from academics.models import TeacherProfile, Subject, Class, Student
    from datetime import date
    
    teacher_profile = get_object_or_404(TeacherProfile, user=request.user)
    subjects = teacher_profile.subjects.all()
    
    # Get all classes where teacher teaches
    classes = Class.objects.filter(
        classschedule__subject__in=subjects
    ).distinct()
    
    # Get students in those classes
    students = Student.objects.filter(
        current_class__in=classes,
        is_active=True
    ).select_related('user', 'current_class')
    
    return render(request, 'accounts/teacher_attendance.html', {
        'teacher_profile': teacher_profile,
        'classes': classes,
        'students': students,
        'today': date.today(),
    })


@login_required
def parent_children(request):
    if not request.user.is_parent:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    children = parent_profile.get_children().select_related('user', 'current_class')
    
    return render(request, 'accounts/parent_children.html', {
        'parent_profile': parent_profile,
        'children': children,
    })


@login_required
def parent_grades(request):
    if not request.user.is_parent:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    children = parent_profile.get_children().select_related('user', 'current_class')
    
    # Get all exam results for all children
    from academics.models import ExamResult
    from django.db.models import Q
    
    child_ids = [child.pk for child in children]
    results = ExamResult.objects.filter(
        enrollment__student__in=child_ids
    ).select_related('exam__subject', 'enrollment__student__user').order_by('-exam__date')
    
    return render(request, 'accounts/parent_grades.html', {
        'parent_profile': parent_profile,
        'children': children,
        'results': results,
    })


@login_required
def parent_attendance(request):
    if not request.user.is_parent:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    parent_profile = get_object_or_404(ParentProfile, user=request.user)
    children = parent_profile.get_children().select_related('user', 'current_class')
    
    # Get all attendance records for all children
    from academics.models import Attendance
    from django.db.models import Q
    
    child_ids = [child.pk for child in children]
    attendance_records = Attendance.objects.filter(
        enrollment__student__in=child_ids
    ).select_related('enrollment__student__user', 'enrollment__enrolled_class').order_by('-date')
    
    return render(request, 'accounts/parent_attendance.html', {
        'parent_profile': parent_profile,
        'children': children,
        'attendance_records': attendance_records,
    })


@login_required
def profile_edit(request):
    """Allow users to edit their own profile information."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard:home')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def password_change(request):
    """Allow users to change their password."""
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully. Please log in again.')
            logout(request)
            return redirect('accounts:login')
    else:
        form = UserPasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})