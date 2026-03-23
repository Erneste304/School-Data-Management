from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('public-events/', views.public_events_view, name='public_events'),
    path('clubs/', views.club_list_view, name='club_list'),
    path('clubs/create/', views.create_club_view, name='create_club'),
    path('events/<int:pk>/', views.event_detail_view, name='event_detail'),
    path('events/create/', views.create_event_view, name='create_event'),
    path('announcements/', views.announcements_view, name='announcements'),
    path('gallery/', views.gallery_view, name='gallery'),
]
