from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AuditLogViewSet, UserActivityViewSet, audit_stats

app_name = 'audit_api'

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet)
router.register(r'activities', UserActivityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', audit_stats, name='audit_stats'),
]
