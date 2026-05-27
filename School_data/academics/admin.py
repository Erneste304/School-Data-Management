from django.contrib import admin
from .models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, TeacherProfile, Assignment, AssignmentSubmission,
    AcademicTerm, ClassSchedule, Curriculum
)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'class_tutor', 'get_class_average', 'get_attendance_rate']
    list_filter = ['level']
    search_fields = ['name', 'class_tutor__username']
    readonly_fields = ['get_class_average', 'get_attendance_rate']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'current_class', 'is_active', 'calculate_gpa', 'get_attendance_rate']
    list_filter = ['is_active', 'current_class']
    search_fields = ['user__username', 'student_id']
    readonly_fields = ['calculate_gpa', 'get_attendance_rate', 'get_grade_distribution', 'get_subject_performance']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'teacher']
    search_fields = ['name', 'code']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'enrolled_class', 'academic_year', 'enrollment_date']
    list_filter = ['academic_year', 'enrolled_class']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'assignment_name', 'score', 'date_recorded']
    list_filter = ['date_recorded']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'date', 'status', 'is_late']
    list_filter = ['status', 'is_late', 'date']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'date']
    list_filter = ['date', 'subject']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'exam', 'score', 'grade']
    list_filter = ['exam__subject', 'grade']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'hire_date']
    filter_horizontal = ['subjects']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'due_date']
    list_filter = ['due_date', 'subject']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'enrollment', 'submission_date', 'grade']
    list_filter = ['submission_date']


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['class_assigned', 'subject', 'day_of_week', 'start_time', 'end_time', 'room', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'term']
    search_fields = ['class_assigned__name', 'subject__name', 'room']


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['subjects']
