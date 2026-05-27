from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ClubViewSet, EventViewSet, AnnouncementViewSet

app_name = 'activities_api'

router = DefaultRouter()
router.register(r'clubs', ClubViewSet)
router.register(r'events', EventViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
