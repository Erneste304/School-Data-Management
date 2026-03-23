from rest_framework import serializers
from .models import ChatRoom, Message
from accounts.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'role', 'profile_picture']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    timestamp_formatted = serializers.DateTimeField(source='timestamp', format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'timestamp_formatted', 
                  'is_read', 'message_type', 'reply_to', 'is_edited', 'is_deleted']

class ChatRoomSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_type', 'slug', 'description', 'members_count']
        
    def get_members_count(self):
        return self.members.count()
