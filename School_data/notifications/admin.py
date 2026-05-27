from django.contrib import admin
from .models import (
    Notification, EmailNotification, SMSNotification,
    NotificationPreference, NotificationTemplate, PushNotification
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['created_at']


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient', 'status', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['subject', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['sent_at']


@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'recipient', 'status', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['phone_number', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['sent_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'in_app_enabled', 'digest_frequency']
    list_filter = ['email_enabled', 'sms_enabled', 'in_app_enabled', 'digest_frequency']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'category', 'is_active']
    list_filter = ['notification_type', 'category', 'is_active']
    search_fields = ['name', 'subject_template']


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'platform', 'status', 'sent_at']
    list_filter = ['platform', 'status', 'sent_at']
    search_fields = ['title', 'recipient__first_name', 'recipient__last_name']
    readonly_fields = ['sent_at']
