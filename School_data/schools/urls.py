from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    path('info/', views.school_info_view, name='info'),
]
