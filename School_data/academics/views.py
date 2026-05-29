from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.permissions import RoleRequiredMixin

class BasePortalView(LoginRequiredMixin, TemplateView):
    """Base class requiring login."""
    pass

class AdminAcademicsDashboardView(RoleRequiredMixin, BasePortalView):
    """Allows Admin/Head/DOS to manage all academic data."""
    allowed_roles = ['admin', 'head_teacher', 'dos']
    template_name = 'academics/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context['role_desc'] = 'Academic Manager'
        return context

class TeacherPortalView(RoleRequiredMixin, BasePortalView):
    """Teacher's view for managing their subjects and students."""
    allowed_roles = ['teacher', 'animateur', 'animatrice']
    template_name = 'academics/teacher_portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Subject
        
        # Fetch subjects specifically assigned to this user
        # This uses the related_name='subjects_taught' from the Subject model
        context['taught_subjects'] = Subject.objects.filter(teacher=self.request.user)
        
        # Add quick actions intended for the teacher dashboard
        # We point them to teacher_dashboard for now to avoid NoReverseMatch 
        # until the specific detail views are implemented.
        context['teacher_actions'] = [
            {'name': 'Attendance', 'url_name': 'teacher_dashboard'}, 
            {'name': 'Enrollments', 'url_name': 'teacher_dashboard'},
            {'name': 'Grading', 'url_name': 'teacher_dashboard'},
        ]
        
        context['role_desc'] = self.request.user.profile.get_role_display()
        return context

class StudentPortalView(RoleRequiredMixin, BasePortalView):
    """Student's view of their own data."""
    allowed_roles = ['student']
    template_name = 'academics/student_portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Future: Get request.user.student to display grades
        context['role_desc'] = 'Student'
        return context

class ParentPortalView(RoleRequiredMixin, BasePortalView):
    allowed_roles = ['parent']
    template_name = 'academics/parent_portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Access the linked student record via the user's profile
        linked_student = self.request.user.profile.related_student
        
        if linked_student:
            context['student_name'] = linked_student.user.get_full_name() or linked_student.user.username
            context['student_class'] = linked_student.current_class.name if linked_student.current_class else 'N/A'
            # Future: Fetch grades, attendance for linked_student
        else:
            context['student_name'] = 'No student linked'
            
        context['role_desc'] = 'Parent'
        return context
