from django.urls import path
from . import views

app_name = 'livestream_api'

urlpatterns = [
    path('streams/', views.streams_list_api, name='streams_list_api'),
]
