from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    Club, ClubMembership, Event, EventRegistration,
    Announcement, Gallery, Competition, Volunteer, VolunteerSignup
)
from academics.models import Student
from accounts.views import role_required
from .forms import (
    ClubForm, EventForm, AnnouncementForm, GalleryForm,
    CompetitionForm, VolunteerForm
)

@login_required
@role_required(['head_teacher', 'animateur', 'admin'])
def dashboard_view(request):
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_published=True).order_by('start_date')[:5]
    active_clubs = Club.objects.filter(is_active=True).annotate(member_count=Count('memberships'))[:6]
    recent_announcements = Announcement.objects.filter(is_published=True).order_by('-publish_date')[:5]
    context = {
        'upcoming_events': upcoming_events,
        'active_clubs': active_clubs,
        'recent_announcements': recent_announcements,
        'total_events': Event.objects.count(),
        'total_clubs': Club.objects.count(),
        'total_volunteers': Volunteer.objects.count(),
    }
    return render(request, 'activities/dashboard.html', context)

@login_required
def public_events_view(request):
    events = Event.objects.filter(start_date__gte=timezone.now(), is_published=True, audience__in=['public', 'students']).order_by('start_date')
    return render(request, 'activities/public_events.html', {'events': events})

@login_required
@role_required(['head_teacher', 'animateur', 'admin'])
def club_list_view(request):
    clubs = Club.objects.all().annotate(member_count=Count('memberships'))
    return render(request, 'activities/club_list.html', {'clubs': clubs})

@login_required
@role_required(['head_teacher', 'animateur', 'admin'])
def create_club_view(request):
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save()
            messages.success(request, f'Club "{club.name}" created successfully!')
            return redirect('activities:club_list')
    else:
        form = ClubForm()
    return render(request, 'activities/club_form.html', {'form': form})

@login_required
def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    return render(request, 'activities/event_detail.html', {'event': event})

@login_required
@role_required(['head_teacher', 'animateur', 'admin'])
def create_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('activities:dashboard')
    else:
        form = EventForm()
    return render(request, 'activities/event_form.html', {'form': form})

@login_required
def announcements_view(request):
    announcements = Announcement.objects.filter(is_published=True).order_by('-publish_date')
    return render(request, 'activities/announcements.html', {'announcements': announcements})

@login_required
def gallery_view(request):
    galleries = Gallery.objects.all().order_by('-created_at')
    return render(request, 'activities/gallery.html', {'galleries': galleries})
