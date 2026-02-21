from django.urls import path
from .views import (
    AnnouncementListView, 
    AnnouncementCreateView, 
    MessageInboxView, 
    MessageDetailView,
    PrivacyPolicyView,
    TermsOfServiceView,
    HelpCenterView
)

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/new/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('inbox/', MessageInboxView.as_view(), name='message_inbox'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms_of_service'),
    path('help-center/', HelpCenterView.as_view(), name='help_center'),
]