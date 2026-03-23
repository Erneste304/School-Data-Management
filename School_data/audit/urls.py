from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_dashboard_view, name='dashboard'),
    path('logs/', views.log_list_view, name='log_list'),
    path('logs/<int:pk>/', views.log_detail_view, name='log_detail'),
    path('activity/', views.user_activity_view, name='user_activity'),
]
