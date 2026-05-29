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

    # 1. Create Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@rutabo.rw',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Admin user created (username: admin, password: admin123)")
    else:
        print("ℹ️ Admin user already exists")

    # 2. Create Head Teacher
    head_teacher, created = User.objects.get_or_create(
        username='head_teacher',
        defaults={
            'email': 'headteacher@rutabo.rw',
            'first_name': 'John',
            'last_name': 'Mugabo',
            'role': 'head_teacher',
            'is_active': True
        }
    )
    if created:
        head_teacher.set_password('teacher123')
        head_teacher.save()
        StaffProfile.objects.get_or_create(user=head_teacher, defaults={
            'department': 'Administration',
            'qualification': 'Masters in Education',
            'date_joined': date(2020, 1, 15)
        })
        print("✅ Head Teacher created (username: head_teacher, password: teacher123)")
    else:
        print("ℹ️ Head Teacher already exists")

    # 3. Create DOS (Director of Studies)
    dos_user, created = User.objects.get_or_create(
        username='dos',
        defaults={
            'email': 'dos@rutabo.rw',
            'first_name': 'Mary',
            'last_name': 'Kamanzi',
            'role': 'dos',
            'is_active': True
        }
    )
    if created:
        dos_user.set_password('dos123')
        dos_user.save()
        StaffProfile.objects.get_or_create(user=dos_user, defaults={
            'department': 'Academics',
            'qualification': 'Masters in Curriculum',
            'date_joined': date(2020, 2, 1)
        })
        print("✅ DOS created (username: dos, password: dos123)")
    else:
        print("ℹ️ DOS already exists")

    # 4. Create Teacher
    teacher_user, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'email': 'teacher1@rutabo.rw',
            'first_name': 'Peter',
            'last_name': 'Niyonzima',
            'role': 'teacher',
            'is_active': True
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        StaffProfile.objects.get_or_create(user=teacher_user, defaults={
            'department': 'Science',
            'qualification': 'Bachelors in Physics',
            'date_joined': date(2021, 9, 1)
        })
        TeacherProfile.objects.get_or_create(user=teacher_user, defaults={
            'hire_date': date(2021, 9, 1)
        })
        print("✅ Teacher created (username: teacher1, password: teacher123)")
    else:
        print("ℹ️ Teacher already exists")

    # 5. Create or get academic term
    term, _ = AcademicTerm.objects.get_or_create(
        name="Term 1 2026",
        defaults={
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 6, 30)
        }
    )

    # 6. Get active staff users
    animateur_user = User.objects.filter(role='animateur').first()

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
