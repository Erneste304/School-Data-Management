from django import forms
from .models import Club, Event, Announcement, Gallery, Competition, Volunteer

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'acronym', 'description', 'category', 'logo', 'meeting_day', 'meeting_time', 'meeting_venue', 'patron', 'president', 'established_date']
        widgets = {
            'meeting_time': forms.TimeInput(attrs={'type': 'time'}),
            'established_date': forms.DateInput(attrs={'type': 'date'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'start_date', 'end_date', 'venue', 'audience', 'capacity', 'club', 'poster', 'registration_required', 'is_published']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'audience', 'publish_date', 'expiry_date', 'featured_image']
        widgets = {
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'description', 'event']

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'type', 'description', 'start_date', 'end_date', 'venue', 'prizes', 'rules']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['title', 'description', 'location', 'date', 'time_start', 'time_end', 'spots_available', 'contact_person', 'contact_phone']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_start': forms.TimeInput(attrs={'type': 'time'}),
            'time_end': forms.TimeInput(attrs={'type': 'time'}),
        }
