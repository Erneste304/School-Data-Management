from django.contrib import admin
from .models import (
    Club, ClubMembership, Event, EventRegistration, 
    Announcement, Gallery, GalleryImage, Competition, 
    CompetitionParticipant, Volunteer, VolunteerSignup
)

class ClubMembershipInline(admin.TabularInline):
    model = ClubMembership
    extra = 1

class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'patron', 'is_active']
    list_filter = ['category', 'is_active']
    inlines = [ClubMembershipInline]

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 1

class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'venue', 'is_published']
    list_filter = ['event_type', 'audience', 'is_published', 'start_date']
    inlines = [EventRegistrationInline]

admin.site.register(Club, ClubAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Announcement)
admin.site.register(Gallery)
admin.site.register(Competition)
admin.site.register(Volunteer)
