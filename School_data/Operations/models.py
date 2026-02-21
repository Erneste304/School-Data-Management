from django.db import models
from django.conf import settings
from Academics.models import Student

class DisciplineRecord(models.Model):
    """
    Model to track student behavior, managed primarily by the DOS.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discipline_records')
    date = models.DateField(auto_now_add=True)
    description = models.TextField()
    action_taken = models.CharField(max_length=200, help_text="Action taken by DOS or Headteacher")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_discipline_cases')
    managed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_discipline_cases', limit_choices_to={'profile__role': 'DOD'})

    class Meta:
        verbose_name_plural = "Discipline Records"

    def __str__(self):
        return f"Discipline: {self.student.user.get_full_name()} - {self.date}"

class TeacherReport(models.Model):
    """
    Model for teachers to submit academic or operational reports to the DOS.
    """
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_reports')
    dos = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reports', limit_choices_to={'profile__role': 'DOS'})
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report: {self.title} from {self.teacher.get_full_name()}"

class OperationApproval(models.Model):
    """
    Model for Headteacher to approve internal operations between Teacher and DOS.
    """
    headteacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authorized_operations', limit_choices_to={'profile__role': 'HEAD'})
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='operation_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_approved = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='approvals/', blank=True, null=True)
    date_requested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Approval Request: {self.title} status={self.is_approved}"

class AuditLog(models.Model):
    """
    Model to track every sensitive action in the system for transparency and legal protection.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    module = models.CharField(max_length=100) # e.g., 'Finance', 'Academics', 'Discipline'
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
