from django.db import models
from django.conf import settings

class StaffRecord(models.Model):
    """
    Core staff model for all employees (Teachers, Admin, Accountants, etc.)
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.profile.role}"

class StaffAttendance(models.Model):
    """
    Tracks daily attendance for staff members.
    """
    staff = models.ForeignKey(StaffRecord, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(auto_now_add=True)
    is_present = models.BooleanField(default=True)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('staff', 'date')

class SalaryHistory(models.Model):
    """
    Tracks payments and salary changes for staff.
    """
    staff = models.ForeignKey(StaffRecord, on_delete=models.CASCADE, related_name='salary_history')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    period = models.CharField(max_length=50) # e.g., 'October 2024'
    transaction_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return f"Salary: {self.staff.user.username} - {self.period}"
