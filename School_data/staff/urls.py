from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list_view, name='staff_list'),
    path('create/', views.staff_create_view, name='staff_create'),
    path('toggle/<int:pk>/', views.staff_toggle_status, name='staff_toggle'),
]
