from django.db import models
from django.conf import settings
from Academics.models import Class


class Announcement(models.Model):
    """
    Represents a school-wide, role-specific, or class-specific announcement.
    """
    SCOPE_CHOICES = [
        ('GLOBAL', 'All Users'),
        ('ADMIN', 'Admins'),
        ('HEAD', 'Headteachers'),
        ('TEACHER', 'Teachers'),
        ('STUDENT', 'Students'),
        ('PARENT', 'Parents'),
        ('ACCOUNTANT', 'Accountants'),
        ('CLASS', 'Specific Class'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='GLOBAL')
    target_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        permissions = [
            ("can_create_announcement", "Can create announcements"),
        ]

    def __str__(self):
        return self.title

class Message(models.Model):
    """
    Represents a direct message between two users.
    """
    CATEGORY_CHOICES = [
        ('MONEY', 'Money / Fees (Accountant)'),
        ('STUDY', 'Study / Academics (DOS)'),
        ('DISCIPLINE', 'Discipline / Behavior (DOD)'),
        ('GENERAL', 'Public / General (Headteacher)'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='GENERAL')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.receiver:
            # Smart Routing Logic
            role_map = {
                'MONEY': 'ACCOUNTANT',
                'STUDY': 'DOS',
                'DISCIPLINE': 'DOD',
                'GENERAL': 'HEAD',
            }
            target_role = role_map.get(self.category)
            # Find the first user with this role
            from Users.models import Profile
            profile = Profile.objects.filter(role=target_role).first()
            if profile:
                self.receiver = profile.user
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.sent_at}"