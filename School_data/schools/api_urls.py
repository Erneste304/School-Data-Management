from django.urls import path
from . import api_views

app_name = 'schools_api'

urlpatterns = [
    path('levels/', api_views.level_list, name='level-list'),
    path('years/', api_views.academic_year_list, name='year-list'),
    path('terms/', api_views.term_list, name='term-list'),
    path('classrooms/', api_views.classroom_list, name='classroom-list'),
]
