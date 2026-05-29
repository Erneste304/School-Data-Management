from django.urls import path
from . import views

app_name = 'chat_api'

urlpatterns = [
    path('rooms/', views.rooms_list_api, name='rooms_list_api'),
    path('rooms/<slug:slug>/send/', views.send_message_api, name='send_message_api'),
    path('rooms/<slug:slug>/messages/', views.get_messages_api, name='get_messages_api'),
    path('unread-counts/', views.get_unread_counts, name='get_unread_counts'),
    path('rooms/<int:room_id>/mark-read/', views.mark_room_read, name='mark_room_read'),
    path('search/', views.search_messages, name='search_messages'),
]
