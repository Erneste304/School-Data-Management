from django.urls import path
from .views import (
    CustomLoginView,
    DashboardHomeView, 
    AdminDashboardView, 
    TeacherDashboardView, 
    StudentDashboardView, 
    AccountantDashboardView, 
    ParentDashboardView,
    DOSDashboardView,
    HeadteacherDashboardView,
    DODDashboardView
    )

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('admin-panel/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('teacher-portal/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('student-portal/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('accountant-portal/', AccountantDashboardView.as_view(), name='accountant_dashboard'),
    path('parent-portal/', ParentDashboardView.as_view(), name='parent_dashboard'),
    path('head-portal/', HeadteacherDashboardView.as_view(), name='headteacher_dashboard'),
    path('dod-portal/', DODDashboardView.as_view(), name='dod_dashboard'),
    path('dos-portal/', DOSDashboardView.as_view(), name='dos_dashboard'),
    path('', DashboardHomeView.as_view(), name='dashboard_home'),

]