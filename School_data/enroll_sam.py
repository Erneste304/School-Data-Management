#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'School_data.settings')
django.setup()

from accounts.models import CustomUser
from academics.models import Student, Class, Enrollment

# Get Sam user
sam_user = CustomUser.objects.filter(username='sam').first()
print(f"Sam user: {sam_user}")

if sam_user:
    # Check if Sam has a Student record
    student = Student.objects.filter(user=sam_user).first()
    print(f"Sam student record: {student}")
    
    if not student:
        # Create Student record for Sam
        import random
        student_id = f"STU{random.randint(1000, 9999)}"
        student = Student.objects.create(
            user=sam_user,
            student_id=student_id,
            enrollment_date='2025-01-01'
        )
        print(f"Created Student record: {student}")
    
    # Show available classes
    classes = Class.objects.all()
    print(f"\nAvailable classes ({classes.count()}):")
    for cls in classes:
        print(f"  - {cls.name} (ID: {cls.id}, Level: {cls.level})")
    
    # Check if Sam is enrolled in any class
    current_enrollment = Enrollment.objects.filter(student=student).first()
    print(f"\nCurrent enrollment: {current_enrollment}")
    
    if classes.exists():
        # Enroll Sam in the first available class
        first_class = classes.first()
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            enrolled_class=first_class,
            defaults={'academic_year': '2025-2026'}
        )
        print(f"\nEnrolled Sam in {first_class.name}: {created}")
        print(f"Enrollment: {enrollment}")
        
        # Update student's current_class
        student.current_class = first_class
        student.save()
        print(f"Updated student.current_class to {first_class.name}")
    
    print("\n=== Summary ===")
    print(f"Student: {student}")
    print(f"Student ID: {student.student_id}")
    print(f"Current Class: {student.current_class}")
    print(f"Enrollments: {Enrollment.objects.filter(student=student).count()}")
else:
    print("Sam user not found!")
