from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from activities.models import Event

class Stream(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=200)
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='stream', null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    stream_key = models.CharField(max_length=100, unique=True, blank=True)
    stream_url = models.URLField(blank=True, null=True)
    hls_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='stream_thumbnails/', blank=True, null=True)
    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-scheduled_start']
    
    def save(self, *args, **kwargs):
        if not self.stream_key:
            import uuid
            self.stream_key = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class StreamSetting(models.Model):
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name='settings')
    enable_chat = models.BooleanField(default=True)
    enable_qa = models.BooleanField(default=True)
    record_stream = models.BooleanField(default=True)
    resolution = models.CharField(max_length=20, default='1080p')
    bitrate = models.IntegerField(default=4000) # in kbps

class ViewerStat(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='viewer_stats')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0) # in seconds

class StreamArchive(models.Model):
    stream = models.OneToOneField(Stream, on_delete=models.CASCADE, related_name='archive')
    video_file = models.FileField(upload_to='stream_archives/')
    duration = models.DurationField()
    size = models.BigIntegerField() # in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Archive of {self.stream.title}"
