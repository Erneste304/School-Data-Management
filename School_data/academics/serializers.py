from rest_framework import serializers
from .models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, TeacherProfile, Assignment, AssignmentSubmission,
    AcademicTerm, ClassSchedule, Curriculum
)


class ClassSerializer(serializers.ModelSerializer):
    class_tutor_name = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'class_tutor', 'class_tutor_name', 'level', 'student_count']

    def get_class_tutor_name(self, obj):
        return obj.class_tutor.get_full_name() if obj.class_tutor else None

    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()


class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'teacher', 'teacher_name']

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else None


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'user', 'student_id', 'enrollment_date', 'current_class',
            'is_active', 'full_name', 'class_name', 'gpa', 'attendance_rate'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_class_name(self, obj):
        return obj.current_class.name if obj.current_class else None

    def get_gpa(self, obj):
        return obj.calculate_gpa()

    def get_attendance_rate(self, obj):
        return obj.get_attendance_rate()


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'enrolled_class', 'academic_year',
                  'enrollment_date', 'student_name', 'class_name']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_class_name(self, obj):
        return obj.enrolled_class.name


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'score', 'assignment_name',
                  'date_recorded', 'student_name']

    def get_student_name(self, obj):
        return obj.enrollment.student.user.get_full_name()


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'enrollment', 'date', 'status', 'is_late',
                  'lateness_minutes', 'student_name']

    def get_student_name(self, obj):
        return obj.enrollment.student.user.get_full_name()


class AttendanceBulkSerializer(serializers.Serializer):
    """For marking attendance for an entire class at once."""
    class_id = serializers.IntegerField()
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )


class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'name', 'date', 'subject', 'subject_name']

    def get_subject_name(self, obj):
        return obj.subject.name


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    exam_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = ['id', 'enrollment', 'exam', 'score', 'grade',
                  'student_name', 'exam_name']

    def get_student_name(self, obj):
        return obj.enrollment.student.user.get_full_name()

    def get_exam_name(self, obj):
        return obj.exam.name


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'subject', 'title', 'description', 'due_date', 'subject_name']

    def get_subject_name(self, obj):
        return obj.subject.name


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assignment_title = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'enrollment', 'submission_date',
                  'content', 'grade', 'student_name', 'assignment_title']

    def get_student_name(self, obj):
        return obj.enrollment.student.user.get_full_name()

    def get_assignment_title(self, obj):
        return obj.assignment.title


class AcademicTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicTerm
        fields = ['id', 'name', 'start_date', 'end_date']


class ClassScheduleSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'class_assigned', 'subject', 'day_of_week',
            'start_time', 'end_time', 'room', 'term', 'is_active',
            'class_name', 'subject_name', 'teacher_name', 'duration'
        ]

    def get_class_name(self, obj):
        return obj.class_assigned.name

    def get_subject_name(self, obj):
        return obj.subject.name

    def get_teacher_name(self, obj):
        return obj.subject.teacher.get_full_name() if obj.subject.teacher else None

    def get_duration(self, obj):
        return obj.get_duration()


class CurriculumSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Curriculum
        fields = ['id', 'name', 'description', 'subjects']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for the dashboard overview stats."""
    total_students = serializers.IntegerField()
    total_staff = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    total_subjects = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    attendance_today = serializers.DictField(child=serializers.IntegerField())
