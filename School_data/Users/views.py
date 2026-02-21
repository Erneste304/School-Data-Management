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

    def form_valid(self, form):
        user = form.get_user()
        # Admin bypasses approval check
        if user.is_superuser or user.profile.role == 'ADMIN':
            return super().form_valid(form)
            
        if not user.profile.is_approved:
            from django.contrib import messages
            messages.error(self.request, "Your account is pending approval. Please contact the administrator.")
            return redirect('login')
        return super().form_valid(form)

class StaffRegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        from .models import CustomUser, Profile
        from django.contrib import messages

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        # Update profile (auto-created by signal in signals.py)
        profile = user.profile
        profile.role = role
        profile.is_approved = False
        profile.save()
        
        # Create StaffRecord for synchronization
        from Staff.models import StaffRecord
        from django.utils import timezone
        StaffRecord.objects.create(
            user=user,
            hire_date=timezone.now().date(),
            salary=0, # Placeholder, updated during formal onboarding
            department="New Joiner",
            is_approved=False
        )
        
        # Log audit trail if module exists
        try:
            from Operations.models import AuditLog
            AuditLog.objects.create(
                user=user,
                action="Registration",
                module="Users",
                description=f"New staff registration: {username} as {role}. Pending approval."
            )
        except: pass

        messages.success(request, "Registration successful! Please wait for administrator approval.")
        return redirect('login')

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
        elif role in ['TEACHER', 'ANIMATEUR', 'ANIMATRICE']:
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
        return render(request, 'academics/teacher_portal.html', {'role': 'teacher'})
    

class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'academics/student_portal.html', {'role': 'student'})
    

class AccountantDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'finance/accountant_dashboard.html', {'role': 'accountant'})
    
class ParentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'academics/parent_portal.html', {'role': 'parent'})

class ProfileDetailView(LoginRequiredMixin, View):
    """
    View for users to see and update their profile details.
    """
    def get(self, request):
        return render(request, 'users/profile.html')

    def post(self, request):
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        if email: user.email = email
        user.save()

        from django.contrib import messages
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('profile')