import os
import django
from datetime import date, time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'School_data.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import CustomUser, StaffProfile
from academics.models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, TeacherProfile, AcademicTerm, ClassSchedule
)

User = get_user_model()

def seed():
    print("🌱 Seeding database...")

    # 1. Create or get academic term
    term, _ = AcademicTerm.objects.get_or_create(
        name="Term 1 2026",
        defaults={
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 6, 30)
        }
    )

    # 2. Get active staff users
    admin_user = User.objects.filter(role='admin').first()
    teacher_user = User.objects.filter(role='head_teacher').first() or User.objects.first()
    animateur_user = User.objects.filter(role='animateur').first() or User.objects.first()

    # Create Class
    class_10a, _ = Class.objects.get_or_create(
        name="Grade 10A",
        defaults={
            'class_tutor': teacher_user,
            'level': 'ORDINARY_LEVEL' # OR Choice
        }
    )
    class_11b, _ = Class.objects.get_or_create(
        name="Grade 11B",
        defaults={
            'class_tutor': animateur_user,
            'level': 'ADVANCED_LEVEL'
        }
    )

    # 3. Create Subjects
    math, _ = Subject.objects.get_or_create(
        code="MATH10",
        defaults={
            'name': "Mathematics",
            'teacher': teacher_user
        }
    )
    physics, _ = Subject.objects.get_or_create(
        code="PHYS11",
        defaults={
            'name': "Physics",
            'teacher': animateur_user
        }
    )

    # 4. Create Student Users
    student_usernames = ["student1", "student2", "student3"]
    students = []
    
    for i, uname in enumerate(student_usernames):
        s_user, created = User.objects.get_or_create(
            username=uname,
            defaults={
                'email': f"{uname}@rutabo.rw",
                'first_name': f"Student {i+1}",
                'last_name': "Doe",
                'role': 'student',
                'phone': f"+25078800000{i+1}"
            }
        )
        if created:
            s_user.set_password("password123")
            s_user.save()

        student, _ = Student.objects.get_or_create(
            user=s_user,
            defaults={
                'student_id': f"STUD00{i+1}",
                'enrollment_date': date(2025, 1, 1),
                'current_class': class_10a if i < 2 else class_11b,
                'is_active': True
            }
        )
        students.append(student)

        # 5. Create Enrollments
        enrollment, _ = Enrollment.objects.get_or_create(
            student=student,
            enrolled_class=class_10a if i < 2 else class_11b,
            academic_year="2025-2026"
        )

        # 6. Add Grades
        Grade.objects.get_or_create(
            enrollment=enrollment,
            assignment_name="Midterm Quiz",
            defaults={'score': 85.5 + i * 4.5}
        )

        # 7. Add Attendance
        Attendance.objects.get_or_create(
            enrollment=enrollment,
            date=date.today(),
            defaults={
                'status': 'Present' if i != 1 else 'Absent',
                'is_late': False,
                'lateness_minutes': 0
            }
        )

    # 8. Create Class Schedules
    ClassSchedule.objects.get_or_create(
        class_assigned=class_10a,
        subject=math,
        day_of_week="Monday",
        start_time=time(8, 30),
        defaults={
            'end_time': time(10, 0),
            'room': "Room 101",
            'term': term,
            'is_active': True
        }
    )
    ClassSchedule.objects.get_or_create(
        class_assigned=class_10a,
        subject=physics,
        day_of_week="Monday",
        start_time=time(10, 30),
        defaults={
            'end_time': time(12, 0),
            'room': "Lab B",
            'term': term,
            'is_active': True
        }
    )

    print("✨ Seeding completed successfully!")

if __name__ == '__main__':
    seed()
