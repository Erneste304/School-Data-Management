from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'title', 'message', 'notification_type', 'is_read', 'created_at', 'action_url', 'icon']
        read_only_fields = ['recipient', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'user', 'email_enabled', 'sms_enabled', 'in_app_enabled',
                  'academic_notifications', 'financial_notifications', 'discipline_notifications',
                  'event_notifications', 'system_notifications', 'digest_frequency']
        read_only_fields = ['user']
