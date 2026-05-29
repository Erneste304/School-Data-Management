from django.db import models
from django.conf import settings
from django.db.models import Avg, Count, Q
from django.utils import timezone
from accounts.models import CustomUser
from schools.models import LEVEL_CHOICES

class Class(models.Model):
    """Represents an academic class, e.g., 'Grade 10A'."""
    name = models.CharField(max_length=100, unique=True)
    class_tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tutored_class'
    )
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='PRIMARY')

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name

    def get_class_average(self):
        """Calculate average GPA for all students in the class."""
        students = self.students.filter(is_active=True)
        if not students.exists():
            return 0.0
        total_gpa = sum(student.calculate_gpa() for student in students)
        return round(total_gpa / students.count(), 2)

    def get_attendance_rate(self):
        """Calculate overall attendance rate for the class."""
        enrollments = Enrollment.objects.filter(enrolled_class=self)
        if not enrollments.exists():
            return 0.0
        total_attendance = 0
        for enrollment in enrollments:
            total_attendance += enrollment.student.get_attendance_rate()
        return round(total_attendance / enrollments.count(), 2)


class Student(models.Model):
    """
    Stores academic-specific information for a user with the 'STUDENT' role.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    current_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

    @property
    def full_name(self):
        return self.user.get_full_name()

    def calculate_gpa(self):
        """
        Calculates the average score across all exam results for the student.
        """
        results = ExamResult.objects.filter(enrollment__student=self)
        if not results.exists():
            return 0.0
        total_score = sum(r.score for r in results)
        return round(float(total_score / results.count()), 2)

    def get_attendance_rate(self):
        """
        Calculates attendance percentage for the student.
        """
        total_records = Attendance.objects.filter(enrollment__student=self).count()
        if total_records == 0:
            return 0.0
        present_records = Attendance.objects.filter(
            enrollment__student=self,
            status='Present'
        ).count()
        return round((present_records / total_records) * 100, 2)

    def get_grade_distribution(self):
        """
        Returns distribution of grades across all subjects.
        """
        results = ExamResult.objects.filter(enrollment__student=self)
        grade_counts = {}
        for result in results:
            grade = result.grade or 'N/A'
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        return grade_counts

    def get_subject_performance(self):
        """
        Returns performance breakdown by subject.
        """
        results = ExamResult.objects.filter(enrollment__student=self).select_related('exam__subject')
        subject_performance = {}
        for result in results:
            subject = result.exam.subject.name
            if subject not in subject_performance:
                subject_performance[subject] = {
                    'scores': [],
                    'average': 0,
                    'count': 0
                }
            subject_performance[subject]['scores'].append(float(result.score))
            subject_performance[subject]['count'] += 1

        for subject in subject_performance:
            scores = subject_performance[subject]['scores']
            subject_performance[subject]['average'] = round(sum(scores) / len(scores), 2) if scores else 0

        return subject_performance

    def get_pending_assignments(self):
        """
        Returns count of pending assignments.
        """
        current_enrollment = Enrollment.objects.filter(student=self, academic_year='2024-2025').first()
        if not current_enrollment:
            return 0
        return AssignmentSubmission.objects.filter(
            enrollment=current_enrollment,
            grade__isnull=True
        ).count()


class Subject(models.Model):
    """Represents a subject, e.g., 'Mathematics'."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects_taught'
    )

    def __str__(self):
        return f"{self.name} ({self.code})"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20, default='2025-2026')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'enrolled_class', 'academic_year']

    def __str__(self):
        return f"{self.student} - {self.enrolled_class} ({self.academic_year})"


class StudentEnrollmentRequest(models.Model):
    """Request from students to be enrolled in a class"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    requested_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    academic_year = models.CharField(max_length=20, default='2025-2026')
    additional_info = models.TextField(blank=True, help_text='Additional information from student')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Student Enrollment Request"
        verbose_name_plural = "Student Enrollment Requests"
        ordering = ['-requested_at']
    
    def approve(self, reviewer):
        """Approve the enrollment request and create enrollment"""
        if self.requested_class:
            enrollment, created = Enrollment.objects.get_or_create(
                student=self.student,
                enrolled_class=self.requested_class,
                academic_year=self.academic_year
            )
            self.student.current_class = self.requested_class
            self.student.save()
        
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
    
    def reject(self, reviewer, reason=''):
        """Reject the enrollment request"""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def __str__(self):
        return f"{self.student} - {self.requested_class} ({self.get_status_display()})"


class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    assignment_name = models.CharField(max_length=100)
    date_recorded = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.assignment_name}: {self.score} for {self.enrollment}"
    class Meta:
        unique_together = ('enrollment', 'assignment_name')
        verbose_name_plural = "Grades"

class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Excused', 'Excused')])
    is_late = models.BooleanField(default=False)
    lateness_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('enrollment', 'date')
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.enrollment} - {self.date}: {self.status}"
    
class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} on {self.date} for {self.subject}"
    
class ExamResult(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, blank=True, help_text="e.g. A, B+, C")

    class Meta:
        unique_together = ('enrollment', 'exam')
        verbose_name_plural = "Exam Results"

    def __str__(self):
        return f"{self.enrollment} - {self.exam}: {self.score}"
    
class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    hire_date = models.DateField()
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    # For multiple levels support as per plan
    levels = models.CharField(max_length=100, blank=True, help_text="e.g. NURSERY,PRIMARY")

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    @property
    def full_name(self):
        return self.user.get_full_name()
    class Meta:
        verbose_name_plural = "Teacher Profiles"  
class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_points = models.IntegerField(default=100)
    allow_late_submission = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} for {self.subject}"
    
    def is_past_deadline(self):
        from django.utils import timezone
        return timezone.now() > self.due_date
    
    class Meta:
        verbose_name_plural = "Assignments"
        ordering = ['-due_date']

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_late = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'enrollment')
        verbose_name_plural = "Assignment Submissions"
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.enrollment} submission for {self.assignment}"
    
    def can_edit(self):
        """Check if submission can still be edited (before deadline)"""
        return not self.assignment.is_past_deadline() and not self.is_late
    
    def save(self, *args, **kwargs):
        # Check if submission is late
        if not self.pk:  # New submission
            from django.utils import timezone
            self.is_late = timezone.now() > self.assignment.due_date
        super().save(*args, **kwargs)
class AcademicTerm(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    class Meta:
        verbose_name_plural = "Academic Terms"

class LessonPlan(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    )

    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='lesson_plans')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lesson_plans')
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='lesson_plans')
    
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    objectives = models.TextField(help_text="Learning objectives for this lesson")
    materials_needed = models.TextField(blank=True, help_text="Materials and resources needed")
    lesson_content = models.TextField(help_text="Detailed lesson content and activities")
    homework = models.TextField(blank=True, help_text="Homework assignment")
    assessment_method = models.TextField(blank=True, help_text="How students will be assessed")
    
    scheduled_date = models.DateField()
    duration_minutes = models.IntegerField(default=60, help_text="Lesson duration in minutes")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                                    blank=True, related_name='received_lesson_plans',
                                    limit_choices_to={'role__in': ['dos', 'head_teacher', 'admin']})
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                                   blank=True, related_name='reviewed_lesson_plans')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, help_text="Feedback from reviewer")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Lesson Plans"
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.title} - {self.subject.name} ({self.scheduled_date})"

class Quiz(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='quizzes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=50)
    
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    submitted_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                                    blank=True, related_name='received_quizzes',
                                    limit_choices_to={'role__in': ['dos', 'head_teacher', 'admin']})
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                                   blank=True, related_name='reviewed_quizzes')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question_text[:50]}..."

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.option_text}"

class QuizResult(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_results')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_results')
    
    score = models.FloatField()
    total_marks = models.FloatField()
    percentage = models.FloatField()
    passed = models.BooleanField(default=False)
    
    answers = models.JSONField(default=dict, blank=True)
    time_taken_minutes = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                                    blank=True, related_name='received_quiz_results',
                                    limit_choices_to={'role__in': ['dos', 'head_teacher', 'admin']})
    submitted_at_review = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                                   blank=True, related_name='reviewed_quiz_results')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Quiz Results"
        ordering = ['-submitted_at']
        unique_together = ['quiz', 'student']

    def save(self, *args, **kwargs):
        self.percentage = (self.score / self.total_marks) * 100 if self.total_marks > 0 else 0
        self.passed = self.percentage >= self.quiz.passing_marks
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.quiz.title}: {self.score}/{self.total_marks}"

class ClassSchedule(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, help_text="Room number or location")
    term = models.ForeignKey(AcademicTerm, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('class_assigned', 'subject', 'day_of_week', 'start_time')
        verbose_name_plural = "Class Schedules"

    def __str__(self):
        return f"{self.class_assigned} - {self.subject} on {self.day_of_week} from {self.start_time} to {self.end_time}"

    def get_duration(self):
        """Calculate duration of the class in minutes."""
        from datetime import datetime, time
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)
    
class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, related_name='curriculums')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Curriculums"