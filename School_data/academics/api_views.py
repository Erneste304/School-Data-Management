from datetime import date
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Count, Q

from .models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, Assignment, AssignmentSubmission,
    AcademicTerm, ClassSchedule, Curriculum
)
from .serializers import (
    ClassSerializer, StudentSerializer, SubjectSerializer,
    EnrollmentSerializer, GradeSerializer, AttendanceSerializer,
    ExamSerializer, ExamResultSerializer, AssignmentSerializer,
    AssignmentSubmissionSerializer, AcademicTermSerializer,
    ClassScheduleSerializer, CurriculumSerializer
)
from accounts.models import CustomUser
from accounts.permissions import IsStaffMember, IsDOSOrAbove


# ── ViewSets ──────────────────────────────────────────────────────────────────

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related('class_tutor').all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        level = self.request.query_params.get('level')
        if level:
            qs = qs.filter(level=level)
        return qs


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('teacher').all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'current_class').filter(is_active=True)
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        class_id = self.request.query_params.get('class_id')
        if class_id:
            qs = qs.filter(current_class_id=class_id)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        return qs


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('student__user', 'enrolled_class').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        class_id = self.request.query_params.get('class_id')
        year = self.request.query_params.get('year')
        if class_id:
            qs = qs.filter(enrolled_class_id=class_id)
        if year:
            qs = qs.filter(academic_year=year)
        return qs


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.select_related('enrollment__student__user').all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        class_id = self.request.query_params.get('class_id')
        
        user = self.request.user
        if user.role == 'student':
            qs = qs.filter(enrollment__student__user=user)
        elif student_id:
            qs = qs.filter(enrollment__student__user_id=student_id)
            
        if class_id:
            qs = qs.filter(enrollment__enrolled_class_id=class_id)
            
        return qs


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('enrollment__student__user').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        date_param = self.request.query_params.get('date')
        class_id = self.request.query_params.get('class_id')
        student_id = self.request.query_params.get('student_id')
        if date_param:
            qs = qs.filter(date=date_param)
        if class_id:
            qs = qs.filter(enrollment__enrolled_class_id=class_id)
        if student_id:
            qs = qs.filter(enrollment__student__user_id=student_id)
        return qs


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('subject').all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.select_related(
        'enrollment__student__user', 'exam'
    ).all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('subject').all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related(
        'assignment', 'enrollment__student__user'
    ).all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        assignment_id = self.request.query_params.get('assignment_id')
        enrollment_id = self.request.query_params.get('enrollment_id')
        student_id = self.request.query_params.get('student_id')
        
        user = self.request.user
        if user.role == 'student':
            qs = qs.filter(enrollment__student__user=user)
        elif student_id:
            qs = qs.filter(enrollment__student__user_id=student_id)
            
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        if enrollment_id:
            qs = qs.filter(enrollment_id=enrollment_id)
        return qs


class AcademicTermViewSet(viewsets.ModelViewSet):
    queryset = AcademicTerm.objects.all()
    serializer_class = AcademicTermSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.select_related(
        'class_assigned', 'subject__teacher', 'term'
    ).filter(is_active=True)
    serializer_class = ClassScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        class_id = self.request.query_params.get('class_id')
        day = self.request.query_params.get('day')
        teacher_id = self.request.query_params.get('teacher_id')
        if class_id:
            qs = qs.filter(class_assigned_id=class_id)
        if day:
            qs = qs.filter(day_of_week=day)
        if teacher_id:
            qs = qs.filter(subject__teacher_id=teacher_id)
        return qs.order_by('start_time')


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.prefetch_related('subjects').all()
    serializer_class = CurriculumSerializer
    permission_classes = [permissions.IsAuthenticated]


# ── Dashboard Stats Endpoint ─────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Return summary statistics for the admin/overview dashboard."""
    today = date.today()
    today_attendance = Attendance.objects.filter(date=today)

    data = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_staff': CustomUser.objects.filter(
            role__in=['admin', 'head_teacher', 'dos', 'dod', 'teacher',
                      'animateur', 'animatrice', 'accountant']
        ).count(),
        'total_classes': Class.objects.count(),
        'total_subjects': Subject.objects.count(),
        'active_enrollments': Enrollment.objects.count(),
        'attendance_today': {
            'present': today_attendance.filter(status='Present').count(),
            'absent': today_attendance.filter(status='Absent').count(),
            'excused': today_attendance.filter(status='Excused').count(),
        },
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_attendance(request):
    """Mark attendance for an entire class at once."""
    class_id = request.data.get('class_id')
    att_date = request.data.get('date', str(date.today()))
    records = request.data.get('records', [])

    if not class_id or not records:
        return Response(
            {'detail': 'class_id and records are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    created = 0
    updated = 0
    for record in records:
        enrollment_id = record.get('enrollment_id')
        att_status = record.get('status', 'Present')
        is_late = record.get('is_late', False)
        lateness = record.get('lateness_minutes', 0)

        obj, was_created = Attendance.objects.update_or_create(
            enrollment_id=enrollment_id,
            date=att_date,
            defaults={
                'status': att_status,
                'is_late': is_late,
                'lateness_minutes': lateness,
            }
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return Response({
        'detail': f'Attendance saved. {created} created, {updated} updated.',
        'created': created,
        'updated': updated,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_schedule(request):
    """Return the schedule for the currently authenticated user."""
    user = request.user
    schedules = ClassSchedule.objects.filter(is_active=True)

    if user.role == 'student':
        try:
            student = Student.objects.get(user=user)
            if student.current_class:
                schedules = schedules.filter(class_assigned=student.current_class)
            else:
                schedules = schedules.none()
        except Student.DoesNotExist:
            schedules = schedules.none()
    elif user.role in ('teacher', 'animateur', 'animatrice'):
        schedules = schedules.filter(subject__teacher=user)
    # admin/head_teacher/dos see everything

    day = request.query_params.get('day')
    if day:
        schedules = schedules.filter(day_of_week=day)

    serializer = ClassScheduleSerializer(schedules.order_by('day_of_week', 'start_time'), many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_profile(request):
    """Return the current user's profile information."""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'role': user.role,
        'role_display': user.get_role_display(),
        'phone': user.phone,
    }

    # Add student-specific data
    if user.role == 'student':
        try:
            student = Student.objects.select_related('current_class').get(user=user)
            data['student'] = {
                'student_id': student.student_id,
                'current_class': student.current_class.name if student.current_class else None,
                'enrollment_date': student.enrollment_date,
                'gpa': student.calculate_gpa(),
                'attendance_rate': student.get_attendance_rate(),
            }
        except Student.DoesNotExist:
            data['student'] = None

    return Response(data)
