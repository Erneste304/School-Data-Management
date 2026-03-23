from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from academics.models import Student
from schools.models import Classroom, AcademicYear

class DisciplineCategory(models.Model):
    """Categories of discipline issues"""
    SEVERITY_CHOICES = (
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    default_action = models.CharField(max_length=200, blank=True)
    points = models.IntegerField(default=0)  # Points for demerit system
    
    class Meta:
        verbose_name_plural = "Discipline Categories"
        ordering = ['severity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"

class DisciplineCase(models.Model):
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('appealed', 'Under Appeal'),
        ('closed', 'Closed'),
    )
    
    # Basic Info
    case_number = models.CharField(max_length=20, unique=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discipline_cases')
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='reported_cases')
    category = models.ForeignKey(DisciplineCategory, on_delete=models.SET_NULL, null=True)
    
    # Details
    incident_date = models.DateTimeField()
    incident_location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    evidence = models.FileField(upload_to='discipline_evidence/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, 
                                    related_name='assigned_cases', limit_choices_to={'role': 'dod'})
    
    # Timeline
    reported_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    resolved_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-reported_date']
        permissions = [
            ('can_investigate_case', 'Can investigate discipline cases'),
            ('can_resolve_case', 'Can resolve discipline cases'),
            ('can_appeal_case', 'Can appeal discipline cases'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.case_number:
            # Generate case number: DC + year + sequence
            import random
            year = timezone.now().year
            self.case_number = f"DC{year}{random.randint(1000, 9999)}"
        if self.status == 'closed' and not self.resolved_date:
            self.resolved_date = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.case_number} - {self.student.full_name} - {self.get_status_display()}"

class DisciplineAction(models.Model):
    """Actions taken for discipline cases"""
    ACTION_CHOICES = (
        ('warning', 'Verbal Warning'),
        ('written_warning', 'Written Warning'),
        ('community_service', 'Community Service'),
        ('suspension', 'Suspension'),
        ('expulsion', 'Expulsion'),
        ('counseling', 'Counseling Session'),
        ('parent_meeting', 'Parent Meeting'),
        ('other', 'Other'),
    )
    
    case = models.ForeignKey(DisciplineCase, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    taken_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='taken_actions')
    date_taken = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_taken']
    
    def __str__(self):
        return f"{self.case.case_number} - {self.get_action_type_display()}"

class DisciplineHearing(models.Model):
    """Hearings for serious discipline cases"""
    case = models.OneToOneField(DisciplineCase, on_delete=models.CASCADE, related_name='hearing')
    hearing_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    chairperson = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, 
                                     related_name='chaired_hearings')
    committee_members = models.ManyToManyField(CustomUser, related_name='hearing_members')
    parent_present = models.BooleanField(default=False)
    parent_name = models.CharField(max_length=200, blank=True)
    parent_comment = models.TextField(blank=True)
    student_statement = models.TextField(blank=True)
    findings = models.TextField()
    recommendations = models.TextField()
    decision = models.TextField()
    decision_date = models.DateTimeField(auto_now_add=True)
    is_appealed = models.BooleanField(default=False)
    appeal_reason = models.TextField(blank=True)
    appeal_decision = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-hearing_date']
    
    def __str__(self):
        return f"Hearing for {self.case.case_number}"

class DisciplineRecord(models.Model):
    """Cumulative discipline record for students"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='discipline_record')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    total_cases = models.IntegerField(default=0)
    major_cases = models.IntegerField(default=0)
    minor_cases = models.IntegerField(default=0)
    last_incident_date = models.DateTimeField(blank=True, null=True)
    is_on_probation = models.BooleanField(default=False)
    probation_end_date = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'academic_year']
        ordering = ['-academic_year', 'student']
    
    def update_points(self):
        """Recalculate total points from cases"""
        cases = DisciplineCase.objects.filter(
            student=self.student,
            reported_date__year=self.academic_year.start_date.year,
            status='closed'
        )
        
        total_points = 0
        major = 0
        minor = 0
        
        for case in cases:
            if case.category:
                total_points += case.category.points
                if case.category.severity in ['major', 'critical']:
                    major += 1
                else:
                    minor += 1
        
        self.total_points = total_points
        self.major_cases = major
        self.minor_cases = minor
        self.total_cases = cases.count()
        
        # Auto-set probation if points exceed threshold
        if total_points >= 50 and not self.is_on_probation:
            self.is_on_probation = True
            from django.utils import timezone
            from datetime import timedelta
            self.probation_end_date = timezone.now() + timedelta(days=90)
        elif total_points < 50 and self.is_on_probation:
            self.is_on_probation = False
            self.probation_end_date = None
        
        self.save()
    
    def __str__(self):
        return f"{self.student.full_name} - {self.academic_year}: {self.total_points} points"

class IncidentReport(models.Model):
    """Daily/weekly incident reports for DOD"""
    title = models.CharField(max_length=200)
    report_date = models.DateField()
    period = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    cases_included = models.ManyToManyField(DisciplineCase, blank=True)
    summary = models.TextField()
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
    
    def __str__(self):
        return f"{self.title} - {self.report_date}"
