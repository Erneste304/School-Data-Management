from django.db import models
from accounts.models import CustomUser

class ChatRoom(models.Model):
    ROOM_TYPES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('group', 'Group'),
        ('staff', 'Staff Only'),
        ('class', 'Class Room'),
    )
    
    name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='public')
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    members = models.ManyToManyField(CustomUser, related_name='chat_rooms', blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='chat_avatars/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.room_type})"

class Message(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('system', 'System')
    )
    
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.sender.username}: {self.content[:50]}'

class ParticipantStatus(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    last_read = models.DateTimeField(null=True, blank=True)
    typing_status = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['room', 'user']

class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_attachments/')
    file_name = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class MessageReaction(models.Model):
    message = models.ForeignKey(Message, related_name='reactions_list', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ['message', 'user', 'reaction']
