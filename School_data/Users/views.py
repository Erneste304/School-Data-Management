from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class LogoutView(View):
    """
    Subclassing View to handle logout via GET (and POST).
    Django 5.0+ requires POST for the built-in LogoutView for security reasons,
    but we're implementing GET support for development convenience.
    """
    def get(self, request):
        logout(request)
        return redirect('/')
    
    def post(self, request):
        logout(request)
        return redirect('/')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

class DashboardHomeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        role = request.user.profile.role

        if role == 'ADMIN':
            return redirect('admin_dashboard')
        elif role == 'HEAD':
            return redirect('headteacher_dashboard')
        elif role == 'DOD':
            return redirect('dod_dashboard')
        elif role == 'DOS':
            return redirect('dos_dashboard')
        elif role == 'TEACHER':
            return redirect('teacher_dashboard')
        elif role == 'STUDENT':
            return redirect('student_dashboard')
        elif role == 'PARENT':
            return redirect('parent_dashboard')
        elif role == 'ACCOUNTANT':
            return redirect('finance:accountant_dashboard')
        
        return redirect('logout')

class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/admin_dashboard.html', {'role': 'admin'})

class HeadteacherDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Full oversight: analytics, approvals, audit logs
        return render(request, 'users/headteacher_dashboard.html', {'role': 'head'})

class DODDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Discipline focus: incident reports, behavior tracking
        return render(request, 'users/dod_dashboard.html', {'role': 'dod'})

class DOSDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Placeholder for DOS logic: Discipline reports, Teacher reports
        return render(request, 'users/dos_dashboard.html', {'role': 'dos'})
    
class TeacherDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/teacher_dashboard.html', {'role': 'teacher'})
    

class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/student_dashboard.html', {'role': 'student'})
    

class AccountantDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/accountant_dashboard.html', {'role': 'accountant'})
    
class ParentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/parent_dashboard.html', {'role': 'parent'})