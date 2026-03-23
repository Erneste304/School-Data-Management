from django.urls import path
from . import views

app_name = 'livestream'

urlpatterns = [
    path('', views.stream_list_view, name='list'),
    path('<int:pk>/', views.live_stream_view, name='watch'),
    path('manage/', views.manage_streams_view, name='manage'),
    path('create/', views.create_stream_view, name='create'),
]
