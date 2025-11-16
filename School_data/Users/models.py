from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = [
    ('ADMIN', 'Admin'),
    ('STUDENT', 'Student'),
    ('TEACHER', 'Teacher'),
    ('PARENT', 'Parent'),
    ('HEAD', 'Headmaster'),
    ('ACCOUNTANT', 'Accountant')
    ]

# Create your models here.
class CustomUser(AbstractUser):

    pass # no new fields needed in base user

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='STUDENT')

    invitation_token = models.UUIDField(default=uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def get_role_display(self):
        return dict(ROLE_CHOICES).get(self.role, self.role)