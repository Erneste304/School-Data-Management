from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

class DashboardHomeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        role = request.user.profile.role

        if role in ['ADMIN', 'HEAD']:
            return redirect('admin_dashboard')
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