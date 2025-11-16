from django.db import models
from django.conf import settings


class Class(models.Model):
    """Represents an academic class, e.g., 'Grade 10A'."""
    name = models.CharField(max_length=100, unique=True)
    class_tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tutored_class'
    )

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name


class Student(models.Model):
    """
    Stores academic-specific information for a user with the 'STUDENT' role.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class Subject(models.Model):
    """Represents a subject, e.g., 'Mathematics'."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects_taught'
    )

    def __str__(self):
        return f"{self.name} ({self.code})"


class Enrollment(models.Model):
    """Links a student to a specific class for an academic year or term."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9, help_text="e.g., '2024-2025'")
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'enrolled_class', 'academic_year')

    def __str__(self):
        return f"{self.student} enrolled in {self.enrolled_class} for {self.academic_year}"