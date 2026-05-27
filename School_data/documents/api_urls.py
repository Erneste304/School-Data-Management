from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import DocumentViewSet, DocumentCategoryViewSet

app_name = 'documents_api'

router = DefaultRouter()
router.register(r'files', DocumentViewSet, basename='document')
router.register(r'categories', DocumentCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
