from django.contrib import admin
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration,
    AlumniDonation, AlumniMentorship, AlumniJobPosting
)


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'graduation_year', 'graduation_class', 'current_occupation', 'current_location']
    list_filter = ['graduation_year', 'is_willing_to_mentor', 'is_willing_to_speak', 'is_willing_to_donate']
    search_fields = ['user__first_name', 'user__last_name', 'graduation_class', 'current_occupation']


@admin.register(AlumniEvent)
class AlumniEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'location', 'event_type', 'registration_deadline']
    list_filter = ['event_type', 'event_date']
    search_fields = ['title', 'location']


@admin.register(AlumniEventRegistration)
class AlumniEventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'alumni', 'registration_date', 'attended']
    list_filter = ['attended', 'event']
    search_fields = ['alumni__user__first_name', 'event__title']


@admin.register(AlumniDonation)
class AlumniDonationAdmin(admin.ModelAdmin):
    list_display = ['alumni', 'amount', 'donation_date', 'donation_purpose', 'is_anonymous']
    list_filter = ['is_anonymous', 'donation_date']
    search_fields = ['alumni__user__first_name', 'donation_purpose']


@admin.register(AlumniMentorship)
class AlumniMentorshipAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'student', 'start_date', 'end_date', 'status', 'mentorship_area']
    list_filter = ['status', 'start_date']
    search_fields = ['mentor__user__first_name', 'student__user__first_name']


@admin.register(AlumniJobPosting)
class AlumniJobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'job_type', 'deadline', 'is_active']
    list_filter = ['job_type', 'is_active', 'posted_date']
    search_fields = ['title', 'company', 'location']
