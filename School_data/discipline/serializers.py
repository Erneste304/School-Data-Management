from rest_framework import serializers
from .models import DisciplineCategory, DisciplineCase, DisciplineAction


class DisciplineCategorySerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = DisciplineCategory
        fields = ['id', 'name', 'description', 'severity', 'severity_display',
                  'default_action', 'points']


class DisciplineActionSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_type_display', read_only=True)
    taken_by_name = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineAction
        fields = ['id', 'case', 'action_type', 'action_display', 'description',
                  'taken_by', 'taken_by_name', 'date_taken', 'due_date',
                  'is_completed', 'completed_date', 'notes']

    def get_taken_by_name(self, obj):
        return obj.taken_by.get_full_name() if obj.taken_by else 'N/A'


class DisciplineCaseSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    reporter_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    severity = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    actions = DisciplineActionSerializer(many=True, read_only=True)

    class Meta:
        model = DisciplineCase
        fields = ['id', 'case_number', 'student', 'student_name',
                  'reported_by', 'reporter_name', 'category', 'category_name',
                  'severity', 'incident_date', 'incident_location', 'description',
                  'status', 'status_display', 'assigned_to',
                  'reported_date', 'last_updated', 'resolved_date', 'actions']
        read_only_fields = ['case_number', 'reported_date', 'last_updated']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_reporter_name(self, obj):
        return obj.reported_by.get_full_name() if obj.reported_by else 'N/A'

    def get_category_name(self, obj):
        return obj.category.name if obj.category else 'Uncategorized'

    def get_severity(self, obj):
        return obj.category.get_severity_display() if obj.category else 'N/A'
