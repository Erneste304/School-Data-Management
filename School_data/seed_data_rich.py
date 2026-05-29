import os
import django
from datetime import date, time, datetime, timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'School_data.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from schools.models import SchoolLevel, AcademicYear, Term, Classroom
from accounts.models import CustomUser, StaffProfile, ParentProfile, ParentStudentRelationship
from academics.models import (
    Class, Student, Subject, Enrollment, Grade, Attendance,
    Exam, ExamResult, TeacherProfile, AcademicTerm, ClassSchedule
)
from finance.models import FeeCategory, FeeStructure, StudentFee, Payment, ExpenseCategory, Expense
from discipline.models import DisciplineCategory, DisciplineCase, DisciplineAction
from activities.models import Club, Event, Announcement
from alumni.models import AlumniProfile, AlumniEvent, AlumniJobPosting, AlumniDonation
from chat.models import ChatRoom, Message
from livestream.models import Stream, StreamSetting
from documents.models import DocumentCategory, Document
from notifications.models import Notification, NotificationPreference

User = get_user_model()

def seed_rich():
    print("🌱 Seeding rich database modules...")

    # ==========================================
    # 1. SEED SCHOOLS MODULE
    # ==========================================
    print("🏫 Seeding Schools app...")
    levels_to_create = [
        ('nursery', 'Nursery School Level'),
        ('primary', 'Primary School Level'),
        ('o_level', 'Ordinary Secondary Level (O-Level)'),
        ('a_level', 'Advanced Secondary Level (A-Level)'),
    ]
    school_levels = {}
    for code, desc in levels_to_create:
        lvl, _ = SchoolLevel.objects.get_or_create(
            name=code,
            defaults={'description': desc}
        )
        school_levels[code] = lvl
        print(f"   Level created/found: {code}")

    year_2026, _ = AcademicYear.objects.get_or_create(
        name="2026",
        defaults={
            'start_date': date(2026, 1, 1),
            'end_date': date(2026, 12, 31),
            'is_current': True
        }
    )

    terms = []
    term_dates = [
        (1, date(2026, 1, 5), date(2026, 4, 10)),
        (2, date(2026, 4, 27), date(2026, 7, 31)),
        (3, date(2026, 9, 7), date(2026, 11, 27))
    ]
    for num, start, end in term_dates:
        t, _ = Term.objects.get_or_create(
            academic_year=year_2026,
            number=num,
            defaults={'start_date': start, 'end_date': end}
        )
        terms.append(t)

    classrooms = []
    classroom_names = [
        ("Nursery 1", 'nursery'),
        ("Primary 1A", 'primary'),
        ("Primary 6B", 'primary'),
        ("Senior 1A", 'o_level'),
        ("Senior 3B", 'o_level'),
        ("Senior 4 MCE", 'a_level'),
        ("Senior 6 PCB", 'a_level')
    ]
    for name, lvl_code in classroom_names:
        cr, _ = Classroom.objects.get_or_create(
            name=name,
            academic_year=year_2026,
            defaults={
                'level': school_levels[lvl_code],
                'capacity': 40
            }
        )
        classrooms.append(cr)
    print("✅ Schools module seeded successfully!")

    # ==========================================
    # 2. SEED PARENT & MY CHILDREN
    # ==========================================
    print("👪 Seeding Parents & ParentStudentRelationships...")
    student1_user = User.objects.filter(username='student1').first()
    student2_user = User.objects.filter(username='student2').first()
    
    student1 = Student.objects.filter(user=student1_user).first()
    student2 = Student.objects.filter(user=student2_user).first()

    parent_user, created = User.objects.get_or_create(
        username='parent1',
        defaults={
            'email': 'parent1@rutabo.rw',
            'first_name': 'Jean',
            'last_name': 'Kabera',
            'role': 'parent',
            'phone': '+250788111222',
            'is_active': True
        }
    )
    if created:
        parent_user.set_password('parent123')
        parent_user.save()
        print("   Parent User 'parent1' created (password: parent123)")

    parent_profile, _ = ParentProfile.objects.get_or_create(
        user=parent_user,
        defaults={
            'occupation': 'Civil Servant',
            'workplace': 'Ministry of Infrastructure',
            'emergency_contact': '+250788333444',
            'relationship_to_student': 'Father'
        }
    )

    if student1:
        ParentStudentRelationship.objects.get_or_create(
            parent=parent_profile,
            student=student1,
            defaults={
                'is_primary_guardian': True,
                'can_view_grades': True,
                'can_view_attendance': True,
                'can_view_discipline': True,
                'can_view_fees': True,
                'relationship_type': 'Father'
            }
        )
    if student2:
        ParentStudentRelationship.objects.get_or_create(
            parent=parent_profile,
            student=student2,
            defaults={
                'is_primary_guardian': False,
                'can_view_grades': True,
                'can_view_attendance': True,
                'can_view_discipline': True,
                'can_view_fees': True,
                'relationship_type': 'Father'
            }
        )
    print("✅ Parent and student links seeded successfully!")

    # ==========================================
    # 3. SEED FINANCE & BILLING
    # ==========================================
    print("💰 Seeding Finance & Billing...")
    tuition, _ = FeeCategory.objects.get_or_create(
        code="TUI",
        defaults={
            'name': 'Tuition Fee',
            'description': 'Main academic tuition fee per term',
            'is_mandatory': True,
            'is_recurring': True
        }
    )
    uniform, _ = FeeCategory.objects.get_or_create(
        code="UNI",
        defaults={
            'name': 'School Uniform Fee',
            'description': 'Fee for school uniform package',
            'is_mandatory': True,
            'is_recurring': False
        }
    )
    activity_fee, _ = FeeCategory.objects.get_or_create(
        code="ACTF",
        defaults={
            'name': 'Extracurricular Activities Fee',
            'description': 'Sports, clubs, and cultural activities fee',
            'is_mandatory': False,
            'is_recurring': True
        }
    )

    # Fee Structures for Term 1 2026
    t1 = terms[0]
    fs_tui, _ = FeeStructure.objects.get_or_create(
        academic_year=year_2026,
        term=t1,
        category=tuition,
        level=school_levels['o_level'],
        defaults={
            'amount': 150000.00,
            'frequency': 'termly',
            'due_date': date(2026, 2, 1),
            'late_fee': 5000.00,
            'is_active': True
        }
    )
    fs_uni, _ = FeeStructure.objects.get_or_create(
        academic_year=year_2026,
        term=t1,
        category=uniform,
        level=school_levels['o_level'],
        defaults={
            'amount': 25000.00,
            'frequency': 'one_time',
            'due_date': date(2026, 1, 15),
            'late_fee': 0.00,
            'is_active': True
        }
    )

    # Student Fees and Payments for student1
    accountant_user = User.objects.filter(role='admin').first() # Fallback cashier
    
    if student1:
        sfee1, _ = StudentFee.objects.get_or_create(
            student=student1,
            fee_structure=fs_tui,
            defaults={
                'academic_year': year_2026,
                'term': t1,
                'total_amount': 150000.00,
                'amount_paid': 100000.00,
                'status': 'partial',
                'due_date': date(2026, 2, 1),
                'notes': 'Paid first installment.'
            }
        )
        if _:
            # Create a corresponding payment
            Payment.objects.create(
                student=student1,
                student_fee=sfee1,
                amount=100000.00,
                payment_date=date(2026, 1, 10),
                payment_method='mobile_money',
                reference_number='TXN7882233990',
                received_by=accountant_user,
                notes='Installment 1'
            )

        sfee2, _ = StudentFee.objects.get_or_create(
            student=student1,
            fee_structure=fs_uni,
            defaults={
                'academic_year': year_2026,
                'term': t1,
                'total_amount': 25000.00,
                'amount_paid': 25000.00,
                'status': 'paid',
                'due_date': date(2026, 1, 15),
                'notes': 'Uniform fee fully paid.'
            }
        )
        if _:
            Payment.objects.create(
                student=student1,
                student_fee=sfee2,
                amount=25000.00,
                payment_date=date(2026, 1, 12),
                payment_method='cash',
                reference_number='CHSH8229',
                received_by=accountant_user,
                notes='Fully paid uniform'
            )

    # Seeding some Expenses
    exp_cat, _ = ExpenseCategory.objects.get_or_create(
        code="UTIL",
        defaults={
            'name': 'Utilities & Power',
            'description': 'Water, electricity and internet bills',
            'budget': 500000.00
        }
    )
    Expense.objects.get_or_create(
        expense_number="EXP20260129",
        defaults={
            'category': exp_cat,
            'description': 'Payment of weekly electric and internet bills',
            'amount': 75000.00,
            'expense_date': date(2026, 1, 29),
            'paid_to': 'Rwanda Energy Group (REG)'
        }
    )
    print("✅ Finance module seeded successfully!")

    # ==========================================
    # 4. SEED DISCIPLINE MODULE
    # ==========================================
    print("⚖️ Seeding Discipline...")
    dis_cat1, _ = DisciplineCategory.objects.get_or_create(
        name="Late Arrival",
        defaults={
            'description': 'Arriving at morning assembly or class after the bell.',
            'severity': 'minor',
            'default_action': 'Verbal warning and campus cleaning.',
            'points': 2
        }
    )
    dis_cat2, _ = DisciplineCategory.objects.get_or_create(
        name="Dress Code Violation",
        defaults={
            'description': 'Improper wearing of school uniform, lack of tie, or wrong socks.',
            'severity': 'minor',
            'default_action': 'Rectify immediate dress code status or detention.',
            'points': 1
        }
    )
    dis_cat3, _ = DisciplineCategory.objects.get_or_create(
        name="Academic Dishonesty",
        defaults={
            'description': 'Cheating or copying homework, quizzes, or major exams.',
            'severity': 'major',
            'default_action': 'Automatic score of 0 and parent conference.',
            'points': 10
        }
    )

    dod_user = User.objects.filter(role='dod').first()
    if not dod_user:
        # Fallback to Admin if DOD role user doesn't exist
        dod_user = User.objects.filter(role='admin').first()

    teacher1 = User.objects.filter(role='teacher').first()

    if student1:
        case, created = DisciplineCase.objects.get_or_create(
            student=student1,
            category=dis_cat1,
            incident_location="School Main Gate",
            defaults={
                'reported_by': teacher1,
                'incident_date': timezone.now() - timedelta(days=2),
                'description': 'Arrived 20 minutes late to morning class without an excuse.',
                'status': 'resolved',
                'assigned_to': dod_user
            }
        )
        if created:
            DisciplineAction.objects.create(
                case=case,
                action_type='warning',
                description='Issued verbal warning and student cleaned schoolyard for 30 minutes.',
                taken_by=dod_user,
                is_completed=True
            )
            
        case2, created = DisciplineCase.objects.get_or_create(
            student=student1,
            category=dis_cat3,
            incident_location="Examination Hall A",
            defaults={
                'reported_by': teacher1,
                'incident_date': timezone.now() - timedelta(days=5),
                'description': 'Found with mathematics crib sheets hidden inside shirt sleeve.',
                'status': 'reported',
                'assigned_to': dod_user
            }
        )
    print("✅ Discipline module seeded successfully!")

    # ==========================================
    # 5. SEED ACTIVITIES (CLUBS, EVENTS, ANNOUNCEMENTS)
    # ==========================================
    print("⚽ Seeding Activities...")
    club1, _ = Club.objects.get_or_create(
        name="Debate & Public Speaking Club",
        defaults={
            'description': 'Enhancing public speaking, argumentation, and critical thinking skills.',
            'acronym': 'DEBATE',
            'category': 'academic',
            'established_date': date(2025, 1, 1),
            'is_active': True
        }
    )
    club2, _ = Club.objects.get_or_create(
        name="Science & Robotics Club",
        defaults={
            'description': 'Hands-on projects with microcontrollers, physics concepts, and basic chemistry experiments.',
            'acronym': 'SCIENCE',
            'category': 'technology',
            'established_date': date(2025, 1, 1),
            'is_active': True
        }
    )

    event1, _ = Event.objects.get_or_create(
        title="Annual Inter-House Sports Day",
        defaults={
            'description': 'A competitive day of track and field events, football, and volleyball.',
            'event_type': 'sports',
            'venue': 'School Sports Complex',
            'start_date': timezone.now() + timedelta(days=10),
            'end_date': timezone.now() + timedelta(days=10, hours=8),
            'audience': 'public'
        }
    )
    event2, _ = Event.objects.get_or_create(
        title="Rutabo SMS Science Fair 2026",
        defaults={
            'description': 'Students demonstrate innovative engineering projects and science prototypes.',
            'event_type': 'academic',
            'venue': 'School Assembly Hall',
            'start_date': timezone.now() + timedelta(days=20),
            'end_date': timezone.now() + timedelta(days=20, hours=6),
            'audience': 'public'
        }
    )

    Announcement.objects.get_or_create(
        title="Term 1 Mid-Term Break Notice",
        defaults={
            'content': 'Please note that the mid-term break will commence on Friday, March 12th. Classes will resume on Monday, March 22nd.',
            'expiry_date': timezone.now() + timedelta(days=20),
            'priority': 'medium',
            'audience': 'public',
            'is_published': True
        }
    )
    print("✅ Activities module seeded successfully!")

    # ==========================================
    # 6. SEED ALUMNI
    # ==========================================
    print("🎓 Seeding Alumni...")
    alumni_user1, created = User.objects.get_or_create(
        username='alumni1',
        defaults={
            'email': 'alumni1@rutabo.rw',
            'first_name': 'David',
            'last_name': 'Mugisha',
            'role': 'public',
            'phone': '+250788555666',
            'is_active': True
        }
    )
    if created:
        alumni_user1.set_password('alumni123')
        alumni_user1.save()

    al_prof1, _ = AlumniProfile.objects.get_or_create(
        user=alumni_user1,
        defaults={
            'graduation_year': 2024,
            'graduation_class': 'Senior 6 MPC (Math, Physics, Computer)',
            'current_occupation': 'Junior Software Engineer',
            'current_employer': 'BK Tech House',
            'current_location': 'Kigali, Rwanda',
            'is_willing_to_mentor': True,
            'is_willing_to_speak': True,
            'is_willing_to_donate': True,
            'bio': 'Passionate builder, open source enthusiast.'
        }
    )

    alevent, _ = AlumniEvent.objects.get_or_create(
        title="Annual Alumni Home-coming Reunion",
        defaults={
            'description': 'Network with fellow graduates, enjoy dinner, and support current student scholarships.',
            'event_date': timezone.now() + timedelta(days=30),
            'location': 'Kigali Marriott Hotel',
            'event_type': 'Reunion',
            'max_attendees': 100,
            'registration_deadline': timezone.now() + timedelta(days=25)
        }
    )

    AlumniJobPosting.objects.get_or_create(
        posted_by=al_prof1,
        title="Software Engineering Intern",
        defaults={
            'company': 'BK Tech House',
            'location': 'Kigali / Remote',
            'job_type': 'Internship',
            'description': 'Excellent opportunity for recent graduates or S6 students with strong programming foundations to work on digital banking products.',
            'requirements': 'Knowledge of Python/Django or React is highly preferred.',
            'application_link': 'https://careers.bk.rw/jobs/software-engineering-intern',
            'is_active': True
        }
    )

    AlumniDonation.objects.get_or_create(
        alumni=al_prof1,
        amount=120000.00,
        defaults={
            'donation_purpose': 'Science Laboratory Equipment Fund',
            'is_anonymous': False,
            'message': 'Always happy to support future scientists at Rutabo School.',
            'payment_method': 'mobile_money',
            'receipt_sent': True
        }
    )
    print("✅ Alumni module seeded successfully!")

    # ==========================================
    # 7. SEED CHAT MODULE
    # ==========================================
    print("💬 Seeding Chat Rooms...")
    c_admin = User.objects.filter(role='admin').first()
    
    room1, _ = ChatRoom.objects.get_or_create(
        slug="general-staff-room",
        defaults={
            'name': "General Staff Lounge",
            'room_type': 'staff',
            'description': 'Daily coordination, announcements, and informal discussions for teachers and administrators.',
            'created_by': c_admin
        }
    )
    
    room2, _ = ChatRoom.objects.get_or_create(
        slug="science-club-channel",
        defaults={
            'name': "Science Club Discussion",
            'room_type': 'public',
            'description': 'For questions and discussions regarding science experiments, robotics projects, and announcements.',
            'created_by': c_admin
        }
    )

    # Seeding some messages
    teacher1_user = User.objects.filter(role='teacher').first()
    admin_user = User.objects.filter(role='admin').first()

    if teacher1_user and admin_user:
        room1.members.add(teacher1_user, admin_user)
        Message.objects.get_or_create(
            room=room1,
            sender=admin_user,
            content="Welcome everyone to our new Rutabo SMS general chatroom! Let's use this for announcements.",
            defaults={'message_type': 'text'}
        )
        Message.objects.get_or_create(
            room=room1,
            sender=teacher1_user,
            content="Wonderful! This makes scheduling physics labs and matching tutors much simpler.",
            defaults={'message_type': 'text'}
        )
    print("✅ Chat module seeded successfully!")

    # ==========================================
    # 8. SEED LIVESTREAM MODULE
    # ==========================================
    print("🎥 Seeding Livestream...")
    s_teacher = User.objects.filter(role='teacher').first()
    
    str1, _ = Stream.objects.get_or_create(
        title="Grade 10 Physics Midterm Overview",
        defaults={
            'description': 'Live review of exam questions, kinematics formulas, and key derivations.',
            'status': 'scheduled',
            'stream_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # Placeholder
            'scheduled_start': timezone.now() + timedelta(days=2),
            'created_by': s_teacher,
            'is_public': True
        }
    )
    if _:
        StreamSetting.objects.get_or_create(
            stream=str1,
            defaults={
                'enable_chat': True,
                'enable_qa': True,
                'record_stream': True,
                'resolution': '1080p'
            }
        )

    str2, _ = Stream.objects.get_or_create(
        title="Morning Assembly and Term 1 Address",
        defaults={
            'description': 'Watch head teacher Mugabo address parents and students on term planning.',
            'status': 'live',
            'stream_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'scheduled_start': timezone.now() - timedelta(minutes=30),
            'actual_start': timezone.now() - timedelta(minutes=30),
            'created_by': admin_user,
            'is_public': True,
            'view_count': 42
        }
    )
    if _:
        StreamSetting.objects.get_or_create(
            stream=str2,
            defaults={
                'enable_chat': True,
                'enable_qa': False,
                'record_stream': True,
                'resolution': '720p'
            }
        )
    print("✅ Livestream module seeded successfully!")

    # ==========================================
    # 9. SEED DOCUMENTS MODULE
    # ==========================================
    print("📁 Seeding Documents...")
    doc_cat1, _ = DocumentCategory.objects.get_or_create(
        name="Academic Syllabus",
        defaults={'description': 'Curriculum guidelines and learning timetables.'}
    )
    doc_cat2, _ = DocumentCategory.objects.get_or_create(
        name="School Regulations",
        defaults={'description': 'Student handbooks, code of conduct, and disciplinary policies.'}
    )

    # Creating database document entries
    # The actual file field can use a dummy file
    Document.objects.get_or_create(
        title="Ordinary Level Physics Curriculum Guide 2026",
        defaults={
            'description': 'Official REB physics curriculum outlines and resources.',
            'category': doc_cat1,
            'file': 'documents/physics_guide_2026.pdf',
            'uploaded_by': admin_user,
            'file_size': 1420500,
            'file_type': 'pdf',
            'is_public': True,
            'tags': 'Physics, O-Level, REB'
        }
    )
    Document.objects.get_or_create(
        title="Rutabo School Code of Conduct & Disciplinary Policies",
        defaults={
            'description': 'Student code of conduct handbook detailing disciplinary procedures.',
            'category': doc_cat2,
            'file': 'documents/conduct_handbook.pdf',
            'uploaded_by': admin_user,
            'file_size': 512000,
            'file_type': 'pdf',
            'is_public': True,
            'tags': 'Regulations, Discipline, Policy'
        }
    )
    print("✅ Documents module seeded successfully!")

    # ==========================================
    # 10. SEED NOTIFICATIONS & PREFERENCES
    # ==========================================
    print("🔔 Seeding Notifications...")
    all_users = User.objects.all()
    for u in all_users:
        NotificationPreference.objects.get_or_create(
            user=u,
            defaults={
                'email_enabled': True,
                'sms_enabled': False,
                'in_app_enabled': True,
                'academic_notifications': True,
                'financial_notifications': True,
                'discipline_notifications': True,
                'event_notifications': True
            }
        )

    # Create dummy in-app notifications
    if student1_user:
        Notification.objects.create(
            recipient=student1_user,
            title="Tuition Due Notice",
            message="Your Term 1 2026 tuition balance is due soon. Please clear outstanding balance of 50,000 RWF.",
            notification_type='Financial',
            is_read=False
        )
        Notification.objects.create(
            recipient=student1_user,
            title="Discipline Warning Issued",
            message="A discipline warning has been registered on your portal regarding Late Arrival.",
            notification_type='Discipline',
            is_read=True
        )

    if teacher1_user:
        Notification.objects.create(
            recipient=teacher1_user,
            title="New Stream Scheduled",
            message="Your virtual classroom physics overview stream is scheduled for this coming Friday.",
            notification_type='System',
            is_read=False
        )

    print("✅ Notifications module seeded successfully!")
    print("✨ Rich Seeding Completed! All 9 missing database modules are fully seeded.")

if __name__ == '__main__':
    seed_rich()
