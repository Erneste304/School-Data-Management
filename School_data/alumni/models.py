from django.db import models
from django.conf import settings
from accounts.models import CustomUser


class AlumniProfile(models.Model):
    """Profile for alumni/graduates"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alumni_profile')
    graduation_year = models.IntegerField()
    graduation_class = models.CharField(max_length=100)
    current_occupation = models.CharField(max_length=200, blank=True)
    current_employer = models.CharField(max_length=200, blank=True)
    current_location = models.CharField(max_length=200, blank=True)
    linkedin_profile = models.URLField(blank=True)
    website = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    is_willing_to_mentor = models.BooleanField(default=False)
    is_willing_to_speak = models.BooleanField(default=False)
    is_willing_to_donate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Alumni Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} - Class of {self.graduation_year}"


class AlumniEvent(models.Model):
    """Events for alumni networking and engagement"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('Reunion', 'Reunion'),
            ('Networking', 'Networking'),
            ('Career Fair', 'Career Fair'),
            ('Fundraising', 'Fundraising'),
            ('Speaker Series', 'Speaker Series'),
            ('Other', 'Other'),
        ],
        default='Networking'
    )
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Alumni Events"

    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%Y-%m-%d')}"


class AlumniEventRegistration(models.Model):
    """Registration for alumni events"""
    event = models.ForeignKey(AlumniEvent, on_delete=models.CASCADE, related_name='registrations')
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('event', 'alumni')
        verbose_name_plural = "Alumni Event Registrations"

    def __str__(self):
        return f"{self.alumni.user.get_full_name()} - {self.event.title}"


class AlumniDonation(models.Model):
    """Track donations from alumni"""
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    donation_date = models.DateTimeField(auto_now_add=True)
    donation_purpose = models.CharField(max_length=200, blank=True)
    is_anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    receipt_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Alumni Donations"

    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous - RWF {self.amount}"
        return f"{self.alumni.user.get_full_name()} - RWF {self.amount}"


class AlumniMentorship(models.Model):
    """Mentorship program connecting alumni with current students"""
    mentor = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='mentorships')
    student = models.ForeignKey('academics.Student', on_delete=models.CASCADE, related_name='mentors')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Active', 'Active'),
            ('Completed', 'Completed'),
            ('Paused', 'Paused'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Active'
    )
    mentorship_area = models.CharField(max_length=200, help_text="e.g., Career guidance, Academic support")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mentor', 'student')
        verbose_name_plural = "Alumni Mentorships"

    def __str__(self):
        return f"{self.mentor.user.get_full_name()} mentoring {self.student.user.get_full_name()}"


class AlumniJobPosting(models.Model):
    """Job postings shared by alumni for current students"""
    posted_by = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(
        max_length=50,
        choices=[
            ('Full-time', 'Full-time'),
            ('Part-time', 'Part-time'),
            ('Internship', 'Internship'),
            ('Contract', 'Contract'),
            ('Remote', 'Remote'),
        ],
        default='Full-time'
    )
    description = models.TextField()
    requirements = models.TextField(blank=True)
    application_link = models.URLField(blank=True)
    application_email = models.EmailField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    posted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Alumni Job Postings"

    def __str__(self):
        return f"{self.title} at {self.company}"
