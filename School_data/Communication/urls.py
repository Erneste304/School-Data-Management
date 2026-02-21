from django.urls import path
from .views import (
    AnnouncementListView, 
    AnnouncementCreateView, 
    MessageInboxView, 
    MessageDetailView
)

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/new/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('inbox/', MessageInboxView.as_view(), name='message_inbox'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
]