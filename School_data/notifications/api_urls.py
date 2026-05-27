from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import NotificationViewSet, NotificationPreferenceViewSet

app_name = 'notifications_api'

router = DefaultRouter()
router.register(r'list', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='preference')

urlpatterns = [
    path('', include(router.urls)),
]
