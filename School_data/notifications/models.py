from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Base notification model for in-app notifications"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('Info', 'Info'),
            ('Success', 'Success'),
            ('Warning', 'Warning'),
            ('Error', 'Error'),
            ('Academic', 'Academic'),
            ('Financial', 'Financial'),
            ('Discipline', 'Discipline'),
            ('Event', 'Event'),
            ('System', 'System'),
        ],
        default='Info'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"


class EmailNotification(models.Model):
    """Email notification tracking"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_notifications')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Sent', 'Sent'),
            ('Failed', 'Failed'),
        ],
        default='Pending'
    )
    error_message = models.TextField(blank=True)
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name='emails')

    class Meta:
        verbose_name_plural = "Email Notifications"
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient.get_full_name()}"


class SMSNotification(models.Model):
    """SMS notification tracking"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sms_notifications')
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Sent', 'Sent'),
            ('Failed', 'Failed'),
            ('Delivered', 'Delivered'),
        ],
        default='Pending'
    )
    error_message = models.TextField(blank=True)
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_messages')

    class Meta:
        verbose_name_plural = "SMS Notifications"
        ordering = ['-sent_at']

    def __str__(self):
        return f"SMS to {self.phone_number} - {self.recipient.get_full_name()}"


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)
    academic_notifications = models.BooleanField(default=True)
    financial_notifications = models.BooleanField(default=True)
    discipline_notifications = models.BooleanField(default=True)
    event_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    digest_frequency = models.CharField(
        max_length=50,
        choices=[
            ('Immediate', 'Immediate'),
            ('Daily', 'Daily'),
            ('Weekly', 'Weekly'),
        ],
        default='Immediate'
    )
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"


class NotificationTemplate(models.Model):
    """Reusable notification templates"""
    name = models.CharField(max_length=100, unique=True)
    subject_template = models.CharField(max_length=200, blank=True)
    body_template = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('Email', 'Email'),
            ('SMS', 'SMS'),
            ('In-App', 'In-App'),
        ],
        default='In-App'
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('Academic', 'Academic'),
            ('Financial', 'Financial'),
            ('Discipline', 'Discipline'),
            ('Event', 'Event'),
            ('System', 'System'),
        ],
        default='System'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Notification Templates"

    def __str__(self):
        return self.name


class PushNotification(models.Model):
    """Push notification for mobile devices"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_notifications')
    title = models.CharField(max_length=200)
    body = models.TextField()
    device_token = models.CharField(max_length=255)
    platform = models.CharField(
        max_length=50,
        choices=[
            ('iOS', 'iOS'),
            ('Android', 'Android'),
            ('Web', 'Web'),
        ],
        default='Web'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Sent', 'Sent'),
            ('Failed', 'Failed'),
            ('Delivered', 'Delivered'),
        ],
        default='Pending'
    )
    error_message = models.TextField(blank=True)
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name='push_notifications')

    class Meta:
        verbose_name_plural = "Push Notifications"
        ordering = ['-sent_at']

    def __str__(self):
        return f"Push to {self.platform} - {self.recipient.get_full_name()}"
