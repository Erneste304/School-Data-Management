from rest_framework import serializers
from .models import CustomUser, StaffProfile


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StaffProfile
        fields = ['employee_id', 'department', 'qualification', 'date_joined']


class UserSerializer(serializers.ModelSerializer):
    profile    = StaffProfileSerializer(read_only=True)
    full_name  = serializers.SerializerMethodField()
    role_label = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model  = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'full_name', 'role', 'role_label', 'phone', 'is_active',
                  'created_at', 'profile']
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user