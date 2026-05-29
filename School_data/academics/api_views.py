from datetime import date
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Count, Q

from .models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, Assignment, AssignmentSubmission,
    AcademicTerm, ClassSchedule, Curriculum, StudentEnrollmentRequest,
    LessonPlan, Quiz, Question, QuestionOption, QuizResult
)
from .serializers import (
    ClassSerializer, StudentSerializer, SubjectSerializer,
    EnrollmentSerializer, GradeSerializer, AttendanceSerializer,
    ExamSerializer, ExamResultSerializer, AssignmentSerializer,
    AssignmentSubmissionSerializer, AcademicTermSerializer,
    ClassScheduleSerializer, CurriculumSerializer, StudentEnrollmentRequestSerializer,
    LessonPlanSerializer, QuizSerializer, QuestionSerializer, QuestionOptionSerializer,
    QuizResultSerializer
)
from accounts.models import CustomUser
from accounts.permissions import IsStaffMember, IsDOSOrAbove


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

    def perform_create(self, serializer):
        assignment = serializer.validated_data['assignment']
        
        # Check if deadline has passed
        if assignment.is_past_deadline() and not assignment.allow_late_submission:
            raise PermissionError("Assignment deadline has passed. Late submissions are not allowed.")
        
        serializer.save()

    def perform_update(self, serializer):
        submission = self.get_object()
        
        # Check if submission can still be edited
        if not submission.can_edit():
            raise PermissionError("Cannot edit submission after deadline or if marked as late.")
        
        serializer.save()


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


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def enrollment_request_list(request):
    """List and create enrollment requests (admin/head_teacher for list, students for create)"""
    if request.method == 'GET':
        if request.user.role not in ('admin', 'head_teacher'):
            return Response({'detail': 'Not authorized.'}, status=403)
        
        requests = StudentEnrollmentRequest.objects.select_related(
            'student__user', 'requested_class', 'reviewed_by'
        ).all()
        serializer = StudentEnrollmentRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'student':
            return Response({'detail': 'Only students can submit enrollment requests.'}, status=403)
        
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({'detail': 'Student record not found.'}, status=404)
        
        # Check if request already exists
        if StudentEnrollmentRequest.objects.filter(student=student).exists():
            return Response({'detail': 'You already have a pending enrollment request.'}, status=400)
        
        serializer = StudentEnrollmentRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student)
            # Send email notification to admin/head_teacher
            send_enrollment_notification(student, serializer.instance)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_enrollment_request(request, student_id):
    """Approve an enrollment request (admin/head_teacher only)"""
    if request.user.role not in ('admin', 'head_teacher'):
        return Response({'detail': 'Not authorized.'}, status=403)
    
    try:
        enrollment_request = StudentEnrollmentRequest.objects.get(student_id=student_id)
    except StudentEnrollmentRequest.DoesNotExist:
        return Response({'detail': 'Enrollment request not found.'}, status=404)
    
    enrollment_request.approve(request.user)
    return Response({'detail': 'Enrollment request approved successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_enrollment_request(request, student_id):
    """Reject an enrollment request (admin/head_teacher only)"""
    if request.user.role not in ('admin', 'head_teacher'):
        return Response({'detail': 'Not authorized.'}, status=403)
    
    try:
        enrollment_request = StudentEnrollmentRequest.objects.get(student_id=student_id)
    except StudentEnrollmentRequest.DoesNotExist:
        return Response({'detail': 'Enrollment request not found.'}, status=404)
    
    reason = request.data.get('reason', '')
    enrollment_request.reject(request.user, reason)
    return Response({'detail': 'Enrollment request rejected.'})


def send_enrollment_notification(student, enrollment_request):
    """Send email notification to admin/head_teacher about new enrollment request"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    admin_users = CustomUser.objects.filter(role__in=('admin', 'head_teacher'))
    admin_emails = [user.email for user in admin_users if user.email]
    
    if not admin_emails:
        return
    
    subject = f'New Enrollment Request: {student.user.get_full_name()}'
    message = f"""
A new student has submitted an enrollment request:

Student: {student.user.get_full_name()}
Student ID: {student.student_id}
Email: {student.user.email}
Requested Class: {enrollment_request.requested_class.name if enrollment_request.requested_class else 'Not specified'}
Academic Year: {enrollment_request.academic_year}
Additional Info: {enrollment_request.additional_info or 'None'}

Please review and approve/reject this request in the admin dashboard.
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")


class LessonPlanViewSet(viewsets.ModelViewSet):
    queryset = LessonPlan.objects.select_related(
        'teacher__user', 'subject', 'class_assigned', 'submitted_to', 'reviewed_by'
    ).all()
    serializer_class = LessonPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if user.role == 'teacher':
            qs = qs.filter(teacher__user=user)
        elif user.role in ['dos', 'head_teacher', 'admin']:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                qs = qs.filter(status=status_filter)
        
        return qs

    def perform_create(self, serializer):
        from accounts.models import TeacherProfile
        teacher = TeacherProfile.objects.get(user=self.request.user)
        serializer.save(teacher=teacher)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        lesson_plan = self.get_object()
        if lesson_plan.status != 'draft':
            return Response({'detail': 'Only draft lesson plans can be submitted'}, status=status.HTTP_400_BAD_REQUEST)
        
        dos_user = CustomUser.objects.filter(role='dos').first()
        if not dos_user:
            dos_user = CustomUser.objects.filter(role__in=['head_teacher', 'admin']).first()
        
        lesson_plan.status = 'submitted'
        lesson_plan.submitted_to = dos_user
        lesson_plan.submitted_at = timezone.now()
        lesson_plan.save()
        
        serializer = self.get_serializer(lesson_plan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        lesson_plan = self.get_object()
        if lesson_plan.status != 'submitted':
            return Response({'detail': 'Only submitted lesson plans can be approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        lesson_plan.status = 'approved'
        lesson_plan.reviewed_by = request.user
        lesson_plan.reviewed_at = timezone.now()
        lesson_plan.save()
        
        serializer = self.get_serializer(lesson_plan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        lesson_plan = self.get_object()
        if lesson_plan.status != 'submitted':
            return Response({'detail': 'Only submitted lesson plans can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        feedback = request.data.get('feedback', '')
        lesson_plan.status = 'rejected'
        lesson_plan.reviewed_by = request.user
        lesson_plan.reviewed_at = timezone.now()
        lesson_plan.feedback = feedback
        lesson_plan.save()
        
        serializer = self.get_serializer(lesson_plan)
        return Response(serializer.data)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related(
        'teacher__user', 'subject', 'class_assigned', 'submitted_to', 'reviewed_by'
    ).prefetch_related('questions__options').all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if user.role == 'teacher':
            qs = qs.filter(teacher__user=user)
        elif user.role in ['dos', 'head_teacher', 'admin']:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                qs = qs.filter(status=status_filter)
        
        return qs

    def perform_create(self, serializer):
        from accounts.models import TeacherProfile
        teacher = TeacherProfile.objects.get(user=self.request.user)
        serializer.save(teacher=teacher)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        if quiz.status != 'draft':
            return Response({'detail': 'Only draft quizzes can be submitted'}, status=status.HTTP_400_BAD_REQUEST)
        
        dos_user = CustomUser.objects.filter(role='dos').first()
        if not dos_user:
            dos_user = CustomUser.objects.filter(role__in=['head_teacher', 'admin']).first()
        
        quiz.status = 'submitted'
        quiz.submitted_to = dos_user
        quiz.submitted_at = timezone.now()
        quiz.save()
        
        serializer = self.get_serializer(quiz)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        quiz = self.get_object()
        if quiz.status != 'submitted':
            return Response({'detail': 'Only submitted quizzes can be approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        quiz.status = 'approved'
        quiz.reviewed_by = request.user
        quiz.reviewed_at = timezone.now()
        quiz.save()
        
        serializer = self.get_serializer(quiz)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        quiz = self.get_object()
        if quiz.status != 'submitted':
            return Response({'detail': 'Only submitted quizzes can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        feedback = request.data.get('feedback', '')
        quiz.status = 'rejected'
        quiz.reviewed_by = request.user
        quiz.reviewed_at = timezone.now()
        quiz.feedback = feedback
        quiz.save()
        
        serializer = self.get_serializer(quiz)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        quiz = self.get_object()
        if quiz.status != 'approved':
            return Response({'detail': 'Only approved quizzes can be published'}, status=status.HTTP_400_BAD_REQUEST)
        
        quiz.status = 'published'
        quiz.save()
        
        serializer = self.get_serializer(quiz)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('quiz').prefetch_related('options').all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            qs = qs.filter(quiz_id=quiz_id)
        return qs


class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.select_related('question').all()
    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.request.query_params.get('question_id')
        if question_id:
            qs = qs.filter(question_id=question_id)
        return qs


class QuizResultViewSet(viewsets.ModelViewSet):
    queryset = QuizResult.objects.select_related(
        'quiz', 'student__user', 'enrollment', 'submitted_to', 'reviewed_by'
    ).all()
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if user.role == 'teacher':
            qs = qs.filter(quiz__teacher__user=user)
        elif user.role == 'student':
            from accounts.models import Student
            try:
                student = Student.objects.get(user=user)
                qs = qs.filter(student=student)
            except Student.DoesNotExist:
                qs = qs.none()
        elif user.role in ['dos', 'head_teacher', 'admin']:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                qs = qs.filter(status=status_filter)
        
        return qs

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz_result = self.get_object()
        if quiz_result.status != 'draft':
            return Response({'detail': 'Only draft results can be submitted'}, status=status.HTTP_400_BAD_REQUEST)
        
        dos_user = CustomUser.objects.filter(role='dos').first()
        if not dos_user:
            dos_user = CustomUser.objects.filter(role__in=['head_teacher', 'admin']).first()
        
        quiz_result.status = 'submitted'
        quiz_result.submitted_to = dos_user
        quiz_result.submitted_at_review = timezone.now()
        quiz_result.save()
        
        serializer = self.get_serializer(quiz_result)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        quiz_result = self.get_object()
        if quiz_result.status != 'submitted':
            return Response({'detail': 'Only submitted results can be approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        quiz_result.status = 'approved'
        quiz_result.reviewed_by = request.user
        quiz_result.reviewed_at = timezone.now()
        quiz_result.save()
        
        serializer = self.get_serializer(quiz_result)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        quiz_result = self.get_object()
        if quiz_result.status != 'submitted':
            return Response({'detail': 'Only submitted results can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        feedback = request.data.get('feedback', '')
        quiz_result.status = 'rejected'
        quiz_result.reviewed_by = request.user
        quiz_result.reviewed_at = timezone.now()
        quiz_result.feedback = feedback
        quiz_result.save()
        
        serializer = self.get_serializer(quiz_result)
        return Response(serializer.data)

