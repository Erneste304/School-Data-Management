from rest_framework import serializers
from .models import AlumniProfile, AlumniEvent, AlumniJobPosting, AlumniDonation


class AlumniProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = AlumniProfile
        fields = ['id', 'user', 'full_name', 'graduation_year', 'graduation_class',
                  'current_occupation', 'current_employer', 'current_location',
                  'linkedin_profile', 'bio', 'is_willing_to_mentor',
                  'is_willing_to_speak', 'is_willing_to_donate']
        read_only_fields = ['user']


class AlumniEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniEvent
        fields = ['id', 'title', 'description', 'event_date', 'location',
                  'event_type', 'max_attendees', 'registration_deadline']


class AlumniJobPostingSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.user.get_full_name', read_only=True)

    class Meta:
        model = AlumniJobPosting
        fields = ['id', 'posted_by', 'posted_by_name', 'title', 'company', 'location',
                  'job_type', 'description', 'requirements', 'application_link',
                  'application_email', 'deadline', 'is_active', 'posted_date']
        read_only_fields = ['posted_by', 'posted_date']


class AlumniDonationSerializer(serializers.ModelSerializer):
    alumni_name = serializers.SerializerMethodField()

    class Meta:
        model = AlumniDonation
        fields = ['id', 'alumni', 'alumni_name', 'amount', 'donation_date',
                  'donation_purpose', 'is_anonymous', 'message', 'payment_method']
        read_only_fields = ['alumni', 'donation_date']

    def get_alumni_name(self, obj):
        if obj.is_anonymous:
            return 'Anonymous'
        return obj.alumni.user.get_full_name()
