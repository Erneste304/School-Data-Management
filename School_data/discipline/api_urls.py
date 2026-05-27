from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    DisciplineCategoryViewSet, DisciplineCaseViewSet,
    DisciplineActionViewSet, discipline_summary
)

app_name = 'discipline_api'

router = DefaultRouter()
router.register(r'categories', DisciplineCategoryViewSet)
router.register(r'cases', DisciplineCaseViewSet)
router.register(r'actions', DisciplineActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', discipline_summary, name='discipline_summary'),
]
