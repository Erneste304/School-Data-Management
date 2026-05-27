from rest_framework import serializers
from .models import AuditLog, UserActivity


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    change_summary = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'action_display', 'timestamp', 'user',
                  'username', 'user_ip', 'model_name', 'app_name',
                  'object_repr', 'object_id', 'description',
                  'request_path', 'request_method', 'changes',
                  'change_summary']

    def get_username(self, obj):
        return obj.user.get_full_name() if obj.user else 'System'

    def get_change_summary(self, obj):
        return obj.get_change_summary()


class UserActivitySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'username', 'session_key', 'login_time',
                  'logout_time', 'ip_address', 'actions_count', 'last_activity']

    def get_username(self, obj):
        return obj.user.get_full_name()
