from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Staff URLs
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:pk>/toggle/', views.staff_toggle_access, name='staff_toggle'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    
    # Student URLs
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    
    # Parent URLs
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/create/', views.parent_create, name='parent_create'),
    path('parents/<int:pk>/', views.parent_detail, name='parent_detail'),
    path('parents/link/', views.link_parent_student, name='parent_link'),
    
    # Student dashboard URLs
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    
    # Teacher dashboard URLs
    path('teacher/subjects/', views.teacher_subjects, name='teacher_subjects'),
    path('teacher/grades/', views.teacher_grades, name='teacher_grades'),
    path('teacher/attendance/', views.teacher_attendance, name='teacher_attendance'),
    
    # Parent dashboard URLs
    path('parent/children/', views.parent_children, name='parent_children'),
    path('parent/grades/', views.parent_grades, name='parent_grades'),
    path('parent/attendance/', views.parent_attendance, name='parent_attendance'),
    
    # User profile URLs
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.password_change, name='password_change'),
]
