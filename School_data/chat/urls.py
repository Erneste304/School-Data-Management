from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('room/<slug:slug>/', views.chat_room_view, name='room_detail'),
    path('api/messages/<slug:slug>/', views.get_messages_api, name='messages_api'),
    path('api/unread-counts/', views.get_unread_counts, name='unread_counts'),
    path('api/room/<int:room_id>/read/', views.mark_room_read, name='mark_room_read'),
    path('api/search/', views.search_messages, name='search_messages'),
]
