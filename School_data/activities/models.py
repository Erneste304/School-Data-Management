from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from academics.models import Student
from schools.models import Classroom

class Club(models.Model):
    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('arts', 'Arts & Culture'),
        ('technology', 'Technology'),
        ('community', 'Community Service'),
        ('business', 'Business & Entrepreneurship'),
        ('religious', 'Religious'),
        ('other', 'Other'),
    ])
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    meeting_day = models.CharField(max_length=20, blank=True)
    meeting_time = models.TimeField(blank=True, null=True)
    meeting_venue = models.CharField(max_length=200, blank=True)
    patron = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, 
                               related_name='patron_clubs', limit_choices_to={'role__in': ['teacher', 'head_teacher', 'animateur']})
    president = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='president_clubs')
    vice_president = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='vice_president_clubs', blank=True)
    secretary = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='secretary_clubs', blank=True)
    treasurer = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='treasurer_clubs', blank=True)
    is_active = models.BooleanField(default=True)
    established_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}"

class ClubMembership(models.Model):
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('executive', 'Executive Member'),
        ('leader', 'Club Leader'),
    )
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    contributions = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['club', 'student']

class Event(models.Model):
    EVENT_TYPES = (
        ('academic', 'Academic Event'),
        ('sports', 'Sports Event'),
        ('cultural', 'Cultural Event'),
        ('religious', 'Religious Event'),
        ('ceremony', 'Ceremony'),
        ('competition', 'Competition'),
        ('workshop', 'Workshop/Seminar'),
        ('fundraising', 'Fundraising'),
        ('other', 'Other'),
    )
    
    AUDIENCE_CHOICES = (
        ('public', 'Public'),
        ('students', 'Students Only'),
        ('staff', 'Staff Only'),
        ('parents', 'Parents'),
        ('invited', 'Invited Only'),
    )
    
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='public')
    capacity = models.IntegerField(default=0)
    organizer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    is_livestream = models.BooleanField(default=False)
    livestream_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attendance_marked = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['event', 'student', 'staff']

class Announcement(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    audience = models.CharField(max_length=20, choices=Event.AUDIENCE_CHOICES, default='public')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    featured_image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    attachment = models.FileField(upload_to='announcement_attachments/', blank=True, null=True)
    
    class Meta:
        ordering = ['-publish_date']

class Gallery(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Galleries"
        ordering = ['-created_at']

class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery_images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Competition(models.Model):
    COMPETITION_TYPES = (
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('arts', 'Arts'),
        ('debate', 'Debate'),
        ('science', 'Science Fair'),
        ('music', 'Music'),
        ('drama', 'Drama'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=COMPETITION_TYPES)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    prizes = models.TextField(blank=True)
    rules = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']

class CompetitionParticipant(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    class Meta:
        unique_together = ['competition', 'student']

class Volunteer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    spots_available = models.IntegerField()
    spots_taken = models.IntegerField(default=0)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']

class VolunteerSignup(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    signup_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    hours_completed = models.FloatField(default=0)
    
    class Meta:
        unique_together = ['volunteer', 'student']
