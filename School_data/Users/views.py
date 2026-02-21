from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum

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
        from Academics.models import Student
        from Staff.models import StaffRecord
        from Finance.models import Transaction
        from Operations.models import AuditLog

        context = {
            'role': 'head',
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_staff': StaffRecord.objects.filter(is_active=True).count(),
            'pending_staff_count': StaffRecord.objects.filter(is_approved=False).count(),
            'total_collections': Transaction.objects.filter(status='APPROVED').aggregate(total=Sum('amount_paid'))['total'] or 0,
            'pending_approvals_count': Transaction.objects.filter(status='PENDING').count() + StaffRecord.objects.filter(is_approved=False).count(),
            'recent_logs': AuditLog.objects.all().order_by('-timestamp')[:5],
            'pending_transactions': Transaction.objects.filter(status='PENDING').order_by('-transaction_date')[:5],
            'pending_staff': StaffRecord.objects.filter(is_approved=False).order_by('-hire_date')[:5],
        }
        return render(request, 'users/headteacher_dashboard.html', context)

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