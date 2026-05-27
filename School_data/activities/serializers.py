from rest_framework import serializers
from .models import Club, ClubMembership, Event, EventRegistration, Announcement


class ClubSerializer(serializers.ModelSerializer):
    patron_name = serializers.CharField(source='patron.get_full_name', read_only=True)

    class Meta:
        model = Club
        fields = ['id', 'name', 'acronym', 'description', 'category', 'meeting_day',
                  'meeting_time', 'meeting_venue', 'patron', 'patron_name', 'is_active',
                  'established_date']


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    audience_display = serializers.CharField(source='get_audience_display', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'event_type', 'event_type_display', 'description',
                  'start_date', 'end_date', 'venue', 'audience', 'audience_display',
                  'capacity', 'organizer', 'organizer_name', 'registration_required',
                  'registration_deadline', 'is_published', 'is_livestream', 'livestream_url']


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'priority', 'priority_display', 'audience',
                  'created_by', 'created_by_name', 'publish_date', 'expiry_date', 'is_published']
