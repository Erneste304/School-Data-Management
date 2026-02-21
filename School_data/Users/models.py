from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = [
    ('ADMIN', 'Admin'),
    ('STUDENT', 'Student'),
    ('TEACHER', 'Teacher'),
    ('PARENT', 'Parent'),
    ('HEAD', 'Headmaster'),
    ('ACCOUNTANT', 'Accountant'),
    ('DOS', 'Dean of Study'),
    ('DOD', 'Director of Discipline'),
]

LEVEL_CHOICES = [
    ('NURSERY', 'Nursery'),
    ('PRIMARY', 'Primary'),
    ('SECONDARY', 'Secondary'),
]

# Create your models here.
class CustomUser(AbstractUser):

    pass # no new fields needed in base user

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='STUDENT')
    school_type = models.CharField(
        max_length=15, 
        choices=LEVEL_CHOICES, 
        blank=True, 
        null=True,
        help_text="For teachers, select their primary level."
    )
# for teacher and accountant approval workflow
    invitation_token = models.UUIDField(default=uuid4, editable=False, unique=True)
    is_approved = models.BooleanField(default=False)
# for student
    
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
# for parent link to student
    related_student = models.ForeignKey(
        'Academics.Student',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    def get_role_display(self):
        return dict(ROLE_CHOICES).get(self.role, self.role)