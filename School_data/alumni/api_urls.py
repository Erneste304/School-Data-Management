from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AlumniProfileViewSet, AlumniEventViewSet,
    AlumniJobPostingViewSet, AlumniDonationViewSet
)

app_name = 'alumni_api'

router = DefaultRouter()
router.register(r'profiles', AlumniProfileViewSet)
router.register(r'events', AlumniEventViewSet)
router.register(r'jobs', AlumniJobPostingViewSet)
router.register(r'donations', AlumniDonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
