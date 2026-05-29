from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ClassViewSet, SubjectViewSet, StudentViewSet, EnrollmentViewSet,
    GradeViewSet, AttendanceViewSet, ExamViewSet, ExamResultViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet, AcademicTermViewSet,
    ClassScheduleViewSet, CurriculumViewSet,
    dashboard_stats, bulk_attendance, my_schedule, my_profile,
    enrollment_request_list, approve_enrollment_request, reject_enrollment_request,
    LessonPlanViewSet, QuizViewSet, QuestionViewSet, QuestionOptionViewSet,
    QuizResultViewSet
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
router.register(r'lesson-plans', LessonPlanViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'question-options', QuestionOptionViewSet)
router.register(r'quiz-results', QuizResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', dashboard_stats, name='dashboard_stats'),
    path('bulk-attendance/', bulk_attendance, name='bulk_attendance'),
    path('my-schedule/', my_schedule, name='my_schedule'),
    path('my-profile/', my_profile, name='my_profile'),
    path('enrollment-request/', enrollment_request_list, name='enrollment_request_list'),
    path('enrollment-request/<int:student_id>/approve/', approve_enrollment_request, name='approve_enrollment_request'),
    path('enrollment-request/<int:student_id>/reject/', reject_enrollment_request, name='reject_enrollment_request'),
]
