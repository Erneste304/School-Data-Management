from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ClassViewSet, SubjectViewSet, StudentViewSet, EnrollmentViewSet,
    GradeViewSet, AttendanceViewSet, ExamViewSet, ExamResultViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet, AcademicTermViewSet,
    ClassScheduleViewSet, CurriculumViewSet,
    dashboard_stats, bulk_attendance, my_schedule, my_profile
)

app_name = 'academics_api'

router = DefaultRouter()
router.register(r'classes', ClassViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'students', StudentViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'exam-results', ExamResultViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', AssignmentSubmissionViewSet)
router.register(r'terms', AcademicTermViewSet)
router.register(r'schedules', ClassScheduleViewSet)
router.register(r'curriculums', CurriculumViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', dashboard_stats, name='dashboard_stats'),
    path('bulk-attendance/', bulk_attendance, name='bulk_attendance'),
    path('my-schedule/', my_schedule, name='my_schedule'),
    path('my-profile/', my_profile, name='my_profile'),
]
