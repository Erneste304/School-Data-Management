from django.db import models
from django.conf import settings
from users.models import Class


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