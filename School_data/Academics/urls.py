from django.urls import path
from .views import (
    AdminAcademicsDashboardView, 
    TeacherPortalView,
    ParentPortalView,
    StudentPortalView,
)

urlpatterns = [
    # Admin/Headteacher Academic Management
    path('admin-mgmt/', AdminAcademicsDashboardView.as_view(), name='admin_academics_dashboard'),
    
    # Teacher Views 
    path('teacher-portal/', TeacherPortalView.as_view(), name='teacher_dashboard'),
    
    # Student Views
    path('student-portal/', StudentPortalView.as_view(), name='student_dashboard'),

    # Parent Views 
    path('parent-portal/', ParentPortalView.as_view(), name='parent_dashboard'),
]