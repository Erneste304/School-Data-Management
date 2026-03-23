from django.urls import path
app_name = 'discipline'
from . import views

app_name = 'discipline'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('cases/', views.case_list_view, name='case_list'),
    path('cases/create/', views.case_create_view, name='case_create'),
    path('cases/<int:pk>/', views.case_detail_view, name='case_detail'),
    path('cases/<int:pk>/update/', views.case_update_view, name='case_update'),
    path('cases/<int:case_pk>/add-action/', views.add_action_view, name='add_action'),
    path('cases/<int:case_pk>/schedule-hearing/', views.schedule_hearing_view, name='schedule_hearing'),
    path('students/<int:student_id>/record/', views.student_record_view, name='student_record'),
    path('reports/generate/', views.generate_report_view, name='generate_report'),
    path('analytics/', views.analytics_view, name='analytics'),
]
