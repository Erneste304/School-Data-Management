from rest_framework import serializers
from .models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, TeacherProfile, Assignment, AssignmentSubmission,
    AcademicTerm, ClassSchedule, Curriculum, StudentEnrollmentRequest,
    LessonPlan, Quiz, Question, QuestionOption, QuizResult
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
    is_past_deadline = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'subject', 'title', 'description', 'due_date', 'max_points',
            'allow_late_submission', 'created_at', 'updated_at',
            'subject_name', 'is_past_deadline', 'submission_count'
        ]

    def get_subject_name(self, obj):
        return obj.subject.name

    def get_is_past_deadline(self, obj):
        return obj.is_past_deadline()

    def get_submission_count(self, obj):
        return obj.submissions.count()


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assignment_title = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'enrollment', 'submission_date', 'updated_at',
            'content', 'file', 'file_url', 'grade', 'is_late', 'feedback',
            'student_name', 'assignment_title', 'can_edit'
        ]

    def get_student_name(self, obj):
        return obj.enrollment.student.user.get_full_name()

    def get_assignment_title(self, obj):
        return obj.assignment.title

    def get_can_edit(self, obj):
        return obj.can_edit()

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None


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


class StudentEnrollmentRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrollmentRequest
        fields = [
            'student', 'student_name', 'student_id', 'requested_class', 'class_name',
            'status', 'academic_year', 'additional_info', 'requested_at',
            'reviewed_by', 'reviewer_name', 'reviewed_at', 'rejection_reason'
        ]
        read_only_fields = ['requested_at', 'reviewed_at', 'reviewed_by']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_student_id(self, obj):
        return obj.student.student_id

    def get_class_name(self, obj):
        return obj.requested_class.name if obj.requested_class else None

    def get_reviewer_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None


class LessonPlanSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    submitted_to_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_assigned', 'class_name', 'title', 'topic', 'objectives',
            'materials_needed', 'lesson_content', 'homework', 'assessment_method',
            'scheduled_date', 'duration_minutes', 'status', 'submitted_to',
            'submitted_to_name', 'submitted_at', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'feedback', 'created_at', 'updated_at'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name()

    def get_subject_name(self, obj):
        return obj.subject.name

    def get_class_name(self, obj):
        return obj.class_assigned.name if obj.class_assigned else None

    def get_submitted_to_name(self, obj):
        return obj.submitted_to.get_full_name() if obj.submitted_to else None

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'option_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'marks', 'order', 'options']


class QuizSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    submitted_to_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_assigned', 'class_name', 'title', 'description', 'instructions',
            'duration_minutes', 'total_marks', 'passing_marks', 'scheduled_date',
            'status', 'submitted_to', 'submitted_to_name', 'submitted_at',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'feedback',
            'created_at', 'updated_at', 'questions'
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name()

    def get_subject_name(self, obj):
        return obj.subject.name

    def get_class_name(self, obj):
        return obj.class_assigned.name if obj.class_assigned else None

    def get_submitted_to_name(self, obj):
        return obj.submitted_to.get_full_name() if obj.submitted_to else None

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None


class QuizResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    quiz_title = serializers.SerializerMethodField()
    submitted_to_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = [
            'id', 'quiz', 'quiz_title', 'student', 'student_name', 'enrollment',
            'score', 'total_marks', 'percentage', 'passed', 'answers',
            'time_taken_minutes', 'submitted_at', 'status', 'submitted_to',
            'submitted_to_name', 'submitted_at_review', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'feedback'
        ]

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_quiz_title(self, obj):
        return obj.quiz.title

    def get_submitted_to_name(self, obj):
        return obj.submitted_to.get_full_name() if obj.submitted_to else None

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None

