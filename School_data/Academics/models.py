from django.db import models
from django.conf import settings
from Users.models import CustomUser, LEVEL_CHOICES

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

    def calculate_gpa(self):
        """
        Calculates the average score across all exam results for the student.
        """
        results = ExamResult.objects.filter(enrollment__student=self)
        if not results.exists():
            return 0.0
        total_score = sum(r.score for r in results)
        return round(float(total_score / results.count()), 2)


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
    academic_year = models.CharField(max_length=9, help_text="e.g., '2024-2025'")
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'enrolled_class', 'academic_year')

    def __str__(self):
        return f"{self.student} enrolled in {self.enrolled_class} for {self.academic_year}"
    
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
    class Meta:
        verbose_name_plural = "Teacher Profiles"  
class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} for {self.subject}"
    class Meta:
        verbose_name_plural = "Assignments"
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    submission_date = models.DateField(auto_now_add=True)
    content = models.TextField()
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'enrollment')
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"{self.enrollment} submission for {self.assignment}"
class AcademicTerm(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    class Meta:
        verbose_name_plural = "Academic Terms"

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

    class Meta:
        unique_together = ('class_assigned', 'subject', 'day_of_week', 'start_time')
        verbose_name_plural = "Class Schedules"

    def __str__(self):
        return f"{self.class_assigned} - {self.subject} on {self.day_of_week} from {self.start_time} to {self.end_time}"
    
class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, related_name='curriculums')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Curriculums"

class AcademicYear(models.Model):
    year = models.CharField(max_length=9, unique=True, help_text="e.g., '2024-2025'")
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.year
    class Meta:
        verbose_name_plural = "Academic Years"
        
   